from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser

from cases.models import OpenedCases
from payments.models import PaymentOrder, PromoCode, Calc
from payments.serializers import (
    UserPaymentOrderSerializer,
    AdminPaymentOrderSerializer,
    AdminPromoCodeSerializer,
    AdminListPromoSerializer,
    ActivatePromoCodeSerializer,
    AdminAnalyticsSerializer,
    ApprovalOrderPaymentsSerializer,
    AdminAnalyticsCommonData,
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


@extend_schema(tags=["admin/payments"])
class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "order_id"
    http_method_names = ["get", "post", "delete", "put"]


@extend_schema(tags=["admin/payments"])
class ApprovalAdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = ApprovalOrderPaymentsSerializer
    queryset = PaymentOrder.objects
    permission_classes = [IsAdminUser]
    lookup_field = "order_id"

    @extend_schema(responses={200: SuccessSerializer})
    def approval(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = PaymentOrder.objects.get(
            order_id=serializer.validated_data["order_id"]
        )
        if not payment:
            return Response(
                {"message": "Такого пополнения не существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment.active == False:
            return Response(
                {"message": "Уже одобрен или отменен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message, success = payment.approval_payment_order()

        return Response({"message": message}, status=status.HTTP_200_OK)


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
    from_date = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="created_at", lookup_expr="lte")


@extend_schema(tags=["admin/analytics"])
class AdminAnalyticsViewSet(ModelViewSet):
    queryset = PaymentOrder.objects.filter(
        status__in=[PaymentOrder.SUCCESS, PaymentOrder.APPROVAL]
    )
    pagination_class = []
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CalcFilter
    http_method_names = ["get"]

    def get_serializer_class(self):
        serializer = {
            "list": AdminAnalyticsSerializer,
            "common_data": AdminAnalyticsCommonData,
        }
        return serializer[self.action]

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать текущий день"
    )
    def list(self, request, *args, **kwargs):
        default_filter = dict()
        default_user_filter = dict()
        if "from_date" not in request.query_params:
            default_from = timezone.localtime().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            default_filter["created_at__gte"] = default_from
            default_user_filter["date_joined__gte"] = default_from.isoformat()
        else:
            default_user_filter["date_joined__gte"] = timezone.datetime.strptime(
                request.query_params["from_date"], "%Y-%m-%d"
            )
        if "to_date" not in request.query_params:
            default_to = timezone.localtime().replace(
                hour=23, minute=59, second=59, microsecond=50
            )
            default_filter["created_at__lte"] = default_to
            default_user_filter["date_joined__lte"] = default_to.isoformat()
        else:
            default_user_filter["date_joined__lte"] = timezone.datetime.strptime(
                request.query_params["from_date"], "%Y-%m-%d"
            )

        queryset = self.filter_queryset(self.get_queryset().filter(**default_filter))
        total_income = queryset.aggregate(Sum("sum"))["sum__sum"] or 0
        total_expense = 0  # todo добавить сумму вывода
        count_users = User.objects.filter(
            **default_user_filter, is_staff=False, is_superuser=False
        ).count()
        data = dict(
            total_expense=total_expense,
            total_income=total_income,
            profit=total_income - total_expense,
            count_users=count_users,
        )

        serializer = self.get_serializer(data)
        return Response(serializer.data)

    def common_data(self, request, *args, **kwargs):
        opened_cases = OpenedCases.objects.filter(
            open_date__gte=timezone.localdate()
        ).count()
        count_users = User.objects.filter(is_staff=False, is_superuser=False).count()
        total_income = self.get_queryset().aggregate(Sum("sum"))["sum__sum"] or 0

        if not total_income or not count_users:
            average_income = 0
        else:
            average_income = total_income / count_users

        total_expense = 0  # todo добавить сумму всех выводов
        ggr = total_income - total_expense

        serializer = self.get_serializer(
            {
                "total_open": opened_cases,
                "online": 1,
                "average_income": average_income,
                "ggr": ggr,
            }
        )
        return Response(serializer.data)
