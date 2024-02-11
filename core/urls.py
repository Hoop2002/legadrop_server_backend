from django.urls import path
from core import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    r"6383d341-4d14-4868-81ba-3c6382f2128e/generic_settings",
    views.GenericSettingsViewSet,
    basename="generic_settings",
)

urlpatterns = [
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics",
        views.AdminAnalyticsViewSet.as_view({"get": "list"}),
        name="admin_analytics_computed",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/common_data",
        views.AdminAnalyticsViewSet.as_view({"get": "common_data"}),
        name="admin_analytics_common",
    ),
    path("analytics", views.AnalyticsFooterView.as_view(), name="analytics_footer"),
]

urlpatterns += router.urls
