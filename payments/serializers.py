from rest_framework import serializers

from payments.models import (
    PaymentOrder,
    PromoCode,
    Calc,
    Output,
    RefLinks,
    RefOutput,
    PurchaseCompositeItems,
)
from payments.manager import PaymentManager
from users.serializers import AdminUserListSerializer, UserItemSerializer
from users.models import UserItems
from datetime import datetime
from core.models import GenericSettings

import phonenumbers
import re


class UserPaymentOrderSerializer(serializers.ModelSerializer):
    type_payments = serializers.ChoiceField(choices=PaymentOrder.PAYMENT_TYPES_CHOICES)

    class Meta:
        model = PaymentOrder
        fields = (
            "order_id",
            "email",
            "type_payments",
            "sum",
            "include_service",
            "location",
            "status",
            "created_at",
            "active",
        )
        read_only_fields = ("order_id", "status", "active")

    def create(self, vals):
        data = vals
        data.update({"user": self.context["request"].user})
        manager = PaymentManager()
        if data["type_payments"] == "lava":
            order = manager._create_lava_payment_order(data)
        if data["type_payments"] == "freekassa":
            req = self.context["request"]
            order = manager._create_freekassa_payment_order(request=req, vals=data)
        if data["type_payments"] == "yookassa":
            raise serializers.ValidationError("Недоступный тип оплаты")
        return order


class ActivatePromoCodeSerializer(serializers.ModelSerializer):
    code_data = serializers.CharField(validators=[], write_only=True)

    def validate(self, attrs):
        if "code_data" in attrs:
            if PromoCode.objects.filter(code_data=attrs["code_data"]).exists():
                return attrs
        raise serializers.ValidationError("Нет такого промокода")

    class Meta:
        model = PromoCode
        fields = ("code_data",)


class AdminPaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"


class AdminListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Output
        fields = ("id", "output_id", "type", "status")


class AdminPurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseCompositeItems
        fields = ("id", "ext_id_order", "player_id", "status", "created_at")


class AdminPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseCompositeItems
        fields = "__all__"


class AdminOutputSerializer(AdminListOutputSerializer):
    output_items = UserItemSerializer(many=True)
    purchase_ci_outputs = AdminPurchaseSerializer(many=True)
    cost_withdrawal_of_items = serializers.FloatField()
    cost_withdrawal_of_items_in_rub = serializers.FloatField()

    class Meta:
        model = Output
        fields = "__all__"


class UserListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Output
        fields = (
            "id",
            "output_id",
            "status",
            "created_at",
        )


class UserItemsCreateOutputSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(source="item.item_id")


class UserCreateOutputSerializer(serializers.ModelSerializer):
    output_items = UserItemsCreateOutputSerializer(many=True)

    def validate(self, attrs):
        user = self.context.get("request").user

        items = user.items.all()
        items_ids = [i.id for i in items]

        if not "output_items" in attrs:
            raise serializers.ValidationError("Не выбраны предметы")
        if not "player_id" in attrs:
            raise serializers.ValidationError('Необходимо указать "player_id"')

        if not attrs["output_items"]:
            raise serializers.ValidationError("Не выбраны предметы")

        for i in attrs["output_items"]:
            if not i["item"]["item_id"] in items_ids:
                raise serializers.ValidationError("Нет такого предмета в инвентаре")

            item = items.filter(id=i["item"]["item_id"]).get()

            if item.withdrawn or item.withdrawal_process:
                raise serializers.ValidationError(
                    "Предмет выведен или находится в процессе вывода"
                )
            if not item.active:
                raise serializers.ValidationError("Предмет отсутствует на аккаунте")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        user_items = validated_data.pop("output_items")

        output = Output.objects.create(user=user, **validated_data)
        for i in user_items:
            item = UserItems.objects.filter(id=i["item"]["item_id"]).first()
            item.withdrawal_process = True
            item.save()
            output.output_items.add(item)

        return output

    class Meta:
        model = Output
        fields = (
            "player_id",
            "comment",
            "output_items",
        )


class UserOutputSerializer(serializers.ModelSerializer):
    output_items = UserItemSerializer(many=True)

    class Meta:
        model = Output
        fields = (
            "id",
            "output_id",
            "player_id",
            "comment",
            "status",
            "created_at",
            "active",
            "output_items",
        )


class AdminListPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = (
            "id",
            "name",
            "activations",
            "type",
            "summ",
            "percent",
            "limit_activations",
            "to_date",
            "created_at",
        )


