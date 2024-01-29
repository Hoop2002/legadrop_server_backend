from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, attrs):
        super().validate(attrs)
        password1 = attrs['password1']
        password2 = attrs['password2']
        if password1 != password2:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    class Meta:
        model = User
        fields = ("username", 'password1', 'password2', "email")


class UserProfileSignUpSerializer(serializers.ModelSerializer):
    user = UserSignUpSerializer()
    image = serializers.CharField()

    def validate(self, attrs):
        super().validate(attrs)
        username = attrs['user']['username']
        return attrs

    def create(self, validated_data):
        pass

    class Meta:
        model = UserProfile
        fields = ("user", "image")


class UserSignInSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "password")
