from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny

from core.models import GenericSettings
from cases.models import OpenedCases, Case
from payments.models import Output, PurchaseCompositeItems
from users.models import UserItems, UserProfile

from legadrop.settings import REDIS_CONNECTION_STRING

from core.serializers import (
    AdminAnalyticsSerializer,
    AdminAnalyticsCommonData,
    FooterSerializer,
    AdminGenericSettingsSerializer,
    AdminAnalyticsIncome,
    AdminAnalyticsOutlay,
    AdminAnalyticsClearProfit,
    AdminAnalyticsAverageCheck,
    AdminAnalyticsCountOpenCases,
    AdminAnalyticsCountRegUser,
    AdminAnalyticsIncomeByCaseType,
    AdminAnalyticsTopUsersDeposite,
    AdminAnalyticsTopRef,
)

from payments.models import PaymentOrder


import redis
import datetime


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
            "graphic_income": AdminAnalyticsIncome,
            "graphic_outlay": AdminAnalyticsOutlay,
            "graphic_clear_profit": AdminAnalyticsClearProfit,
            "graphic_average_check": AdminAnalyticsAverageCheck,
            "graphic_count_open_cases": AdminAnalyticsCountOpenCases,
            "graphic_count_reg_users": AdminAnalyticsCountRegUser,
            "graphic_income_by_case_type": AdminAnalyticsIncomeByCaseType,
            "block_top_users_deposite": AdminAnalyticsTopUsersDeposite,
            "block_top_ref": AdminAnalyticsTopRef,
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

    ### graphics views ###

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_income(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        payments = PaymentOrder.objects.filter(
            created_at__range=(start_date, end_date), status=PaymentOrder.SUCCESS
        )
        records = []

        cur_date = start_date
        while cur_date <= end_date:
            next_date = cur_date + datetime.timedelta(days=1)
            income = (
                payments.filter(created_at__date=cur_date.date()).aggregate(Sum("sum"))[
                    "sum__sum"
                ]
                or 0
            )
            records.append({"income": income, "date": cur_date.date()})
            cur_date = next_date

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_outlay(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        outputs = Output.objects.filter(
            created_at__range=(start_date, end_date), status=Output.COMPLETED
        )

        records = []
        cur_date = start_date
        while cur_date <= end_date:

            sum_ = 0.0
            next_date = cur_date + datetime.timedelta(days=1)
            outlays = outputs.filter(created_at__date=cur_date.date()).all()

            for outlay in outlays:
                sum_ += outlay.cost_withdrawal_of_items_in_rub

            records.append({"outlay": sum_, "date": cur_date.date()})

            cur_date = next_date

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_clear_profit(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        outputs = Output.objects.filter(
            created_at__range=(start_date, end_date), status=Output.COMPLETED
        )
        payments = PaymentOrder.objects.filter(
            created_at__range=(start_date, end_date), status=PaymentOrder.SUCCESS
        )

        records = []
        cur_date = start_date
        while cur_date <= end_date:
            outlay_sum = 0.0

            next_date = cur_date + datetime.timedelta(days=1)

            income = (
                payments.filter(created_at__date=cur_date.date()).aggregate(Sum("sum"))[
                    "sum__sum"
                ]
                or 0
            )

            outlays = outputs.filter(created_at__date=cur_date.date()).all()

            for outlay in outlays:
                outlay_sum += outlay.cost_withdrawal_of_items_in_rub

            if outlay_sum == 0.0:
                profit = income
            else:
                profit = float(income) - outlay_sum

            records.append({"profit": profit, "date": cur_date.date()})

            cur_date = next_date

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_count_open_cases(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        open_cases = OpenedCases.objects.filter(open_date__range=(start_date, end_date))

        records = []

        cur_date = start_date
        while cur_date <= end_date:
            records.append(
                {
                    "count": open_cases.filter(open_date__date=cur_date.date()).count(),
                    "date": cur_date.date(),
                }
            )
            cur_date += datetime.timedelta(days=1)

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_average_check(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        payments = PaymentOrder.objects.filter(
            created_at__range=(start_date, end_date), status=PaymentOrder.SUCCESS
        )
        records = []

        cur_date = start_date
        while cur_date <= end_date:
            next_date = cur_date + datetime.timedelta(days=1)

            payments_cur_date = payments.filter(created_at__date=cur_date.date())

            income = payments_cur_date.aggregate(Sum("sum"))["sum__sum"] or 0

            if income == 0 or payments_cur_date.count() == 0:
                check = 0
            else:
                check = income / payments_cur_date.count()

            records.append({"check": check, "date": cur_date.date()})
            cur_date = next_date

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_count_reg_users(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        seven_days_ago = current_date - datetime.timedelta(days=7)

        kw_start_date = kwargs.get("start_date", seven_days_ago.strftime("%Y-%m-%d"))
        kw_end_date = kwargs.get("end_date", current_date.strftime("%Y-%m-%d"))

        start_date = datetime.datetime.strptime(kw_start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(kw_end_date, "%Y-%m-%d")

        users = User.objects.filter(date_joined__range=[start_date, end_date])

        records = []

        cur_date = start_date
        while cur_date <= end_date:
            records.append(
                {
                    "count": users.filter(date_joined__date=cur_date.date()).count(),
                    "date": cur_date.date(),
                }
            )
            cur_date += datetime.timedelta(days=1)

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Формат даты YYYY-MM-DD. По дефолту будет отдавать данные за неделю"
    )
    def graphic_income_by_case_type(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()

        date = kwargs.get("date", current_date.strftime("%Y-%m-%d"))

        records = []

        cases = Case.objects.all()

        for case in cases:
            income = 0.0

            opening = case.users_opening.filter(
                open_date__date=datetime.datetime.strptime(date, "%Y-%m-%d")
            ).all()
            count = opening.count() or 0
            for open_ in opening:
                income += float(case.price) - float(open_.item.purchase_price)

            records.append(
                {
                    "case_name": case.name,
                    "count_open": count,
                    "income": round(income, 2),
                    "date": datetime.datetime.strptime(date, "%Y-%m-%d").date(),
                }
            )

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)

    ### blocks views ###

    def block_top_ref(self, request, *args, **kwargs):
        users = UserProfile.objects.all()

        records = []

        for user in users:
            count_next = 0

            ref_links = user.ref_links.all()

            for ref in ref_links:
                ref_activate = ref.activated_links.all()
                count_next += ref_activate.count()

            records.append(
                {
                    "id": user.id,
                    "name": user.user.username,
                    "image": str(user.image) or None,
                    "count_next": count_next,
                    "total_income": user.total_income,
                }
            )

        records = sorted(records, key=lambda x: x["total_income"], reverse=True)

        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    def block_top_users_deposite(self, request, *args, **kwargs):
        current_date = datetime.datetime.today()
        back_date = current_date - datetime.timedelta(hours=24)

        top = int(kwargs.get("top"))

        users = UserProfile.objects.all()

        records = []

        for user in users:
            records.append(
                {
                    "id": user.id,
                    "name": user.user.username,
                    "image": str(user.image) or None,
                    "payments_price": user.user.user_payments_orders.filter(
                        created_at__range=[back_date, current_date],
                        status=PaymentOrder.SUCCESS,
                    ).aggregate(Sum("sum"))["sum__sum"]
                    or 0,
                }
            )

        sorted_rec = sorted(records, key=lambda x: x["payments_price"], reverse=True)
        serializer = self.get_serializer(sorted_rec[:top], many=True)

        return Response(serializer.data)

    def get_user_ltv(self, request, *args, **kwargs):
        pass


@extend_schema(tags=["footer"])
class AnalyticsFooterView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(responses=FooterSerializer)
    def get(self, request, r=redis.from_url(REDIS_CONNECTION_STRING)):
        generic = GenericSettings.load()
        opened_cases = OpenedCases.objects.all().count() + generic.opened_cases_buff
        total_users = User.objects.all().count() + generic.users_buff

        users_online = (
            len(r.zrange("asgi:group:online_users", 0, -1)) + generic.online_buff
        )

        total_purchase = (
            UserItems.objects.filter(from_case=False).count() + generic.purchase_buff
        )

        pci = PurchaseCompositeItems.objects.first()

        total_outputs = (
            pci.total_crystals if pci != None else 0
        ) + generic.output_crystal_buff

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
class GenericSettingsViewSet(viewsets.GenericViewSet):
    serializer_class = AdminGenericSettingsSerializer
    queryset = GenericSettings.objects.all()
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        settings = GenericSettings.load()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        settings = GenericSettings.load()
        serializer = self.get_serializer(settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
