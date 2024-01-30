from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from payments.models import PaymentOrder
from payments.serializers import UserPaymentOrderSerializer, AdminPaymentOrderSerializer


class UserPaymentOrderViewSet(ModelViewSet):
    serializer_class = UserPaymentOrderSerializer
    queryset = PaymentOrder.objects
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        paginator = LimitOffsetPagination()

        payments = request.user.user_payments_orders.all()
        result = paginator.paginate_queryset(payments, request)

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        pass

class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects
