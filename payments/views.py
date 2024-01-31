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
        payments = request.user.user_payments_orders.all()
        result = self.paginate_queryset(payments, request)
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    def retrieve(self, request, order_id, *args, **kwargs):
        payment = PaymentOrder.objects.filter(order_id=order_id).first()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.data
        validated_data.update({"user": request.user.id})

        serializer.create(validated_data)

        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects
