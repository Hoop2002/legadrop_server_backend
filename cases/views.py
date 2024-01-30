from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from cases.serializers import CasesSerializer, ItemListSerializer
from cases.models import Case, Item


class CasesViewSet(ModelViewSet):
    serializer_class = CasesSerializer
    queryset = Case.objects
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        cases = self.paginate_queryset(self.get_queryset().all())
        serializer = self.get_serializer(cases, many=True)
        result = self.get_paginated_response(serializer.data)
        return result


class ShopItemsViewSet(ModelViewSet):
    serializer_class = ItemListSerializer
    queryset = Item.objects
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        items = self.paginate_queryset(self.get_queryset().filter(sale=True))
        serializer = self.get_serializer(items, many=True)
        result = self.get_paginated_response(serializer.data)
        return result
