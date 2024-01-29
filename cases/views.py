from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from cases.serializers import CasesSerializer, ItemListSerializer
from cases.models import Case, Item


class CasesViewSet(ModelViewSet):
    serializer_class = CasesSerializer
    queryset = Case.objects

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ItemsViewSet(ModelViewSet):
    serializer_class = ItemListSerializer
    queryset = Item.objects

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