class AdminPromoCodeSerializer(AdminListPromoSerializer):
    type = serializers.ChoiceField(choices=PromoCode.PROMO_TYPES)
    percent = serializers.IntegerField(
        min_value=0, max_value=100, required=False, default=0
    )
    summ = serializers.FloatField(required=False)
    to_date = serializers.DateTimeField(required=False)
    limit_activations = serializers.IntegerField(required=False)
    code_data = serializers.CharField(max_length=128, required=False)
    limit_for_user = serializers.IntegerField(required=False, default=1)
    bonus_limit = serializers.IntegerField(required=False, default=1)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "code_data" in attrs:
            data = attrs["code_data"]
            if self.instance:
                promo = PromoCode.objects.filter(code_data=data).exclude(
                    id=self.instance.id
                )
            else:
                promo = PromoCode.objects.filter(code_data=data)
            if promo.exists():
                raise serializers.ValidationError(
                    {"code_number": "Промокод с таким кодом уже сущесвует!"}
                )
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = PromoCode
        fields = (
            "id",
            "name",
            "type",
            "code_data",
            "active",
            "activations",
            "summ",
            "percent",
            "limit_activations",
            "limit_for_user",
            "bonus_limit",
            "to_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "activations")


class CalcsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calc
        fields = ("user_id", "balance", "created_at")


class RefLinksAdminSerializer(serializers.ModelSerializer):
    from_user = AdminUserListSerializer(read_only=True)

    class Meta:
        model = RefLinks
        fields = ("code_data", "from_user", "active", "created_at")


class AdminGetBalanceMoogoldSerializer(serializers.Serializer):
    balance = serializers.FloatField()
    date = serializers.DateTimeField(default=datetime.now)


class AdminRefOutputListSerializer(serializers.ModelSerializer):
    user = AdminUserListSerializer(read_only=True, source="user.profile")

    class Meta:
        model = RefOutput
        fields = ("ref_output_id", "user", "sum", "status", "active")


class AdminRefOutputSerializer(serializers.ModelSerializer):
    user = AdminUserListSerializer(read_only=True, source="user.profile")

    class Meta:
        model = RefOutput
        fields = "__all__"


class UserRefOutputListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefOutput
        fields = ("ref_output_id", "sum", "status", "type")


class UserRefOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefOutput
        fields = (
            "ref_output_id",
            "sum",
            "status",
            "type",
            "comment",
            "card_number",
            "phone",
            "crypto_number",
            "created_at",
        )


class UserRefOutputCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        user = self.context.get("request").user

        generic_settings = GenericSettings.objects.first()

        if not "sum" in attrs:
            raise serializers.ValidationError("Не указана сумма")

        if generic_settings.min_ref_output > attrs["sum"]:
            raise serializers.ValidationError(
                f"Сумма вывода не может быть меньше {generic_settings.min_ref_output}"
            )

        if attrs["sum"] > user.profile.available_withdrawal:
            raise serializers.ValidationError(
                f"Сумма вывода не может быть больше доступной к выводу"
            )

        if not "type" in attrs:
            raise serializers.ValidationError("Не выбран тип оплаты")

        type_ = attrs["type"]

        if type_ == RefOutput.CARD:
            if not "card_number" in attrs:
                raise serializers.ValidationError("Не введен номер карты")

            attrs["card_number"] = attrs["card_number"].strip()

            pattern0 = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{4}$")
            pattern1 = re.compile(r"^\d{16}$")
            pattern2 = re.compile(r"^[\d\s-]+$")
            pattern3 = re.compile(r"^\d{4} \d{4} \d{4} \d{4}$")

            if not pattern2.match(attrs["card_number"]):
                raise serializers.ValidationError("Номер карты невалиден")

            if (
                pattern0.match(attrs["card_number"])
                or pattern1.match(attrs["card_number"])
                or pattern3.match(attrs["card_number"])
            ):
                pass
            else:
                raise serializers.ValidationError("Номер карты невалиден")

        if type_ == RefOutput.СRYPTOCURRENCY:
            if not "crypto_number" in attrs:
                raise serializers.ValidationError("Не введен номер криптокошелька")

        if type_ == RefOutput.SBP:
            if not "phone" in attrs:
                raise serializers.ValidationError("Не введен номер телефона")
            try:
                phone_num = phonenumbers.parse(attrs["phone"])

                if phonenumbers.is_valid_number(phone_num):
                    pass
                else:
                    raise serializers.ValidationError("Невалидный номер телефона")
            except phonenumbers.phonenumberutil.NumberParseException:
                raise serializers.ValidationError("Невалидный номер телефона")

        attrs["user"] = user

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)

    class Meta:
        model = RefOutput
        fields = ("sum", "comment", "type", "card_number", "phone", "crypto_number")
