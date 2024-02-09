from django.urls import path
from core import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics",
        views.AdminAnalyticsViewSet.as_view({"get": "list"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/common_data",
        views.AdminAnalyticsViewSet.as_view({"get": "common_data"}),
    ),
    path("analytics", views.AnalyticsFooterView.as_view(), name="analytics_footer"),
]

urlpatterns += router.urls
