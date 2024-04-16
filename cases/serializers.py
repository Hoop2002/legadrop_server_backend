from django.utils import timezone
from rest_framework import serializers
from rest_framework import status
from cases.models import Case, Item, RarityCategory, Category, ConditionCase, Contests
from users.models import UserItems, UserProfile, ContestsWinners
from payments.models import Calc

from utils.fields import Base64ImageField


class ConditionSerializer(serializers.ModelSerializer):
    type_condition = serializers.ChoiceField(
        choices=ConditionCase.CONDITION_TYPES_CHOICES
    )
    time = serializers.TimeField(
        required=False,
        allow_null=True,
        default="",
    )
    time_reboot = serializers.TimeField(
        required=False,
        default="24:00:00",
    )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = ConditionCase
        fields = (
            "condition_id",
            "name",
            "description",
            "type_condition",
            "price",
            "time",
            "time_reboot",
            "group_id_vk",
            "group_id_tg",
        )
        read_only_fields = ("condition_id",)


class RarityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RarityCategory
        fields = ("rarity_id", "name", "rarity_color")
        read_only_fields = ("name", "rarity_id", "rarity_color")


class RarityCategoryAdminSerializer(RarityCategorySerializer):
    class Meta:
        model = RarityCategory
        fields = RarityCategorySerializer.Meta.fields


class ItemListSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(max_length=9)
    image = serializers.ImageField(use_url=True, read_only=True)
    rarity_category = RarityCategorySerializer(read_only=True)

    class Meta:
        model = Item
        fields = (
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
        )
        read_only_fields = (
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
        )


class AdminItemListSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(max_length=9)
    image = serializers.CharField()
    rarity_category = RarityCategorySerializer(read_only=True)
    purchase_price = serializers.FloatField(source="purchase_price_cached")
    percent = serializers.SerializerMethodField()

    @staticmethod
    def get_percent(instance):
        if isinstance(instance, dict) and "percent" in instance.keys():
            return instance["percent"]
        return 0

    class Meta:
        model = Item
        fields = (
            "item_id",
            "name",
            "price",
            "purchase_price",
            "image",
            "rarity_category",
            "type",
            "created_at",
            "percent",
        )
        read_only_fields = (
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
            "type",
            "created_at",
        )


class UserItemSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        super(UserItemSerializer, self).validate(attrs)
        if attrs["item"]:
            price = attrs["item"].price
            balance = attrs["user"].profile.balance
            if price > balance:
                raise serializers.ValidationError(
                    detail="Недостаточно средств", code=status.HTTP_406_NOT_ACCEPTABLE
                )
        return attrs

    def create(self, validated_data):
        user_item = super().create(validated_data)
        Calc.objects.create(
            user_id=user_item.user_id,
            balance=-user_item.item.price,
        )
        return user_item

    class Meta:
        model = UserItems
        fields = ("user", "item", "id")
        read_only_fields = ("id",)


class ItemsAdminSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(required=True)
    purchase_price = serializers.FloatField(read_only=True)
    image = Base64ImageField(
        required=False, max_length=None, use_url=True, allow_null=True
    )
    rarity_category = RarityCategorySerializer(read_only=True)
    rarity_category_id = serializers.CharField(max_length=9, write_only=True)
    step_down_factor = serializers.FloatField(default=1, required=False)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = Item
        fields = (
            "id",
            "item_id",
            "name",
            "price",
            "crystals_quantity",
            "type",
            "service",
            "is_output",
            "purchase_price",
            "sale_price",
            "percent_price",
            "sale",
            "image",
            "created_at",
            "updated_at",
            "step_down_factor",
            "rarity_category",
            "rarity_category_id",
        )
        read_only_fields = ("id", "created_at", "updated_at", "rarity_category")
        write_only_fields = ("rarity_category_id",)


class CaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("category_id", "name")
        read_only_fields = ("name",)


class ListCasesSerializer(serializers.ModelSerializer):
    category = CaseCategorySerializer()

    class Meta:
        model = Case
        fields = ("translit_name", "name", "price", "case_free", "image", "category")


class ListCaseItemsSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(max_length=9)
    image = serializers.CharField()
    rarity_category = RarityCategorySerializer(read_only=True)
    percent = serializers.FloatField()

    class Meta:
        model = Item
        fields = (
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
            "percent",
        )
        read_only_fields = (
            "item_id",
            "name",
            "price",
            "image",
            "rarity_category",
            "percent",
        )


class CaseSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    category = CaseCategorySerializer()

    @staticmethod
    def get_items(instance) -> ListCaseItemsSerializer:
        items = instance.get_items()
        return ListCaseItemsSerializer(items, many=True).data

    class Meta:
        model = Case
        fields = (
            "translit_name",
            "name",
            "price",
            "case_free",
            "image",
            "category",
            "items",
        )


