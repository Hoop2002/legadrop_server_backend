from django.urls import path
from users import views

urlpatterns = [
    path("sign_in", views.AuthViewSet.as_view({"post": "sign_in"}), name="sign_in"),
]
