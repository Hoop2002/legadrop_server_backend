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


### graphics serializer ###


class AdminAnalyticsIncome(serializers.Serializer):
    income = serializers.FloatField()
    date = serializers.DateField()


class AdminAnalyticsOutlay(serializers.Serializer):
    outlay = serializers.FloatField()
    date = serializers.DateField()


class AdminAnalyticsClearProfit(serializers.Serializer):
    profit = serializers.FloatField()
    date = serializers.DateField()


class AdminAnalyticsCountOpenCases(serializers.Serializer):
    count = serializers.IntegerField()
    date = serializers.DateField()


class AdminAnalyticsAverageCheck(serializers.Serializer):
    check = serializers.FloatField()
    date = serializers.DateField()


class AdminAnalyticsCountRegUser(serializers.Serializer):
    count = serializers.IntegerField()
    date = serializers.DateField()


class AdminAnalyticsIncomeByCaseType(serializers.Serializer):
    case_name = serializers.CharField()
    count_open = serializers.IntegerField()
    income = serializers.FloatField()
    date = serializers.DateField()


### blocks serializer ###


class AdminAnalyticsTopRef(serializers.Serializer):
    name = serializers.CharField()
    image = serializers.CharField()


class AdminAnalyticsTopUsersDeposite(serializers.Serializer):
    name = serializers.CharField()
    image = serializers.CharField()


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
