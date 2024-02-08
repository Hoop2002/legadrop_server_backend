from rest_framework import serializers


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
