from django.urls import path
from users import views

urlpatterns = [
    path("sign_in", views.AuthViewSet.as_view({"post": "sign_in"}), name="auth"),
    path("sign_up", views.AuthViewSet.as_view({"post": "sign_up"}), name="auth"),
]
