from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from cases.serializers import CasesSerializer, ItemListSerializer
from cases.models import Case, Item


class CasesViewSet(ModelViewSet):
    serializer_class = CasesSerializer
    queryset = Case.objects

    def list(self, request, *args, **kwargs):
        cases = self.paginate_queryset(self.get_queryset().all())
        serializer = self.get_serializer(cases, many=True)
        result = self.get_paginated_response(serializer.data)
        return result


class ItemsViewSet(ModelViewSet):
    serializer_class = ItemListSerializer
    queryset = Item.objects

    def list(self, request, *args, **kwargs):
        items = self.paginate_queryset(self.get_queryset().all())
        serializer = self.get_serializer(items, many=True)
        result = self.get_paginated_response(serializer.data)
        return result
