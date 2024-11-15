import uuid
import re
import hmac
import hashlib

from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.db.models import Sum
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status

from rest_framework_simplejwt.tokens import AccessToken
from social_django.utils import load_backend, load_strategy
from social_core.actions import do_auth
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    BooleanFilter,
    ChoiceFilter,
)

from users.models import UserProfile, UserItems, UserUpgradeHistory, UserVerify
from core.models import GenericSettings
from cases.models import Item
from payments.models import PaymentOrder, RefLinks
from legaemail.models import SendMail
from payments.models import Calc
from cases.serializers import ItemListSerializer
from users.serializers import (
    UserCreateSerializer,
    UserSignInSerializer,
    UserProfileSerializer,
    UserItemSerializer,
    HistoryItemSerializer,
    GetGenshinAccountSerializer,
    AdminUserSerializer,
    AdminUserListSerializer,
    GameHistorySerializer,
    AdminUserPaymentHistorySerializer,
    SuccessSignUpSerializer,
    UpgradeItemSerializer,
    MinimalValuesSerializer,
    UserVerifycationSerializer,
    AdminUserItemSerializer,
    UserReferralSerializer,
    UpgradeHistorySerializer,
    OtherUserItemsSerializer,
    RequestItemsForUpgradeSerializer,
)
from gateways.enka import get_genshin_account
from utils.default_filters import CustomOrderFilter
from utils.serializers import BulkDestroyIntSerializer
from utils.functions.sort_dict import SortDict


