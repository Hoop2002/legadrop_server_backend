from django.contrib.auth import authenticate, login
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import status
from drf_spectacular.utils import extend_schema

from rest_framework.response import Response

from users.models import UserProfile, UserItems
from users.serializers import (
    UserProfileCreateSerializer,
    UserSignInSerializer,
    UserProfileSerializer,
    UserItemSerializer,
    HistoryItemSerializer,
    GetGenshinAccountSerializer,
    AdminUserSerializer,
    AdminUserListSerializer,
    GameHistorySerializer,
    AdminUserPaymentHistorySerializer,
)
from payments.models import PaymentOrder, RefLinks

from gateways.enka import get_genshin_account


@extend_schema(tags=["main"])
class AuthViewSet(GenericViewSet):
    queryset = UserProfile.objects
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        serializers = {
            "sign_up": UserProfileCreateSerializer,
            "sign_in": UserSignInSerializer,
        }
        return serializers[self.action]

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


@extend_schema(tags=["user"])
class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        _instance = self.queryset.get(id=request.user.profile.id)
        serializer = self.get_serializer(_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class UserItemsListView(ModelViewSet):
    queryset = UserItems.objects
    http_method_names = ["get", "delete"]

    def get_serializer_class(self):
        if self.action == "items_history":
            return HistoryItemSerializer
        return UserItemSerializer

    def list(self, request, *args, **kwargs):
        items = self.paginate_queryset(self.get_queryset().filter(active=True))
        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response

    @extend_schema(request=None)
    def destroy(self, request, *args, **kwargs):
        user_item: UserItems = self.get_object()

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

    @extend_schema(request=None)
    def items_history(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(active=False)
        items = self.paginate_queryset(queryset)
        serializer = self.get_serializer(items, many=True)
        response = self.get_paginated_response(serializer.data)
        return response


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


@extend_schema(tags=["admin/users"])
class AdminUsersViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put"]
    lookup_field = "user_id"

    def get_serializer_class(self):
        if self.action == "list":
            return AdminUserListSerializer
        return AdminUserSerializer

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


@extend_schema(tags=["admin/users"])
class AdminUserHistoryGamesViewSet(GenericViewSet):
    queryset = UserItems.objects
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def get_serializer_class(self):
        if self.action == "games":
            return GameHistorySerializer
        return UserItemSerializer

    @extend_schema(responses={200: GameHistorySerializer(many=True)})
    @action(detail=False, pagination_class=LimitOffsetPagination)
    def games(self, request, *args, **kwargs) -> GameHistorySerializer(many=True):
        user_id = kwargs.get("user_id")
        queryset = self.get_queryset().filter(user_id=user_id, from_case=True)
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(responses={200: UserItemSerializer(many=True)})
    @action(detail=False, pagination_class=LimitOffsetPagination)
    def items(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        queryset = self.get_queryset().filter(user_id=user_id)
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(tags=["admin/users"])
class AdminUserPaymentHistoryViewSet(GenericViewSet):
    queryset = PaymentOrder.objects
    serializer_class = AdminUserPaymentHistorySerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        queryset = self.get_queryset().filter(user_id=user_id)
        paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)
