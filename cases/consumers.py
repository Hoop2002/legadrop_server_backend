from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import asyncio
import aioredis
import json

class LiveTapeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        return super().disconnect(close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if not data.get("action", False):
            await self.send(json.dumps({"message": "error, not found 'action'"}))
            return


        r = aioredis.from_url(settings.REDIS_CONNECTION_STRING)

        list_key = 'live_tape'

        if data["action"] == "get_items":
            items = list(reversed([json.loads(i.decode("utf-8")) for i in await r.lrange(list_key, -19, -1)]))
            await self.send(text_data=json.dumps(items))
            return
        
        if data["action"] == "get_luxury_item":
            items = list(reversed([json.loads(i.decode("utf-8")) for i in await r.lrange(list_key, 0, -1)]))
            items = sorted(items, key=lambda x: x['price'], reverse=True)
            if not items:
                await self.send(text_data=json.dumps({"message": "item not found"}))
                return
            luxury_item = items[0]
            await self.send(text_data=json.dumps(luxury_item))
            return