@extend_schema(tags=["main"])
class AuthViewSet(GenericViewSet):
    queryset = UserProfile.objects

    def get_permissions(self):
        if self.action == "get_token":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "sign_up":
            return UserCreateSerializer
        if self.action == "get_token":
            return SuccessSignUpSerializer
        return UserSignInSerializer

    def get_token(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            next_url = request.build_absolute_uri(reverse("shopitems_list"))
            user = request.user
            token = AccessToken.for_user(user)
            request.session.clear()
            ref = self._check_cookies(request)
            response = Response({"next": next_url, "token": str(token)})
            if ref:
                ref.delete_cookie("ref")
                ref.activate_link(user)
            return response

    def sign_up(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serializer = self.get_serializer(user)
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            ref = self._check_cookies(request)
            if ref:
                response.delete_cookie("ref")
                ref.activate_link(user)
            return response
        else:
            return Response(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    @extend_schema(request=None, responses={302: None})
    def sign_in_google(self, request, *args, **kwargs):
        strategy = load_strategy(request)
        backend = load_backend(
            strategy=strategy,
            name="google-oauth2",
            redirect_uri=f"{self.request.scheme}://{self.request.get_host()}/complete/google-oauth2/",
        )
        return do_auth(backend, REDIRECT_FIELD_NAME)

    @extend_schema(request=None, responses={301: None})
    def sign_in_vk(self, request, *args, **kwargs):
        strategy = load_strategy(request)
        backend = load_backend(
            strategy=strategy,
            name="vk-oauth2",
            redirect_uri=f"{self.request.scheme}://{self.request.get_host()}/complete/vk-oauth2/",
        )
        return do_auth(backend, REDIRECT_FIELD_NAME)

    def sign_in(self, request, *args, **kwargs):
        username = self.request.data.get("username")
        password = self.request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            message = (
                "Пожалуйста, введите корректные имя пользователя и"
                " пароль учётной записи. Оба поля могут быть чувствительны"
                " к регистру."
            )
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        token = AccessToken.for_user(user)
        ref = self._check_cookies(request)
        response = Response(str(token))
        if ref:
            ref.delete_cookie("ref")
            ref.activate_link(user)
        return response

    @staticmethod
    def _check_cookies(request):
        cookie = request.COOKIES.get("ref")
        if not cookie:
            return None
        ref = RefLinks.objects.filter(
            code_data=cookie, active=True, removed=False, from_user__isnull=False
        )
        if not ref:
            return None
        return ref.first()

    @extend_schema(request=None)
    def sign_up_in_telegram(self, request, *args, **kwargs):

        data = request.data

        if not data.get("hash", False):
            return Response({"message": "Некорректные данные"}, status=400)
        else:
            hash_req = data.pop("hash")

        sort_data = SortDict(data=data)
        message = "\n".join([f"{key}={value}" for key, value in sort_data.items()])

        hash_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        check_hash = hmac.new(
            key=hash_key, msg=message.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        if hash_req == check_hash:
            user = request.user
            exist_user = UserProfile.objects.filter(telegram_id=data["id"]).first()

            if exist_user and not user.is_authenticated:
                next_url = request.build_absolute_uri(reverse("shopitems_list"))
                token = AccessToken.for_user(exist_user.user)
                request.session.clear()
                return Response({"next": next_url, "token": str(token)}, status=200)

            if user.is_authenticated:
                if not user.profile.telegram_id:
                    user.profile.telegram_id = int(data["id"])
                    user.profile.telegram_username = str(data["username"])
                    if not user.first_name:
                        user.first_name = str(data["first_name"])
                    user.save()
                    user.profile.save()

                    return Response(
                        {"message": "Аккаунт успешно привязан."}, status=200
                    )
                else:
                    return Response(
                        {"message": f"Аккаунт {data['username']} уже привязан."}
                    )

            if not user.is_authenticated and not exist_user:
                next_url = request.build_absolute_uri(reverse("shopitems_list"))
                user_cr = User.objects.create_user(
                    username=data["username"], first_name=data.get("first_name", "")
                )
                user_cr.profile.telegram_id = int(data["id"])
                user_cr.profile.telegram_username = str(data["username"])
                user_cr.profile.save()

                token = AccessToken.for_user(user_cr)

                request.session.clear()
                return Response({"next": next_url, "token": str(token)}, status=200)

        else:
            return Response({"message": "Некорректные данные"}, status=400)

        return Response({"message": "Вы уже авторизованы"}, status=400)


@extend_schema(tags=["user"])
class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    def retrieve_other_user(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        instance = self.queryset.filter(id=user_id)

        if not instance:
            return Response({"message": "Пользователь не найден"}, status=404)

        serializer = self.get_serializer(instance.get())
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        _instance = self.queryset.get(id=request.user.profile.id)
        serializer = self.get_serializer(_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@extend_schema(tags=["user"])
class UpgradeHistoryViewSet(ModelViewSet):
    queryset = UserUpgradeHistory.objects.all()
    serializer_class = UpgradeHistorySerializer
    http_method_names = ("get",)


class UserRefViewSet(GenericViewSet):
    queryset = UserProfile.objects
    serializer_class = UserReferralSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserItemsListView(ModelViewSet):
    queryset = UserItems.objects
    http_method_names = ("get", "delete", "post")
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "items_history":
            return HistoryItemSerializer
        if self.action == "other_user_list":
            return OtherUserItemsSerializer
        return UserItemSerializer

    def list(self, request, *args, **kwargs):
        items = self.paginate_queryset(
            self.get_queryset().filter(active=True, user=request.user)
        )
        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response

    @extend_schema(request=None)
    def destroy(self, request, *args, **kwargs):
        user_item: UserItems = self.get_object()
        if not user_item.active:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not request.user == user_item.user:
            return Response(
                {"message": "Не ваш предмет"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_item.withdrawal_process:
            return Response(
                {"message": "Предмет в процессе вывода"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_item.withdrawn:
            return Response(
                {"message": "Предмет выведен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_item.sale_item()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=BulkDestroyIntSerializer, responses=None)
    @action(detail=False, methods=("delete", "post"))
    def bulk_destroy(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        count = self.queryset.model.bulk_sale(request.user, ids)
        if not count:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None)
    def items_history(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(active=False, user=request.user)
        items = self.paginate_queryset(queryset)
        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response

    @extend_schema(request=None, responses={200: UserItemSerializer(many=True)})
    @action(detail=True, methods=("get",), pagination_class=LimitOffsetPagination)
    def other_user_list(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = User.objects.filter(profile__id=user_id).last()
        if not user:
            return Response({"message": "Пользователь не найден"}, status=404)

        queryset = self.get_queryset().filter(user=user)
        items = self.paginate_queryset(queryset)

        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response


@extend_schema(tags=["upgrade"])
class UpgradeItem(GenericViewSet):
    queryset = UserItems.objects
    serializer_class = UpgradeItemSerializer
    http_method_names = ("get", "post")
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ("price",)
    search_fields = ("name",)

    def get_serializer_class(self):
        if self.action == "get_minimal_values":
            return MinimalValuesSerializer
        if self.action == "upgrade":
            return ItemListSerializer
        if self.action == "items":
            return RequestItemsForUpgradeSerializer
        if self.action == "user_items":
            return UserItemSerializer
        return UpgradeItemSerializer

    @extend_schema(responses={200: UserItemSerializer(many=True)})
    @action(detail=False, methods=("get",), pagination_class=LimitOffsetPagination)
    def user_items(self, request, *args, **kwargs):
        items = self.paginate_queryset(
            self.get_queryset().filter(
                withdrawal_process=False, active=True, user=request.user
            )
        )
        serializer = self.get_serializer(items, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        request=RequestItemsForUpgradeSerializer,
        responses={200: ItemListSerializer(many=True)},
        description="Поля доступные для сортировки списка: `price`. Сортировка от большего к меньшему `-price`",
    )
    @action(detail=False, pagination_class=LimitOffsetPagination, methods=("post",))
    def items(self, request, *args, **kwargs):
        generic = GenericSettings.load()

        data_serializer = self.get_serializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)

        if data_serializer.validated_data.get("upgrade_items"):
            current_price = (
                data_serializer.validated_data.get("upgrade_items").aggregate(
                    sum=Sum("item__price")
                )["sum"]
                or 0
            )
        else:
            current_price = data_serializer.validated_data.get("balance")

        max_update = current_price * (generic.base_upgrade_percent * 100)
        min_update = current_price * generic.base_upper_ratio

        items = self.filter_queryset(
            Item.objects.filter(
                upgrade=True,
                removed=False,
                price__gte=min_update,
                price__lte=max_update,
            ).exclude(price=0)
        )
        paginated = self.paginate_queryset(items)
        serializer = ItemListSerializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["post"])
    def get_minimal_values(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self._get_min_values(serializer.validated_data["upgraded_item"])
        return Response(data)

    @action(detail=False, methods=["post"])
    def get_upgrade_data(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message, _status = self._check_conditions(data)
        if not _status:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        upgrade_ratio, upgrade_percent = message

        return Response(
            {
                "upgrade_ratio": round(upgrade_ratio, 4),
                "upgrade_percent": round(upgrade_percent * 100, 4),
            }
        )

    @extend_schema(responses={200: ItemListSerializer, 204: None})
    @action(detail=False, methods=["post"])
    def upgrade_items(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message, _status = self._check_conditions(data)
        if not _status:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        if "balance" in data:
            _status, item = UserItems.upgrade_item(
                user=request.user,
                balance=data["balance"],
                upgraded=data["upgraded_item"],
            )
            history = UserUpgradeHistory.objects.create(
                user=request.user,
                balance=data["balance"],
            )
            history.desired.add(data["upgraded_item"])
            Calc.objects.create(
                balance=-data["balance"],
                user=request.user,
                comment="Апгрейд",
                demo=request.user.profile.demo,
            )
            if not _status:
                if item == "Проигрыш":
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            history.success = True
            history.save()
            UserItems.objects.create(item=item, user=request.user)
            return Response(ItemListSerializer(item).data)
        else:
            _status, item = UserItems.upgrade_item(
                user=request.user,
                upgrade=data["upgrade_items"],
                upgraded=data["upgraded_item"],
            )
            history = UserUpgradeHistory.objects.create(
                user=request.user,
            )
            history.upgraded.set(data["upgrade_items"])
            history.desired.add(data["upgraded_item"])
            data["upgrade_items"].update(active=False)
            if not _status:
                if item == "Проигрыш":
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(status=status.HTTP_400_BAD_REQUEST)

            history.success = True
            history.save()
            UserItems.objects.create(item=item, user=request.user)
            return Response(ItemListSerializer(item).data)

    def _check_conditions(self, data) -> (str, bool) or ((float, float), bool):
        generic = GenericSettings.load()
        if data.get("upgrade_items"):
            cost = data.get("upgrade_items").aggregate(sum=Sum("item__price"))["sum"]
        else:
            cost = data.get("balance")
        upgraded_cost = data.get("upgraded_item").price
        default_data = self._get_min_values(data.get("upgraded_item"))

        upgrade_ratio = upgraded_cost / cost
        upgrade_percent = generic.base_upgrade_percent / upgrade_ratio

        if upgrade_ratio < generic.base_upper_ratio:
            return "Слишком большая ставка", False
        if (cost < generic.minimal_price_upgrade) or (cost < default_data["min_bet"]):
            return f"Минимальная ставка от {default_data['min_bet']}", False
        return (upgrade_ratio, upgrade_percent), True

    @staticmethod
    def _get_min_values(item) -> dict[str:float]:
        generic = GenericSettings.load()
        upgraded_cost = item.price
        min_bet = upgraded_cost / (generic.base_upgrade_percent * 100)
        if generic.minimal_price_upgrade > min_bet:
            min_bet = generic.minimal_price_upgrade
        min_ratio = generic.base_upper_ratio
        max_ratio = upgraded_cost / min_bet
        max_bet = upgraded_cost / generic.base_upper_ratio
        return {
            "min_bet": round(min_bet, 2),
            "min_ratio": round(min_ratio, 4),
            "max_bet": round(max_bet, 2),
            "max_ratio": round(max_ratio, 4),
        }


@extend_schema(tags=["genshin"])
class GetGenshinAccountView(GenericViewSet):
    http_method_names = ["post"]
    serializer_class = GetGenshinAccountSerializer

    def get_uid(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rdata = get_genshin_account(uid=serializer.validated_data["uid"])

        if not rdata:
            return Response(
                {"message": "Такого аккаунта не существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"result": rdata}, status=status.HTTP_200_OK)


class UserCustomOrderFilter(CustomOrderFilter):
    allowed_custom_filters = (
        "user_id",
        "username",
        "balance",
        "winrate",
        "all_output",
        "all_debit",
        "is_active",
    )
    fields_related = {
        "username": "user__username",
        "is_active": "user__is_active",
        "balance": "balance_save",
        "winrate": "winrate_save",
        "all_debit": "debit_save",
        "all_output": "output_save",
    }


class UsersFilter(FilterSet):
    is_active = BooleanFilter(field_name="user__is_active")
    individual_percent = BooleanFilter(
        field_name="individual_percent", method="filter_individual_percent"
    )

    @staticmethod
    def filter_individual_percent(queryset, name, value):
        if value is True:
            return queryset.exclude(individual_percent=0)
        if value is False:
            return queryset.filter(individual_percent=0)
        return queryset


@extend_schema(tags=["admin/users"])
class AdminUsersViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminUser]
    http_method_names = ("post", "get", "put")
    lookup_field = "user_id"
    filter_backends = (DjangoFilterBackend, UserCustomOrderFilter, SearchFilter)
    filterset_class = UsersFilter
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "telegram_username",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return AdminUserListSerializer
        return AdminUserSerializer

    @extend_schema(
        description=(
            "Поля доступные для сортировки списка: `user_id`, `username`, `balance`, `winrate`, "
            "`all_output`, `all_debit`, `is_active`. Сортировка от большего к меньшему "
            '"`-user_id`", от меньшего к большему "`user_id`", работает для всех полей'
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        _instance = self.get_object()
        serializer = self.get_serializer(_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_202_ACCEPTED)


class UserItemsOrdering(CustomOrderFilter):
    allowed_custom_filters = (
        "id",
        "case_name",
        "open_date",
        "case_price",
        "item_price",
        "item_price_sold",
        "item_name",
    )
    fields_related = {
        "case_name": "case__name",
        "open_date": "created_at",
        "case_price": "case__price",
        "item_price": "item__price",
        "item_price_sold": "calc__balance",
        "item_name": "item__name",
    }


class UserItemsFilter(FilterSet):
    ITEM_STATUSES = (
        ("active", "На аккаунте"),
        ("inactive", "Продан"),
        ("withdrawn", "Выведен"),
    )
    status = ChoiceFilter(
        field_name="status", method="filter_status", choices=ITEM_STATUSES
    )

    @staticmethod
    def filter_status(queryset, name, value):
        if value == "active":
            return queryset.filter(active=True, withdrawn=False)
        if value == "inactive":
            return queryset.filter(active=False, withdrawn=False)
        if value == "withdrawn":
            return queryset.filter(withdrawn=True)
        return queryset


@extend_schema(tags=["admin/users"])
class AdminUserHistoryGamesViewSet(GenericViewSet):
    queryset = UserItems.objects
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]
    filter_backends = (DjangoFilterBackend, UserItemsOrdering)
    filterset_class = UserItemsFilter

    def get_serializer_class(self):
        if self.action == "games":
            return GameHistorySerializer
        if self.action == "items_history":
            return HistoryItemSerializer
        return AdminUserItemSerializer

    @extend_schema(
        responses={200: GameHistorySerializer(many=True)},
        description=(
            "Поля доступные для сортировки списка: `id`, `case_name`, `open_date`, `case_price`, "
            "`item_price`. Сортировка от большего к меньшему "
            '"`-id`", от меньшего к большему "`id`", работает для всех полей'
        ),
    )
    @action(detail=False, pagination_class=LimitOffsetPagination)
    def games(self, request, *args, **kwargs) -> GameHistorySerializer(many=True):
        user_id = kwargs.get("user_id")
        queryset = self.filter_queryset(
            self.get_queryset().filter(user_id=user_id, from_case=True)
        )
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        responses={200: AdminUserItemSerializer(many=True)},
        description=(
            "Поля доступные для сортировки списка: `id`, `item_price`, `item_name`."
            " Сортировка от большего к меньшему "
            '"`-id`", от меньшего к большему "`id`", работает для всех полей'
        ),
    )
    @action(detail=False, pagination_class=LimitOffsetPagination)
    def items(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        responses={200: HistoryItemSerializer(many=True)},
        description=(
            "Поля доступные для сортировки списка: `id`, `item_price_sold`, `item_name`."
            " Сортировка от большего к меньшему "
            '"`-id`", от меньшего к большему "`id`", работает для всех полей'
        ),
    )
    @action(detail=False, pagination_class=LimitOffsetPagination)
    def items_history(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        queryset = self.filter_queryset(
            self.get_queryset().filter(active=False, user_id=user_id)
        )
        items = self.paginate_queryset(queryset)
        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response


@extend_schema(tags=["admin/users"])
class AdminUserPaymentHistoryViewSet(GenericViewSet):
    queryset = PaymentOrder.objects
    serializer_class = AdminUserPaymentHistorySerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ("id", "type_payments", "created_at", "sum", "status")
    filterset_fields = ("type_payments", "status")

    @extend_schema(
        description=(
            "Поля доступные для сортировки списка: `id`, `type_payments`, `created_at`, `sum`, `status`."
            " Сортировка от большего к меньшему "
            '"`-id`", от меньшего к большему "`id`", работает для всех полей'
        ),
    )
    def list(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(tags=["verify"])
class UserVerificationViewSet(ModelViewSet):
    http_method_names = ["post", "get"]
    serializer_class = UserVerifycationSerializer
    permission_classes = [IsAuthenticated]

    def verify(self, request, *args, **kwargs):
        if request.user.profile.verified:
            return Response(
                {"message": "Вы уже верефицированный пользователь!"}, status=400
            )

        from datetime import timedelta
        from django.utils import timezone

        serializer = self.get_serializer(request.data)
        data = serializer.data

        pattern0 = re.compile(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$")
        if not pattern0.match(data["email"]):
            return Response({"message": "Некорректный email"}, status=400)

        verify_check = UserVerify.objects.filter(email=data["email"], active=True)

        if verify_check:
            return Response(
                {
                    "message": f"Уже существует заявка на верификацию, проверьте почту {data['email']}"
                },
                status=400,
            )

        verify = UserVerify.objects.create(
            email=data["email"],
            access_token=str(uuid.uuid4()),
            active=True,
            to_date=timezone.localtime() + timedelta(minutes=15),
            user=request.user,
        )

        generic = GenericSettings.objects.first()

        domain = generic.email_verify_url + verify.access_token

        email = SendMail.objects.create(
            to_email=data["email"],
            type=SendMail.VERIFY,
            text=f"""Здравствуйте! \n Чтобы подтвердить ваш аккаунт перейдите по ссылке {domain}""",
        )

        return Response(
            {"message": f"Заявка создана, проверьте почту {verify.email}"}, status=200
        )

    def verify_user(self, request, access_token: str, *args, **kwargs):
        verify = UserVerify.objects.filter(access_token=access_token, active=True)

        if not verify:
            return Response({"message": "Некорректный access token"}, status=400)

        verify = verify.get()

        if verify.user == request.user:
            user = request.user
            user.profile.verified = True
            user.email = verify.email

            user.profile.save()
            user.save()

            verify.active = False
            verify.save()

            return Response(
                {"message": "Поздравляем! Вы верефицированный пользователь"}, status=200
            )
        else:
            return Response({"message": "Некорректный access token"}, status=400)
