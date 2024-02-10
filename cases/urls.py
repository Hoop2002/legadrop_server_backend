from django.urls import path
from rest_framework import routers

from cases import views


router = routers.DefaultRouter()
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/items",
    views.ItemAdminViewSet,
    basename="admin_items",
)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/rarity_category",
    views.AdminRarityCategoryViewSet,
    basename="admin_rarity_category",
)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/cases",
    views.AdminCasesViewSet,
    basename="admin_cases",
)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/case_conditions",
    views.AdminCaseConditionsViewSet,
    basename="admin_case_conditions",
)


urlpatterns = [
    path("cases", views.CasesViewSet.as_view({"get": "list"}), name="cases_list"),
    path(
        "case/<str:translit_name>",
        views.CasesViewSet.as_view({"get": "retrieve"}),
        name="case_detail",
    ),
    path(
        "case/<str:translit_name>/open",
        views.CasesViewSet.as_view({"post": "open_case"}),
        name="case_open",
    ),
    path(
        "shop/items",
        views.ShopItemsViewSet.as_view({"get": "list"}),
        name="shopitems_list",
    ),
    path(
        "shop/items/<str:item_id>",
        views.ShopItemsViewSet.as_view({"get": "retrieve"}, name="shopitems_detail"),
    ),
    path(
        "shop/buy/<str:item_id>",
        views.ShopItemsViewSet.as_view({"post": "buy_item"}, name="buy_item"),
    ),
]

urlpatterns += router.urls
