from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from users.models import UserProfile
from utils import Base64ImageField


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate(self, attrs):
        super().validate(attrs)
        password1 = attrs["password1"]
        password2 = attrs["password2"]
        if password1 != password2:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        _user = User.objects.filter(username=attrs["username"]).exists()
        if _user:
            raise serializers.ValidationError(
                {"username": "Пользователь с таким логином уже зарегистрирован"}
            )
        return attrs

    class Meta:
        model = User
        fields = ("id", "username", "password1", "password2", "email")


class UserSerializer(UserCreateSerializer):
    username = serializers.CharField(required=False)
    password1 = serializers.CharField(required=False, write_only=True)
    password2 = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        try:
            super().validate(attrs)
        except serializers.ValidationError as err:
            print(err)


class UserProfileCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    token = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_token(instance):
        return str(AccessToken.for_user(instance.user))

    def create(self, validated_data):
        validated_data["user"].pop("password1")
        password = validated_data["user"].pop("password2")
        validated_data["user"]["password"] = password
        user = User.objects.create(**validated_data["user"])
        user.set_password(password)
        user.save()
        validated_data["user"] = user
        profile = UserProfile.objects.create(**validated_data)
        return profile

    class Meta:
        model = UserProfile
        fields = ("user", "token", "locale")


class UserSignInSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "password")


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    image = Base64ImageField(required=False, max_length=None, use_url=True)
    verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("user", "image", "locale", "verified")
