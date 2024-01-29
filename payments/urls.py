from django.urls import include, path
from payments import views

urlpatterns = [path("", views.UserPaymentOrderViewSet.as_view({"get": "list"}))]