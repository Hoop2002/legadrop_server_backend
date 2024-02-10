from django.urls import path
from rest_framework import routers

from cases import views


router = routers.DefaultRouter()
router.register(r"6383d341-4d14-4868-81ba-3c6382f2128e/items", views.ItemAdminViewSet)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/rarity_category",
    views.AdminRarityCategoryViewSet,
)
router.register(r"6383d341-4d14-4868-81ba-3c6382f2128e/cases", views.AdminCasesViewSet)
router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/case_conditions",
    views.AdminCaseConditionsViewSet,
)


urlpatterns = [
    path("cases", views.CasesViewSet.as_view({"get": "list"})),
    path("case/<str:translit_name>", views.CasesViewSet.as_view({"get": "retrieve"})),
    path(
        "case/<str:translit_name>/open", views.CasesViewSet.as_view({"post": "open_case"})
    ),
    path("shop/items", views.ShopItemsViewSet.as_view({"get": "list"})),
    path(
        "shop/items/<str:item_id>", views.ShopItemsViewSet.as_view({"get": "retrieve"})
    ),
    path(
        "shop/buy/<str:item_id>", views.ShopItemsViewSet.as_view({"post": "buy_item"})
    ),
]

urlpatterns += router.urls
