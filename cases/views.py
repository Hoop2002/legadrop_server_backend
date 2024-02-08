from rest_framework import status
from rest_framework.viewsets import ModelViewSet
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
    ConditionCaseSerializer,
)
from cases.models import Case, Item, RarityCategory, ConditionCase


@extend_schema(tags=["cases"])
class CasesViewSet(ModelViewSet):
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

    @extend_schema(request=None, responses={200: ItemListSerializer})
    @action(detail=True, permission_classes=[IsAuthenticated])
    def open_case(self, request, *args, **kwargs):
        case = self.get_object()
        message, success = case.check_conditions(user=request.user)
        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        item = case.open_case(request.user)
        serializer = self.get_serializer(item)
        return Response(serializer.data)


@extend_schema(tags=["admin/cases"])
class AdminCaseConditionsViewSet(ModelViewSet):
    queryset = ConditionCase.objects.all()
    serializer_class = ConditionCaseSerializer
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
            return ListCasesSerializer
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
