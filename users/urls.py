from django.urls import path
from users import views

urlpatterns = [
    path("get_token", views.AuthViewSet.as_view({'get': 'get_token'}), name="get_token"),
    path("sign_in", views.AuthViewSet.as_view({"post": "sign_in"}), name="sign_in"),
    path("sign_up", views.AuthViewSet.as_view({"post": "sign_up"}), name="sign_up"),
    path(
        "sign_in/google",
        views.AuthViewSet.as_view({"post": "sign_in_google"}),
        name="sign_up_google",
    ),
    path(
        "sign_in/vk",
        views.AuthViewSet.as_view({"post": "sign_in_vk"}),
        name="sign_up_vk",
    ),
    path("user", views.UserProfileViewSet.as_view({"get": "retrieve"}), name="user"),
    path(
        "user/update",
        views.UserProfileViewSet.as_view({"put": "update"}),
        name="update_user",
    ),
    path(
        "user/items",
        views.UserItemsListView.as_view({"get": "list"}),
        name="user_items_list",
    ),
    path(
        "user/items/history",
        views.UserItemsListView.as_view({"get": "items_history"}),
        name="user_items_history",
    ),
    path(
        "user/item/sale/<int:pk>",
        views.UserItemsListView.as_view({"delete": "destroy"}),
        name="sale_user_item",
    ),
    path("user/genshin_uid/", views.GetGenshinAccountView.as_view({"post": "get_uid"})),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/user/<int:user_id>/payments/",
        views.AdminUserPaymentHistoryViewSet.as_view({"get": "list"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/user/<int:user_id>/games/",
        views.AdminUserHistoryGamesViewSet.as_view({"get": "games"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/user/<int:user_id>/items/",
        views.AdminUserHistoryGamesViewSet.as_view({"get": "items"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/users/",
        views.AdminUsersViewSet.as_view({"get": "list"}),
    ),
    path(
        "6383d341-4d14-4868-81ba-3c6382f2128e/user/<int:user_id>/",
        views.AdminUsersViewSet.as_view({"get": "retrieve", "put": "update"}),
    ),
]
