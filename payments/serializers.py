from rest_framework.serializers import ModelSerializer, ChoiceField
from payments.models import PaymentOrder
from gateways.lava_api import LavaApi
from django.conf import settings

class UserPaymentOrderSerializer(ModelSerializer):
    type_payments = ChoiceField(choices=PaymentOrder.PAYMENT_TYPES_CHOICES)

    def create(self, validated_data):
        lava = LavaApi()
        return super().create(validated_data)

    class Meta:
        model = PaymentOrder
        fields = ("order_id", "email", "genshin_uid", 'type_payments', "status", "active")
        read_only_fields = ("order_id", "status", 'active')
    

    
class AdminPaymentOrderSerializer(ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"
