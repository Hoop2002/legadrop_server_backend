from channels.generic.websocket import AsyncWebsocketConsumer


class OnlineUsersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "online_users"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        await self.send(text_data)
