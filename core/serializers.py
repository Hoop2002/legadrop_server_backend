from rest_framework import serializers
from core.models import GenericSettings


class AdminAnalyticsSerializer(serializers.Serializer):
    total_income = serializers.FloatField()
    total_expense = serializers.FloatField()
    profit = serializers.FloatField()
    count_users = serializers.IntegerField()


class AdminAnalyticsCommonData(serializers.Serializer):
    total_open = serializers.IntegerField()
    online = serializers.IntegerField()
    average_income = serializers.FloatField()
    ggr = serializers.FloatField()


class FooterSerializer(serializers.Serializer):
    opened_cases = serializers.IntegerField()
    total_users = serializers.IntegerField()
    users_online = serializers.IntegerField()
    total_purchase = serializers.IntegerField()
    total_outputs = serializers.IntegerField()


class AdminGenericSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericSettings
        fields = (
            "opened_cases_buff",
            "users_buff",
            "online_buff",
            "purchase_buff",
            "output_crystal_buff",
        )
