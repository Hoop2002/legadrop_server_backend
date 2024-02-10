from rest_framework import serializers

from payments.models import PaymentOrder, PromoCode, Calc
from payments.manager import PaymentManager


class UserPaymentOrderSerializer(serializers.ModelSerializer):
    type_payments = serializers.ChoiceField(choices=PaymentOrder.PAYMENT_TYPES_CHOICES)

    class Meta:
        model = PaymentOrder
        fields = (
            "order_id",
            "email",
            "type_payments",
            "sum",
            "include_service_lava",
            "lava_link",
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
        return order


class ApprovalOrderPaymentsSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(validators=[], write_only=True)

    def validate(self, attrs):
        if "order_id" in attrs:
            if PaymentOrder.objects.filter(order_id=attrs["order_id"]).exists():
                return attrs
        raise serializers.ValidationError("Нет такого пополнения")

    class Meta:
        model = PaymentOrder
        fields = ("order_id",)


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


class AdminListPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ("id", "name", "type", "code_data")


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
        fields = ("user_id", "debit", "credit", "created_at")
