from django.urls import path
from payments import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/promo",
    views.AdminPromoCodeViewSet,
    basename="admin_promo",
)

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/output",
    views.AdminOutputsViewSet,
    basename="admin_output",
)

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/payments",
    views.AdminPaymentOrderViewSet,
    basename="admin_payments",
)
router.register("payments", views.UserPaymentOrderViewSet, basename="user_payments")
router.register("promo", views.PromoViewSet, basename="user_promo")

urlpatterns = [
    path(
        "ref/<str:code_data>",
        views.RefLinksViewSet.as_view({"get": "ref_link"}),
        name="ref_link",
    ),
]

urlpatterns += router.urls
