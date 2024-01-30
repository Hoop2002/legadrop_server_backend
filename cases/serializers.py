from rest_framework import serializers
from cases.models import Case, Item, RarityCategory
from users.models import UserItems
from payments.models import Calc


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


class UserItemSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user_item = super().create(validated_data)
        Calc.objects.create(user_id=user_item.user_id)
        return user_item

    class Meta:
        model = UserItems
        fields = ("user", "item", "id")
        read_only_fields = ("id",)
