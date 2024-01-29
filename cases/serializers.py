from rest_framework.serializers import ModelSerializer
from cases.models import Case, Item


class CasesSerializer(ModelSerializer):
    class Meta:
        model = Case
        fields = ("id", "name", "price")


class ItemListSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("id", "name")
