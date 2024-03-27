from django.urls import path
from users.consumers import OnlineUsersConsumer

websocket_urlpatterns = [
    path("ws/online/", OnlineUsersConsumer.as_asgi()),
]
