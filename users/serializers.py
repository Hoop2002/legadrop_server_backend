from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, Token

from users.models import UserProfile


class UserSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "password", "email")


class UserProfileSignUpSerializer(serializers.ModelSerializer):
    user = UserSignUpSerializer

    class Meta:
        model = UserProfile
        fields = ("user", "image")


class UserSignInSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "password")
