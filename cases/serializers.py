from rest_framework import serializers
from rest_framework import status
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

    def validate(self, attrs):
        super(UserItemSerializer, self).validate(attrs)
        if attrs["item"]:
            price = attrs["item"].price
            balance = attrs["user"].profile.balance
            if price > balance:
                raise serializers.ValidationError(
                    detail="Недостаточно средств", code=status.HTTP_406_NOT_ACCEPTABLE
                )
        return attrs

    def create(self, validated_data):
        user_item = super().create(validated_data)
        Calc.objects.create(
            user_id=user_item.user_id,
            balance=-user_item.item.price,
            debit=user_item.item.price - user_item.item.purchase_price,
            credit=-(user_item.item.price - user_item.item.purchase_price),
        )
        return user_item

    class Meta:
        model = UserItems
        fields = ("user", "item", "id")
        read_only_fields = ("id",)
