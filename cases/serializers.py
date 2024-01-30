from rest_framework import serializers
from cases.models import Case, Item, RarityCategory


class CasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ("id", "name", "price")


class RarityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RarityCategory
        fields = ("rarity_id", "name")
        read_only_fields = ("rarity_id", "name")


class ItemListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    rarity_category = RarityCategorySerializer()

    class Meta:
        model = Item
        fields = ("item_id", "name", "price", "image", "rarity_category")
        read_only_fields = ("item_id", "name", "price", "image", "rarity_category")
