import json
from channels.generic.websocket import WebsocketConsumer


class LiveTapeConsumer(WebsocketConsumer):
    def connect(self):
        return super().connect()

    def disconnect(self, close_code):
        return super().disconnect(close_code)

    def receive(self, text_data):
        pass
