import typing
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from core.models import GenericSettings
from users.models import UserProfile, UserItems, UserVerify
from social_django.models import UserSocialAuth
from payments.models import PaymentOrder, Calc, RefLinks
from cases.models import Item

from cases.serializers import RarityCategorySerializer
from utils.fields import Base64ImageField


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate(self, attrs):
        super().validate(attrs)
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")
        if password1 != password2:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        _auth_user = None
        if self.context["request"]:
            _auth_user = self.context["request"].user
        _user = (
            User.objects.filter(username=attrs["username"])
            .exclude(id=_auth_user.id if _auth_user else None)
            .exists()
        )

        if _user:
            raise serializers.ValidationError(
                {"username": "Пользователь с таким логином уже зарегистрирован"}
            )
        return attrs

    class Meta:
        model = User
        fields = ("id", "username", "password1", "password2", "email")


class UserSerializer(UserCreateSerializer):
    username = serializers.CharField(required=False)
    password1 = serializers.CharField(required=False, write_only=True)
    password2 = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False)


class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class UserProfileCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    token = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_token(instance) -> str:
        return str(AccessToken.for_user(instance.user))

    def create(self, validated_data):
        validated_data["user"].pop("password1")
        password = validated_data["user"].pop("password2")
        validated_data["user"]["password"] = password
        user = User.objects.create(**validated_data["user"])
        user.set_password(password)
        user.save()
        validated_data["user"] = user
        profile = UserProfile.objects.create(**validated_data)
        RefLinks.objects.create(from_user=profile)
        return profile

    class Meta:
        model = UserProfile
        fields = ("user", "token", "locale")


class UserSignInSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "password")


