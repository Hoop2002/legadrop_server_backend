from rest_framework.serializers import ModelSerializer, ChoiceField
from payments.models import PaymentOrder
from payments.manager import PaymentManager


class UserPaymentOrderSerializer(ModelSerializer):
    type_payments = ChoiceField(choices=PaymentOrder.PAYMENT_TYPES_CHOICES)

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


class AdminPaymentOrderSerializer(ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"
