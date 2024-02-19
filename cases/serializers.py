from django.utils import timezone
from rest_framework import serializers
from rest_framework import status
from cases.models import Case, Item, RarityCategory, Category, ConditionCase, Contests
from users.models import UserItems, ContestsWinners
from payments.models import Calc

from utils.fields import Base64ImageField


class ConditionSerializer(serializers.ModelSerializer):
    type_condition = serializers.ChoiceField(
        choices=ConditionCase.CONDITION_TYPES_CHOICES
    )
    time = serializers.TimeField(
        required=False,
        allow_null=True,
        default="",
    )
    time_reboot = serializers.TimeField(
        required=False,
        default="24:00:00",
    )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = ConditionCase
        fields = (
            "condition_id",
            "name",
            "description",
            "type_condition",
            "price",
            "time",
            "time_reboot",
        )
        read_only_fields = ("condition_id",)


class RarityCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = RarityCategory
        fields = ("rarity_id", "name", "rarity_color")
        read_only_fields = ("name", "rarity_id", "rarity_color")


class RarityCategoryAdminSerializer(RarityCategorySerializer):
    class Meta:
        model = RarityCategory
        fields = RarityCategorySerializer.Meta.fields


class ItemListSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(max_length=9)
    image = serializers.ImageField(use_url=True, read_only=True)
    rarity_category = RarityCategorySerializer(read_only=True)

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


class ItemsAdminSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(required=True)
    purchase_price = serializers.FloatField(required=True)
    image = Base64ImageField(
        required=False, max_length=None, use_url=True, allow_null=True
    )
    rarity_category = RarityCategorySerializer(read_only=True)
    rarity_category_id = serializers.CharField(max_length=9, write_only=True)
    step_down_factor = serializers.FloatField(default=1, required=False)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = Item
        fields = (
            "id",
            "item_id",
            "name",
            "price",
            "purchase_price",
            "sale_price",
            "percent_price",
            "sale",
            "image",
            "created_at",
            "updated_at",
            "step_down_factor",
            "rarity_category",
            "rarity_category_id",
        )
        read_only_fields = ("id", "created_at", "updated_at", "rarity_category")
        write_only_fields = ("rarity_category_id",)


class CaseCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("category_id", "name")
        read_only_fields = ("name",)


class ListCasesSerializer(serializers.ModelSerializer):
    category = CaseCategorySerializer()

    class Meta:
        model = Case
        fields = ("translit_name", "name", "price", "case_free", "image", "category")


class ListCaseItemsSerializer(ItemListSerializer):
    percent = serializers.SerializerMethodField()

    def get_percent(self, instance) -> float:
        count = (
            self.context["view"]
            .queryset.first()
            .items.filter(rarity_category=instance.rarity_category)
            .count()
        )
        item_percent = (
            instance.rarity_category.category_percent / count
            + instance.step_down_factor
        )
        return item_percent

    class Meta:
        model = Item
        fields = ItemListSerializer.Meta.fields + ("percent",)


class CaseSerializer(serializers.ModelSerializer):
    items = ListCaseItemsSerializer(many=True)

    class Meta:
        model = Case
        fields = (
            "translit_name",
            "name",
            "price",
            "case_free",
            "image",
            "category",
            "items",
        )


class ListConditionSerializer(serializers.ModelSerializer):
    condition_id = serializers.CharField(max_length=9)

    class Meta:
        model = ConditionCase
        fields = ("condition_id", "name", "type_condition")
        read_only_fields = ("name", "type_condition")


class AdminCasesSerializer(ListCasesSerializer):
    name = serializers.CharField(max_length=256)
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    category = CaseCategorySerializer(read_only=True)
    category_id = serializers.CharField(max_length=9, write_only=True)
    items = ItemListSerializer(many=True, read_only=True)
    conditions = ListConditionSerializer(many=True, read_only=True)
    item_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True
    )
    condition_ids = serializers.ListSerializer(
        child=serializers.CharField(), write_only=True, required=False
    )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    def create(self, validated_data):
        if "condition_ids" in validated_data:
            condition_ids = validated_data.pop("condition_ids")
            conditions = ConditionCase.objects.filter(condition_id__in=condition_ids)
            validated_data["conditions"] = conditions

        # item обязательные, поэтому не ставим проверку
        item_ids = validated_data.pop("item_ids")
        items = Item.objects.filter(item_id__in=item_ids)
        validated_data["items"] = items

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "condition_ids" in validated_data:
            condition_ids = validated_data.pop("condition_ids")
            conditions = ConditionCase.objects.filter(condition_id__in=condition_ids)
            validated_data["conditions"] = conditions

        if "item_ids" in validated_data:
            item_ids = validated_data.pop("item_ids")
            items = Item.objects.filter(item_id__in=item_ids)
            validated_data["items"] = items
        return super().update(instance, validated_data)

    class Meta:
        model = Case
        fields = (
            "case_id",
            "name",
            "translit_name",
            "active",
            "image",
            "price",
            "case_free",
            "category",
            "category_id",
            "items",
            "item_ids",
            "conditions",
            "condition_ids",
            "created_at",
            "updated_at",
        )


class ContestsSerializer(serializers.ModelSerializer):
    time_start = serializers.DateTimeField(source="next_start")
    current_award = ItemListSerializer()
    count_participants = serializers.SerializerMethodField()
    last_winner = serializers.SerializerMethodField()
    conditions = serializers.SerializerMethodField()

    def get_count_participants(self) -> int:
        return self.instance.participants.count()

    def get_last_winner(self):
        return self.instance.winners.order_by("pk").last()

    def get_conditions(self) -> list[str]:
        return self.instance.conditions.value_list("description", flat=True)

    class Meta:
        model = Contests
        fields = (
            "contest_id",
            "name",
            "time_start",
            "current_award",
            "count_participants",
            "last_winner",
            "conditions",
        )


class AdminContestsSerializer(serializers.ModelSerializer):
    current_award_id = serializers.CharField(write_only=True)
    timer = serializers.DurationField(help_text="Формат: дни часы:минуты:секунды")

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = Contests
        fields = (
            "contest_id",
            "name",
            "timer",
            "active",
            "one_time",
            "items",
            "current_award",
            "current_award_id",
            "participants",
            "conditions",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "contest_id",
            "items",
            "participants",
            "created_at",
            "updated_at",
        )
