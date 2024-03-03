from django.conf import settings
from cases.serializers import ItemListSerializer
import redis 
import json
import threading
import time

def task(user, items):
    list_key = 'live_tape'
    redis_client = redis.from_url(settings.REDIS_CONNECTION_STRING)
    
    new_items = []

    for i in items:
        item = ItemListSerializer(i[0]).data
        item.update({"user_item_id": i[1].id})
        item.update({"user": {"id": user.id, "image": str(user.profile.image), "username": user.username}})
        item.update({"timestamp": time.time()})
        new_items.append(dict(item))

    for item in new_items:
        redis_client.rpush(list_key, json.dumps(item))


def write_items_in_redis(user, items):
    th = threading.Thread(target=task, args=(user, items))
    th.start()