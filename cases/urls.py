from django.urls import path

from cases import views


urlpatterns = [
    path("cases", views.CasesViewSet.as_view({"get": "list"})),
    path("shop/items", views.ItemsViewSet.as_view({"get": "list"})),
]