class ListConditionSerializer(serializers.ModelSerializer):
    condition_id = serializers.CharField(max_length=9)

    class Meta:
        model = ConditionCase
        fields = ("condition_id", "name", "type_condition")
        read_only_fields = ("name", "type_condition")


class AdminCreateCaseSerializer(ListCasesSerializer):
    name = serializers.CharField(max_length=256)
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    active = serializers.BooleanField(default=False)
    category_id = serializers.CharField(max_length=9, write_only=True)
    item_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True
    )
    condition_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True, required=False
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "name" in attrs:
            if self.instance:
                case_exists = (
                    Case.objects.filter(name=attrs["name"])
                    .exclude(id=self.instance.id)
                    .exists()
                )
            else:
                case_exists = Case.objects.filter(name=attrs["name"]).exists()
            if case_exists:
                raise serializers.ValidationError(
                    {"name": "Кейс с таким именем уже существует!"}
                )
        return attrs

    def create(self, validated_data):
        if "condition_ids" in validated_data:
            condition_ids = validated_data.pop("condition_ids")
            conditions = ConditionCase.objects.filter(condition_id__in=condition_ids)
            validated_data["conditions"] = conditions

        # item обязательные, поэтому не ставим проверку
        item_ids = validated_data.pop("item_ids")
        items = Item.objects.filter(item_id__in=item_ids)
        if items.count() < 1:
            raise serializers.ValidationError(
                {"item_ids": "Ни одного предмета не выбрано!"}
            )
        validated_data["items"] = items

        return super().create(validated_data)

    class Meta:
        model = Case
        fields = (
            "name",
            "active",
            "image",
            "recommendation_price",
            "category_id",
            "item_ids",
            "condition_ids",
        )
        read_only_fields = ("recommendation_price",)


class TestOpenCaseSerializer(serializers.Serializer):
    items_prices = serializers.ListField(child=serializers.FloatField())
    count_open = serializers.IntegerField()
    percent = serializers.FloatField()


