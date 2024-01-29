from rest_framework.serializers import ModelSerializer
from payments.models import PaymentOrder


class UserPaymentOrderSerializer(ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = ("order_id", "email", "status", "active")


class AdminPaymentOrderSerializer(ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"
