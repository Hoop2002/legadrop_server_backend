from django.urls import path
from payments import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/promo", views.AdminPromoCodeViewSet
)

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/payments", views.AdminPaymentOrderViewSet
)
router.register("payments", views.UserPaymentOrderViewSet)

urlpatterns = [
    path("promo/activate", views.PromoViewSet.as_view({"post": "activate"})),
]

urlpatterns += router.urls
