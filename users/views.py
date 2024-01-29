from django.contrib.auth import authenticate, login
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.response import Response

from users.models import UserProfile
from users.serializers import UserProfileSignUpSerializer, UserSignInSerializer


class AuthViewSet(ModelViewSet):
    queryset = UserProfile.objects

    def get_serializer_class(self):
        serializers = {
            "sign_up": UserProfileSignUpSerializer,
            "sign_in": UserSignInSerializer,
        }
        return serializers.get(self.action)

    def sign_up(self, request, *args, **kwargs):
        pass

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
        return Response({"message": message})
