from django.contrib.auth import authenticate, login
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema

from rest_framework.response import Response

from users.models import UserProfile
from users.serializers import UserProfileSignUpSerializer, UserSignInSerializer


@extend_schema(tags=["main"])
class AuthViewSet(ModelViewSet):
    queryset = UserProfile.objects
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        serializers = {
            "sign_up": UserProfileSignUpSerializer,
            "sign_in": UserSignInSerializer,
        }
        return serializers.get(self.action)

    def sign_up(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = self.get_serializer(user)
            return Response(response.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    def sign_in(self, request, *args, **kwargs):
        username = self.request.data.get("username")
        password = self.request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            token = AccessToken.for_user(user)
            return Response(str(token))
        message = (
            "Пожалуйста, введите корректные имя пользователя и"
            " пароль учётной записи. Оба поля могут быть чувствительны"
            " к регистру."
        )
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
