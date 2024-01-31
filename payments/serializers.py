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
            "status",
            "active",
        )
        read_only_fields = ("order_id", "status", "active")
    
    def create(self, validated_data):
        manager = PaymentManager()
        if validated_data['type_payments'] == "lava":
            order = manager._create_lava_payment_order(validated_data)
        return order


class AdminPaymentOrderSerializer(ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"
