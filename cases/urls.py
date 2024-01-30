from django.urls import path

from cases import views


urlpatterns = [
    path("cases", views.CasesViewSet.as_view({"get": "list"})),
    path("shop/items", views.ShopItemsViewSet.as_view({"get": "list"})),
    path(
        "shop/items/<str:item_id>", views.ShopItemsViewSet.as_view({"get": "retrieve"})
    ),
]
