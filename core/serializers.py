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
    total_crystal = serializers.IntegerField()


class AdminGenericSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericSettings
        fields = (
            "opened_cases_buff",
            "users_buff",
            "min_ref_output",
            "online_buff",
            "purchase_buff",
            "output_crystal_buff",
            "default_mark_up_case",
            "base_upgrade_percent",
            "minimal_price_upgrade",
            "base_upper_ratio",
            "notify_domain",
            "free_kassa_success_url",
            "free_kassa_failure_url",
            "email_verify_url_redirect",
            "email_verify_url",
            "telegram_verify_bot_token",
        )
