from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from core.models import GenericSettings
from cases.models import OpenedCases
from payments.models import PaymentOrder, Output
from users.models import UserItems

from core.serializers import (
    AdminAnalyticsSerializer,
    AdminAnalyticsCommonData,
    FooterSerializer,
    AdminGenericSettingsSerializer,
)


class BaseDateFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="created_at", lookup_expr="lte")


@extend_schema(tags=["admin/analytics"])
class AdminAnalyticsViewSet(ModelViewSet):
    queryset = PaymentOrder.objects.filter(
        status__in=[PaymentOrder.SUCCESS, PaymentOrder.APPROVAL]
    )
    pagination_class = []
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BaseDateFilter
    http_method_names = ["get"]
    permission_classes = [IsAdminUser]

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
        total_expense = Output.objects.filter(
            active=False, status="completed"
        ).aggregate(Sum("withdrawal_price"))
        total_expense = total_expense["withdrawal_price__sum"] or 0
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

        total_expense = Output.objects.filter(
            active=False, status="completed"
        ).aggregate(Sum("withdrawal_price"))
        total_expense = total_expense["withdrawal_price__sum"] or 0
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


@extend_schema(tags=["footer"])
class AnalyticsFooterView(APIView):
    @extend_schema(responses=FooterSerializer)
    def get(self, request):
        generic = GenericSettings.load()
        opened_cases = OpenedCases.objects.all().count() + generic.opened_cases_buff
        total_users = User.objects.all().count() + generic.users_buff
        # todo сделать онлайн пользователей
        users_online = 0 + generic.users_buff
        total_purchase = (
            UserItems.objects.filter(from_case=False).count() + generic.purchase_buff
        )
        # todo выводы
        total_outputs = 0 + generic.output_crystal_buff
        data = dict(
            opened_cases=opened_cases,
            total_users=total_users,
            users_online=users_online,
            total_purchase=total_purchase,
            total_crystal=total_outputs,
        )
        serializer = FooterSerializer(data)
        return Response(serializer.data)


@extend_schema(tags=["admin/generic"])
class GenericSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = AdminGenericSettingsSerializer
    queryset = GenericSettings.objects.all()
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "put"]

    def create(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            return Response(
                {
                    "message": "Уже созданы настройки ядра, теперь их можно только изменить"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)