class UserReferralSerializer(serializers.ModelSerializer):
    ref_link = serializers.SerializerMethodField()
    code_data = serializers.CharField(
        required=False,
        write_only=True,
        help_text="всё, что будет сюда вписано, будет подставлено после базового урл",
    )

    def get_ref_link(self, instance) -> str:
        ref = instance.ref_links.first()
        if not ref:
            ref = RefLinks.objects.create(from_user=instance)
        generic = GenericSettings.load()
        domain = generic.domain_url
        return f"https://{domain}/ref/{ref.code_data}"

    def validate(self, attrs):
        code_data = attrs.get("code_data")
        if code_data is not None:
            if RefLinks.objects.filter(code_data=code_data).exists():
                raise serializers.ValidationError(
                    {"code_data": "Такой код уже существует!"}
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if "code_data" in validated_data:
            code_data = validated_data.pop("code_data")
            RefLinks.objects.create(from_user=instance, code_data=code_data)
            instance.save()
        return instance

    class Meta:
        model = UserProfile
        fields = (
            "ref_link",
            "total_income",
            "total_withdrawal",
            "available_withdrawal",
            "code_data",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    user = OtherUserSerializer(required=False)
    image = Base64ImageField(required=False, max_length=None, use_url=True)

    def update(self, instance, validated_data):
        user_data = {}
        if "user" in validated_data:
            user_data = validated_data.pop("user")
        if "password1" in user_data:
            password = user_data.pop("password1")
            user_data.pop("password2")
            instance.user.set_password(password)

        if "code_data" in validated_data:
            code_data = validated_data.pop("code_data")
            RefLinks.objects.create(from_user=instance, code_data=code_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        for key, value in user_data.items():
            setattr(instance.user, key, value)

        instance.user.save()
        instance.save()

        return instance

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "player_id",
            "image",
            "balance",
            "locale",
            "verified",
        )
        read_only_fields = ("verified", "balance")


class UserItemSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(source="item.item_id")
    name = serializers.CharField(source="item.name")
    price = serializers.SerializerMethodField()
    image = Base64ImageField(source="item.image", use_url=True, max_length=None)
    rarity_category = RarityCategorySerializer(source="item.rarity_category")

    @staticmethod
    def get_price(instance) -> float:
        if instance.item.sale_price != 0:
            sale_price = instance.item.sale_price
        elif instance.item.percent_price != 0:
            sale_price = instance.item.price * instance.item.percent_price
        else:
            sale_price = instance.item.purchase_price
        return sale_price

    class Meta:
        model = UserItems
        fields = (
            "id",
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
            "withdrawal_process",
        )


class AdminUserItemSerializer(UserItemSerializer):
    price = serializers.FloatField(source="item.price")


class HistoryItemSerializer(UserItemSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField()
    action_date = serializers.SerializerMethodField()

    @staticmethod
    def get_action_date(instance) -> serializers.DateTimeField(format="%d.%m.%y %H:%M"):
        if instance.calc:
            return instance.calc.created_at.strftime("%d.%m.%y %H:%M")
        if instance.output:
            return instance.output.created_at.strftime("%d.%m.%y %H:%M")
        if not instance.active:
            return instance.updated_at.strftime("%d.%m.%y %H:%M")
        return None

    @staticmethod
    def get_price(instance) -> float:
        if instance.calc:
            return instance.calc.balance
        return 0

    @staticmethod
    def get_status(instance) -> str:
        if not instance.active and not instance.withdrawn:
            return "Продан"
        elif instance.withdrawn:
            return "Выведен"
        else:
            return "На аккаунте"

    class Meta:
        model = UserItems
        fields = (
            "id",
            "item_id",
            "name",
            "price",
            "image",
            "status",
            "rarity_category",
            "action_date",
        )


class MinimalValuesSerializer(serializers.Serializer):
    upgraded_items = serializers.ListSerializer(
        child=serializers.CharField(), help_text="Желаемые предметы", write_only=True
    )
    min_bet = serializers.FloatField(read_only=True)
    max_bet = serializers.FloatField(read_only=True)
    min_ratio = serializers.FloatField(read_only=True)
    max_ratio = serializers.FloatField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        upgraded = Item.objects.filter(
            item_id__in=attrs["upgraded_items"], upgrade=True
        )
        if len(attrs["upgraded_items"]) > upgraded.count():
            raise serializers.ValidationError(
                {"upgraded_items": "Не все выбранные предметы доступны для апгрейда"}
            )
        attrs["upgraded_items"] = upgraded
        return attrs


class UpgradeItemSerializer(MinimalValuesSerializer, serializers.ModelSerializer):
    upgrade_items = serializers.ListSerializer(
        child=serializers.IntegerField(),
        help_text="Предметы для обновления",
        required=False,
        write_only=True,
    )
    balance = serializers.FloatField(write_only=True, required=False)
    upgrade_percent = serializers.SerializerMethodField(read_only=True)
    upgrade_ratio = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_upgrade_percent(instance) -> float:
        return 0

    @staticmethod
    def get_upgrade_ratio(instance) -> float:
        return 0

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        generic = GenericSettings.load()

        if "upgrade_items" not in attrs and "balance" not in attrs:
            raise serializers.ValidationError(
                {"balance": "Должна быть какая-то ставка"}
            )
        if "upgrade_items" in attrs and "balance" in attrs:
            raise serializers.ValidationError(
                {"balance": "Нужно выбрать один тип апгрейда"}
            )
        user = self.context.get("request").user
        if "upgrade_items" in attrs:
            user_items = user.items.filter(id__in=attrs["upgrade_items"], active=True)
            if len(attrs["upgrade_items"]) > user_items.count():
                raise serializers.ValidationError(
                    {
                        "upgrade_items": "Выберите только те пердметы, которые вам принадлежат"
                    }
                )
            sum_items = user_items.aggregate(sum=Sum("item__price"))["sum"]
            if generic.minimal_price_upgrade > sum_items:
                raise serializers.ValidationError(
                    {"upgrade_items": "Ставка меньше минимальной"}
                )

            attrs["upgrade_items"] = user_items
        if "balance" in attrs:
            if attrs["balance"] < 0:
                raise serializers.ValidationError(
                    {"balance": "Указано не верное количество денег"}
                )
            if user.profile.balance < attrs["balance"]:
                raise serializers.ValidationError(
                    {"balance": "Указано не верное количество денег"}
                )
            if generic.minimal_price_upgrade > attrs["balance"]:
                raise serializers.ValidationError(
                    {"balance": "Ставка меньше минимальной"}
                )

        return attrs

    class Meta:
        model = UserItems
        fields = (
            "upgrade_items",
            "upgraded_items",
            "balance",
            "upgrade_percent",
            "upgrade_ratio",
        )


class GetGenshinAccountSerializer(serializers.Serializer):
    uid = serializers.CharField()


class GameHistorySerializer(serializers.ModelSerializer):

    item = serializers.SerializerMethodField()
    case = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    @staticmethod
    def get_item(
        instance,
    ) -> typing.TypedDict(
        "item",
        {
            "item_id": str,
            "name": str,
            "price": float,
            "type": str,
            "purchase_price": float,
        },
    ):
        item_ = instance.item
        return {
            "item_id": item_.item_id,
            "name": item_.name,
            "price": item_.price,
            "type": item_.type,
            "purchase_price": item_.purchase_price_cached,
        }

    @staticmethod
    def get_case(
        instance,
    ) -> typing.TypedDict(
        "item",
        {
            "case_id": str,
            "name": str,
            "translit_name": float,
            "price": str,
        },
    ):
        case_ = instance.case
        return {
            "case_id": case_.case_id,
            "name": case_.name,
            "translit_name": case_.translit_name,
            "price": case_.price,
        }

    @staticmethod
    def get_status(instance) -> str:
        if not instance.active and not instance.withdrawn:
            return "Продан"
        elif instance.withdrawn:
            return "Выведен"
        else:
            return "На аккаунте"

    class Meta:
        model = UserItems
        fields = ("id", "item", "case", "status")


class AdminUserListSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None, required=False)
    all_debit = serializers.FloatField(source="debit_save")
    all_output = serializers.FloatField(source="output_save")
    username = serializers.CharField(source="user.username")
    link_vk = serializers.SerializerMethodField()
    link_tg = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active")
    balance = serializers.FloatField(source="balance_save")
    winrate = serializers.FloatField(source="winrate_save")
    player_id = serializers.CharField(source="user.player_id")
    @staticmethod
    def get_link_vk(instance):
        auth_vk = UserSocialAuth.objects.filter(
            user=instance.user, provider="vk-oauth2"
        ).first()
        if not auth_vk:
            return ""
        return f"https://vk.com/id{auth_vk.extra_data['id']}"

    @staticmethod
    def get_link_tg(instance):
        tg_username = instance.telegram_username

        if not tg_username:
            return ""

        return f"https://t.me/{tg_username}/"

    class Meta:
        model = UserProfile
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "link_vk",
            "link_tg",
            "image",
            "player_id",
            "username",
            "partner_percent",
            "partner_income",
            "total_income",
            "total_withdrawal",
            "available_withdrawal",
            "balance",
            "winrate",
            "all_debit",
            "all_output",
            "telegram_id",
            "date_joined",
            "is_active",
        )
        read_only_fields = ("date_joined",)


class AdminUserSerializer(AdminUserListSerializer):
    balance = serializers.FloatField(required=False)
    all_debit = serializers.FloatField(read_only=True)
    all_output = serializers.FloatField(read_only=True)
    winrate = serializers.FloatField(read_only=True)
    partner_percent = serializers.FloatField(min_value=1, max_value=2)
    partner_income = serializers.FloatField(min_value=0, max_value=1)
    individual_percent = serializers.FloatField(min_value=-1)

    def validate(self, attrs):
        if "balance" in attrs:
            if not self.instance.demo:
                raise serializers.ValidationError(
                    {"balance": "Нельзя менять баланс у обычного пользователя"}
                )
        return attrs

    def update(self, instance, validated_data):
        if "user" in validated_data:
            user = validated_data.pop("user")
            if "username" in user:
                instance.user.username = user.pop("username")
            if "first_name" in user:
                instance.user.first_name = user.pop("first_name")
            if "last_name" in user:
                instance.user.last_name = user.pop("last_name")
            if "email" in user:
                instance.user.email = user.pop("email")
            if "is_active" in user:
                instance.user.is_active = user.pop("is_active")
            instance.user.save()

        if "balance" in validated_data:
            balance = validated_data.pop("balance")
            user_balance = instance.balance
            difference = user_balance - balance
            Calc.objects.create(
                user=instance.user,
                balance=difference * -1,
                demo=True,
                comment=f"Начисление пользователю денег оператором {self.context['request'].user.username}",
            )
        return super(AdminUserSerializer, self).update(instance, validated_data)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = UserProfile
        fields = AdminUserListSerializer.Meta.fields + (
            "individual_percent",
            "demo",
            "verified",
        )
        read_only_fields = (
            "all_debit",
            "all_output",
            "date_joined",
            "link_vk",
            "link_tg",
            "player_id",
            "total_income",
            "total_withdrawal",
            "available_withdrawal",
            "winrate",
            "all_debit",
            "all_output",
        )


class AdminUserPaymentHistorySerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = PaymentOrder
        fields = (
            "id",
            "order_id",
            "location",
            "active",
            "type_payments",
            "sum",
            "manually_approved",
            "status",
            "created_at",
            "updated_at",
        )


class SuccessSignUpSerializer(serializers.Serializer):
    next = serializers.CharField()
    token = serializers.CharField()


class AdminUserVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerify
        fields = "__all__"


class UserVerifycationSerializer(serializers.Serializer):
    email = serializers.EmailField()
