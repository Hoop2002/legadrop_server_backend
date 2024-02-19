from rest_framework import serializers

from payments.models import PaymentOrder, PromoCode, Calc, Output, RefLinks
from payments.manager import PaymentManager

from users.serializers import AdminUserListSerializer, UserItemSerializer


class UserPaymentOrderSerializer(serializers.ModelSerializer):
    type_payments = serializers.ChoiceField(choices=PaymentOrder.PAYMENT_TYPES_CHOICES)

    class Meta:
        model = PaymentOrder
        fields = (
            "order_id",
            "email",
            "type_payments",
            "sum",
            "include_service_lava",
            "lava_link",
            "status",
            "created_at",
            "active",
        )
        read_only_fields = ("order_id", "status", "active")

    def create(self, vals):
        data = vals
        data.update({"user": self.context["request"].user})
        manager = PaymentManager()
        if data["type_payments"] == "lava":
            order = manager._create_lava_payment_order(data)
        return order


class ActivatePromoCodeSerializer(serializers.ModelSerializer):
    code_data = serializers.CharField(validators=[], write_only=True)

    def validate(self, attrs):
        if "code_data" in attrs:
            if PromoCode.objects.filter(code_data=attrs["code_data"]).exists():
                return attrs
        raise serializers.ValidationError("Нет такого промокода")

    class Meta:
        model = PromoCode
        fields = ("code_data",)


class AdminPaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"


class AdminListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Output
        fields = ("id", "output_id", "type", "status")


class AdminOutputSerializer(AdminListOutputSerializer):
    class Meta:
        model = Output
        fields = "__all__"


class UserListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Output
        fields = (
            "id",
            "output_id",
            "status",
            "created_at",
        )

class UserItemsCreateOutputSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(source="item.item_id")

class UserCreateOutputSerializer(serializers.ModelSerializer):
    output_items = UserItemsCreateOutputSerializer(many=True)

    def validate(self, attrs):
        user = self.context.get("request").user

        items = user.items.all()
        items_ids = [i.id for i in items]

        if not "output_items" in attrs: 
            raise serializers.ValidationError("Не выбраны предметы")
        if not "player_id" in attrs:
            raise serializers.ValidationError("Необходимо указать \"player_id\"")

        if not attrs['output_items']:
            raise serializers.ValidationError("Не выбраны предметы")

        for i in attrs['output_items']:
            if not i['item']['item_id'] in items_ids:
                raise serializers.ValidationError("Нет такого предмета в инвентаре")
            
            item = items.filter(id=i['item']['item_id']).get()

            if item.withdrawn or item.withdrawal_process:
                raise serializers.ValidationError("Предмет выведен или находится в процессе вывода")
            if not item.active:
                raise serializers.ValidationError("Предмет отсутствует на аккаунте")

        return attrs
    
    class Meta:
        model = Output
        fields = (
            "player_id",
            "comment",
            "output_items",
        )

class UserOutputSerializer(serializers.ModelSerializer):
    output_items = UserItemSerializer(many=True)

    class Meta:
        model = Output
        fields = (
            "id",
            "output_id",
            "player_id",
            "comment",
            "status",
            "created_at",
            "active",
            "output_items",
        )


class AdminListPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ("id", "name", "type", "code_data")


class AdminPromoCodeSerializer(AdminListPromoSerializer):
    type = serializers.ChoiceField(choices=PromoCode.PROMO_TYPES)
    percent = serializers.IntegerField(
        min_value=0, max_value=100, required=False, default=0
    )
    summ = serializers.FloatField(required=False)
    to_date = serializers.DateTimeField(required=False)
    limit_activations = serializers.IntegerField(required=False)
    code_data = serializers.CharField(max_length=128, required=False)
    limit_for_user = serializers.IntegerField(required=False, default=1)
    bonus_limit = serializers.IntegerField(required=False, default=1)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "method", None) == "PUT":
            for field in fields:
                fields[field].required = False
        return fields

    class Meta:
        model = PromoCode
        fields = (
            "id",
            "name",
            "type",
            "code_data",
            "active",
            "activations",
            "summ",
            "percent",
            "limit_activations",
            "limit_for_user",
            "bonus_limit",
            "to_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "activations")


class CalcsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calc
        fields = ("user_id", "debit", "credit", "created_at")


class RefLinksAdminSerializer(serializers.ModelSerializer):
    from_user = AdminUserListSerializer(read_only=True)

    class Meta:
        model = RefLinks
        fields = ("code_data", "from_user", "active", "created_at")
