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
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/income/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_income"}),
        name="admin_analytics_income",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/outlay/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_outlay"}),
        name="admin_analytics_outlay",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/clear_profit/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_clear_profit"}),
        name="admin_analytics_clear_profit",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/count_open_cases/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_count_open_cases"}),
        name="admin_analytics_count_open_cases",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/average_check/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_average_check"}),
        name="admin_analytics_average_check",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/count_reg_users/<str:start_date>/<str:end_date>",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_count_reg_users"}),
        name="admin_analytics_count_reg_users",
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/analytics/graphics/income_by_cases/<str:date>/",
        views.AdminAnalyticsViewSet.as_view({"get": "graphic_income_by_case_type"}),
        name="admin_analytics_income_by_case",
    ),
    path("analytics", views.AnalyticsFooterView.as_view(), name="analytics_footer"),
]

urlpatterns += router.urls
