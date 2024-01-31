from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema

from cases.serializers import CasesSerializer, ItemListSerializer, UserItemSerializer, ItemsAdminSerializer
from cases.models import Case, Item


class CasesViewSet(ModelViewSet):
    serializer_class = CasesSerializer
    queryset = Case.objects.filter(active=True)
    permission_classes = [AllowAny]


class ShopItemsViewSet(ModelViewSet):
    serializer_class = ItemListSerializer
    queryset = Item.objects.filter(sale=True)
    permission_classes = [AllowAny]
    lookup_field = "item_id"

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
        user = self.request.user
        serializer = self.get_serializer(data={"item": item.id, "user": user.id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(ItemListSerializer(item).data)


@extend_schema(tags=['admin'])
class ItemAdminViewSet(ModelViewSet):
    queryset = Item.objects.filter(removed=False)
    permission_classes = [IsAdminUser]
    lookup_field = "item_id"
    http_method_names = ['get', 'post', 'delete', 'put']

    def get_serializer_class(self):
        serializer = {
            'list': ItemListSerializer,
            'retrieve': ItemsAdminSerializer
        }
        return serializer[self.action]
