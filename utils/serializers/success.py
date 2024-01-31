from rest_framework import serializers


class SuccessSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
