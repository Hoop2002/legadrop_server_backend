from django.urls import include, path
from payments import views
from rest_framework import routers

# router = routers.SimpleRouter()

# router.register('payments', views.UserPaymentOrderViewSet)

urlpatterns = [
    path(
        "payments/",
        views.UserPaymentOrderViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "payments/<str:order_id>",
        views.UserPaymentOrderViewSet.as_view({"get": "retrieve"}),
    ),
]
