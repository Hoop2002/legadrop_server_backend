from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("username", "password", "email")


class UserProfileSignUpSerializer(serializers.ModelSerializer):
    user = UserSignUpSerializer()
    image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ("user", "image")


class UserSignInSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "password")
