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
    r"6383d341-4d14-4868-81ba-3c6382f2128e/category",
    views.AdminCategoryViewSet,
    basename="admin_category",
)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/conditions",
    views.AdminConditionsViewSet,
    basename="admin_case_conditions",
)
router.register(
    "6383d341-4d14-4868-81ba-3c6382f2128e/contest",
    views.AdminContestViewSet,
    basename="admin_contest",
)

router.register("cases", views.CasesViewSet, basename="cases")


urlpatterns = [
    path(
        "cases/<str:translit_name>/open_case/<int:count>",
        views.CasesViewSet.as_view({"post": "open_case"}),
        name="cases",
    ),
    path(
        "contests/",
        views.ContestsViewSet.as_view({"get": "list"}),
        name="contests_list",
    ),
    path(
        "contests/<contest_id>/",
        views.ContestsViewSet.as_view({"post": "participate"}),
        name="participate",
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
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/recommendation/crystals/<int:crystal_castles>",
        views.ItemAdminViewSet.as_view({"get": "get_crystal_count_recommendation"}),
        name="crystal_count_recommendation",
    ),
]

urlpatterns += router.urls
