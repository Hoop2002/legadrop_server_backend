from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser

from payments.models import PaymentOrder, PromoCode, Calc
from payments.serializers import (
    UserPaymentOrderSerializer,
    AdminPaymentOrderSerializer,
    AdminPromoCodeSerializer,
    AdminListPromoSerializer,
    ActivatePromoCodeSerializer,
    AdminAnalyticsSerializer,
)
from utils.serializers import SuccessSerializer


class UserPaymentOrderViewSet(ModelViewSet):
    serializer_class = UserPaymentOrderSerializer
    queryset = PaymentOrder.objects
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        payments = request.user.user_payments_orders.all()
        result = self.paginate_queryset(payments)
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    def retrieve(self, request, order_id, *args, **kwargs):
        payment = PaymentOrder.objects.filter(order_id=order_id).first()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects


@extend_schema(tags=["promo"])
class PromoViewSet(GenericViewSet):
    queryset = PromoCode.objects
    serializer_class = ActivatePromoCodeSerializer
    lookup_field = "code_data"

    @extend_schema(responses={200: SuccessSerializer})
    def activate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo = PromoCode.objects.get(code_data=serializer.validated_data["code_data"])
        message, success = promo.activate_promo(self.request.user)
        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(tags=["admin/promo"])
class AdminPromoCodeViewSet(ModelViewSet):
    queryset = PromoCode.objects.filter(removed=False)
    serializer_class = AdminPromoCodeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete", "put"]

    def get_serializer_class(self):
        if self.action == "list":
            return AdminListPromoSerializer
        return AdminPromoCodeSerializer

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(request=None)
    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(id=self.kwargs["pk"], removed=False)
            .update(removed=True)
        )
        if count < 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CalcFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name="creation_date", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="creation_date", lookup_expr="lte")


@extend_schema(tags=["analytics"])
class AdminAnalyticsViewSet(ModelViewSet):
    queryset = Calc.objects
    serializer_class = AdminAnalyticsSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CalcFilter

    def list(self, request, *args, **kwargs):
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            from_date = from_date[0]
            to_date = to_date[0]
            analytics = Calc.calc_analytics()

        return Response()
