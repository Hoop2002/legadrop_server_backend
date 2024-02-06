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

urlpatterns = [
    path(
        "payments/",
        views.UserPaymentOrderViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/payments/approval",
        views.ApprovalAdminPaymentOrderViewSet.as_view({"post": "approval"}),
    ),
    path(
        "payments/<str:order_id>",
        views.UserPaymentOrderViewSet.as_view({"get": "retrieve"}),
    ),
    path("promo/activate", views.PromoViewSet.as_view({"post": "activate"})),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics",
        views.AdminAnalyticsViewSet.as_view({"get": "list"}),
    ),
]

urlpatterns += router.urls
