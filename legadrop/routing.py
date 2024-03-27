from django.urls import path
from users.consumers import OnlineUsersConsumer
from cases.consumers import LiveTapeConsumer

websocket_urlpatterns = [
    path("ws/online", OnlineUsersConsumer.as_asgi()),
    path("ws/live", LiveTapeConsumer.as_asgi()),
]
