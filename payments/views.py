from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from payments.models import PaymentOrder
from payments.serializers import UserPaymentOrderSerializer, AdminPaymentOrderSerializer


class UserPaymentOrderViewSet(ModelViewSet):
    serializer_class = UserPaymentOrderSerializer
    queryset = PaymentOrder.objects
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    

class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects