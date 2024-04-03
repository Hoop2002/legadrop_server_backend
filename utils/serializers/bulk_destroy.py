from rest_framework import serializers


class BulkDestroySerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())


class BulkDestroyIntSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
