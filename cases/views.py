from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from cases.serializers import (
    CaseSerializer,
    ListCasesSerializer,
    AdminCasesSerializer,
    ItemListSerializer,
    UserItemSerializer,
    ItemsAdminSerializer,
    RarityCategoryAdminSerializer,
    ConditionSerializer,
    AdminContestsSerializer,
    ContestsSerializer,
    AdminListCasesSerializer,
)
from cases.models import Case, Item, RarityCategory, ConditionCase, Contests
from utils.serializers import SuccessSerializer


@extend_schema(tags=["contests"])
class ContestsViewSet(ModelViewSet):
    queryset = Contests.objects.filter(active=True, removed=False)
    serializer_class = ContestsSerializer
    http_method_names = ["get", "post"]
    lookup_field = "contest_id"

    @extend_schema(
        request=None, responses={200: SuccessSerializer, 400: SuccessSerializer}
    )
    def participate(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.participants.filter(id=request.user.id).exists():
            return Response(
                {"message": "Вы уже принимаете участие в этом конкурсе!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        message, _status = instance.check_conditions(request.user)
        if not _status:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        instance.participants.add(request.user)
        return Response(
            {"message": "Теперь вы принимаете участие в конкурсе"},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["cases"])
class CasesViewSet(GenericViewSet):
    queryset = Case.objects.filter(active=True, removed=False)
    permission_classes = [AllowAny]
    lookup_field = "translit_name"
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "list":
            return ListCasesSerializer
        if self.action == "open_case":
            return ItemListSerializer
        return CaseSerializer

    def get_permissions(self):
        if self.action == "open_case":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginate_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginate_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={200: ItemListSerializer})
    @action(detail=True, methods=["post"])
    def open_case(self, request, *args, **kwargs):
        case = self.get_object()
        message, success = case.check_conditions(user=request.user)
        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        if case.price > request.user.profile.balance:
            return Response(
                {"message": "Недостаточно средств!"}, status=status.HTTP_400_BAD_REQUEST
            )
        item = case.open_case(request.user)
        serializer = self.get_serializer(item)
        return Response(serializer.data)


@extend_schema(tags=["admin/conditions"])
class AdminConditionsViewSet(ModelViewSet):
    queryset = ConditionCase.objects.all()
    serializer_class = ConditionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "condition_id"
    http_method_names = ["get", "post", "delete", "put"]

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


@extend_schema(tags=["admin/cases"])
class AdminCasesViewSet(ModelViewSet):
    queryset = Case.objects.filter(removed=False)
    permission_classes = [IsAdminUser]
    lookup_field = "case_id"
    http_method_names = ["get", "post", "delete", "put"]

    def get_serializer_class(self):
        if self.action == "list":
            return AdminListCasesSerializer
        return AdminCasesSerializer

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(case_id=self.kwargs["case_id"], removed=False)
            .update(removed=True, active=False)
        )
        if count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class ShopItemsViewSet(ModelViewSet):
    serializer_class = ItemListSerializer
    queryset = Item.objects.filter(sale=True, removed=False)
    permission_classes = [AllowAny]
    lookup_field = "item_id"
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action == "buy_item":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        serializers = {
            "list": ItemListSerializer,
            "retrieve": ItemListSerializer,
            "buy_item": UserItemSerializer,
        }
        return serializers[self.action]

    @extend_schema(request=None, responses={200: ItemListSerializer})
    def buy_item(self, request, *args, **kwargs):
        item = self.get_object()
        self.check_object_permissions(self.request, item)
        user = self.request.user
        serializer = self.get_serializer(data={"item": item.id, "user": user.id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(ItemListSerializer(item).data)


@extend_schema(tags=["admin/items"])
class ItemAdminViewSet(ModelViewSet):
    queryset = Item.objects.filter(removed=False)
    permission_classes = [IsAdminUser]
    lookup_field = "item_id"
    http_method_names = ["get", "post", "delete", "put"]

    def get_serializer_class(self):
        if self.action == "list":
            return ItemListSerializer
        return ItemsAdminSerializer

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(item_id=self.kwargs["item_id"], removed=False)
            .update(removed=True, sale=False)
        )
        if count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=["admin/rarity"])
class AdminRarityCategoryViewSet(ModelViewSet):
    queryset = RarityCategory.objects.all()
    serializer_class = RarityCategoryAdminSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "put", "delete"]


@extend_schema(tags=["admin/contest"])
class AdminContestViewSet(ModelViewSet):
    queryset = Contests.objects.filter(removed=False)
    lookup_field = "contest_id"
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "list":
            return ContestsSerializer
        return AdminContestsSerializer

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(contest_id=self.kwargs["contest_id"], removed=False)
            .update(removed=True, active=False)
        )

        if count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def set_random_award(self, request, *args, **kwargs):
        instance = self.get_object()
        message = instance.set_new_award()
        if message:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