class AdminCasesSerializer(AdminCreateCaseSerializer):
    name = serializers.CharField(max_length=256)
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    category = CaseCategorySerializer(read_only=True)
    category_id = serializers.CharField(max_length=9, write_only=True)
    items = serializers.SerializerMethodField()
    conditions = ListConditionSerializer(many=True, read_only=True)
    item_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True
    )
    condition_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True, required=False
    )

    @staticmethod
    def get_items(instance) -> AdminItemListSerializer:
        items = instance.get_admin_items()
        return AdminItemListSerializer(items, many=True).data

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    def update(self, instance, validated_data):
        if "condition_ids" in validated_data:
            condition_ids = validated_data.pop("condition_ids")
            conditions = ConditionCase.objects.filter(condition_id__in=condition_ids)
            validated_data["conditions"] = conditions

        if "item_ids" in validated_data:
            item_ids = validated_data.pop("item_ids")
            items = Item.objects.filter(item_id__in=item_ids)
            validated_data["items"] = items
        return super().update(instance, validated_data)

    class Meta:
        model = Case
        fields = (
            "case_id",
            "name",
            "translit_name",
            "active",
            "image",
            "price",
            "recommendation_price",
            "case_free",
            "category",
            "category_id",
            "items",
            "item_ids",
            "conditions",
            "condition_ids",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("recommendation_price",)


class LastWinnerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    photo = Base64ImageField(source="user.profile.image", use_url=True, max_length=None)
    date = serializers.DateTimeField(source="created_at", format="%d.%m.%Y в %H:%M")
    item = ItemListSerializer()

    class Meta:
        model = ContestsWinners
        fields = ("username", "photo", "item", "date")


class ContestsSerializer(serializers.ModelSerializer):
    next_start = serializers.SerializerMethodField()
    current_award = ItemListSerializer()
    count_participants = serializers.SerializerMethodField()
    last_winners = serializers.SerializerMethodField()
    conditions = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()

    @staticmethod
    def get_next_start(instance) -> timezone.datetime:
        if instance.next_start:
            return instance.next_start
        if not instance.next_start:
            instance.set_next_start()
            return instance.next_start

    @staticmethod
    def get_count_participants(instance) -> int:
        return instance.participants.count()

    @staticmethod
    def get_last_winners(instance) -> LastWinnerSerializer(many=True):
        winners = instance.winners.order_by("-pk")[:5]
        if not winners:
            return []
        serializer = LastWinnerSerializer(winners, many=True)
        return serializer.data

    @staticmethod
    def get_conditions(instance) -> list[str]:
        return instance.conditions.values_list("name", flat=True)

    def get_participant(self, instance) -> bool:
        user = self.context["request"].user
        if user.is_authenticated:
            return user in instance.participants.all()
        return False

    class Meta:
        model = Contests
        fields = (
            "contest_id",
            "name",
            "next_start",
            "current_award",
            "count_participants",
            "last_winners",
            "conditions",
            "one_time",
            "active",
            "participant",
        )


class EasyUserListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = UserProfile
        fields = ("user_id", "username")


class AdminContestsSerializer(serializers.ModelSerializer):
    current_award = ItemListSerializer(read_only=True)
    current_award_id = serializers.CharField(write_only=True, required=False)
    timer = serializers.DurationField(help_text="Формат: дни часы:минуты:секунды")
    items = ItemListSerializer(many=True, read_only=True)
    item_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True
    )
    conditions = ListConditionSerializer(many=True, read_only=True)
    condition_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True, required=False
    )
    one_time = serializers.BooleanField(default=False)
    participants = EasyUserListSerializer(many=True, read_only=True)
    participant_ids = serializers.ListSerializer(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    def validate(self, attrs):
        super().validate(attrs)
        if "next_start" in attrs:
            now = timezone.now()
            if now > attrs["next_start"]:
                raise serializers.ValidationError(
                    {"next_start": "Время начала не может быть больше, чем текущее!"}
                )

        if "item_ids" in attrs:
            for item in attrs["item_ids"]:
                if not Item.objects.filter(item_id=item).exists():
                    raise serializers.ValidationError(
                        {"item_ids": f"Предмета с id {item} не существует"}
                    )
            attrs["items"] = Item.objects.filter(item_id__in=attrs["item_ids"])
            attrs.pop("item_ids")

        if "current_award_id" in attrs:
            if not Item.objects.filter(item_id=attrs["current_award_id"]).exists():
                raise serializers.ValidationError(
                    {"current_award": f"Такого приза не существует!"}
                )
            attrs["current_award"] = Item.objects.filter(
                item_id=attrs["current_award_id"]
            ).last()
            attrs.pop("current_award_id")

        if "condition_ids" in attrs:
            for condition in attrs["condition_ids"]:
                if not ConditionCase.objects.filter(condition_id=condition).exists():
                    raise serializers.ValidationError(
                        {"condition_ids": f"Условия с id {condition} не существует"}
                    )
            attrs["conditions"] = ConditionCase.objects.filter(
                condition_id__in=attrs["condition_ids"]
            )
            attrs.pop("condition_ids")

        if "participants" in attrs:
            for participant in attrs["participants"]:
                if not UserProfile.objects.filter(user_id=participant).exists():
                    raise serializers.ValidationError(
                        {
                            "participants": f"Пользователя с id {participant} не существует"
                        }
                    )
            attrs["participants"] = UserProfile.objects.filter(
                user_id__in=attrs["participants"]
            )

        return attrs

    def create(self, validated_data):
        if "current_award" in validated_data and "items" in validated_data:
            if validated_data["current_award"] not in validated_data["items"]:
                raise serializers.ValidationError(
                    {"current_award": "Приз должен быть в списке допустимых предметов!"}
                )
        instance = super().create(validated_data)
        if not instance.current_award:
            instance.set_new_award()
        if not instance.next_start:
            instance.next_start = instance.created_at + instance.timer
        return instance

    def update(self, instance, validated_data):
        if "timer" in validated_data:
            diff = validated_data["timer"] - instance.timer
            if (
                diff.total_seconds() != 0
                and instance.next_start is not None
                and not validated_data.get("next_start")
            ):
                validated_data["next_start"] = instance.next_start + diff

        if "current_award" in validated_data:
            if "items" in validated_data:
                all_items = validated_data["items"] | instance.items.all()
                all_items = all_items.distinct()
                if validated_data["current_award"] not in all_items:
                    raise serializers.ValidationError(
                        {
                            "current_award": "Приз должен быть в списке допустимых предметов!"
                        }
                    )

            if validated_data["current_award"] not in instance.items.all():
                raise serializers.ValidationError(
                    {"current_award": "Приз должен быть в списке допустимых предметов!"}
                )
        return super().update(instance, validated_data)

    class Meta:
        model = Contests
        fields = (
            "contest_id",
            "name",
            "timer",
            "next_start",
            "active",
            "one_time",
            "items",
            "item_ids",
            "current_award",
            "current_award_id",
            "participants",
            "participant_ids",
            "conditions",
            "condition_ids",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "contest_id",
            "created_at",
            "updated_at",
        )


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("category_id", "name")
        read_only_fields = ("category_id",)


class AdminListCasesSerializer(serializers.ModelSerializer):
    category = CaseCategorySerializer()
    conditions = ListConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = (
            "case_id",
            "translit_name",
            "name",
            "price",
            "case_free",
            "image",
            "category",
            "conditions",
            "created_at",
            "updated_at",
        )
