from django.urls import include, path
from rest_framework import routers

from cases import views


router = routers.DefaultRouter()

# router.register(viewset=views.CasesViewSet, prefix="cases")

urlpatterns = [
    path("cases", views.CasesViewSet.as_view({"get": "list"})),
    path("shop/items", views.ItemsViewSet.as_view({"get": "list"})),
]
