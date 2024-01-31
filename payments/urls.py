from django.urls import path
from payments import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/promo", views.AdminPromoCodeViewSet
)

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

urlpatterns += router.urls
