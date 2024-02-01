from django.urls import path
from users import views

urlpatterns = [
    path("sign_in", views.AuthViewSet.as_view({"post": "sign_in"}), name="sign_in"),
    path("sign_up", views.AuthViewSet.as_view({"post": "sign_up"}), name="sign_up"),
    path("user", views.UserProfileViewSet.as_view({"get": "retrieve"}), name="user"),
    path(
        "user/update",
        views.UserProfileViewSet.as_view({"put": "update"}),
        name="update_user",
    ),
    path("user/items", views.UserItemsListView.as_view({'get': 'list'}), name="user_items_list"),
    path("user/item/sale/<int:pk>", views.UserItemsListView.as_view({'delete': 'destroy'}), name='sale_user_item')
]
