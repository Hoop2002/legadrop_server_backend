from django.urls import path
from payments import views
from rest_framework import routers
from django.conf import settings

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
router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/ref_links",
    views.AdminRefLinkViewSet,
    basename="ref_links_admin",
)
router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/ref_outputs",
    views.AdminRefOutputViewSet,
    basename="admin_refoutputs",
)
router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/purchase",
    viewset=views.AdminPurchaseViewSet,
    basename="purchase",
)


router.register("payments", views.UserPaymentOrderViewSet, basename="user_payments")
router.register("outputs", views.UserOutputsViewSet, basename="user_outputs")
router.register("ref_output", views.UserRefOutputViewSet, basename="user_ref_outputs")
router.register("promo", views.PromoViewSet, basename="user_promo")

router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/moogold",
    viewset=views.AdminBalanceInMoogoldViewSet,
    basename="moogold_balance",
)

urlpatterns = [
    path(
        f"{settings.FREEKASSA_NOTIFY_PREFIX}/freekassa/notification",
        views.AdminFreekassaNotifyViewSet.as_view({"post": "notification"}),
    ),
    path(
        "ref/<str:code_data>",
        views.RefLinksViewSet.as_view({"get": "ref_link"}),
        name="ref_link",
    ),
]

urlpatterns += router.urls
