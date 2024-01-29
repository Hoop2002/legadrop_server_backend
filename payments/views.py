from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from payments.models import PaymentOrder
from payments.serializers import UserPaymentOrderSerializer, AdminPaymentOrderSerializer


class UserPaymentOrderViewSet(ModelViewSet):
    serializer_class = UserPaymentOrderSerializer
    queryset = PaymentOrder.objects
    

class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects