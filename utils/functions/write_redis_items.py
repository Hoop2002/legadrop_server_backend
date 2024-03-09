from django.conf import settings
from cases.serializers import ItemListSerializer
import redis
import json
import threading
import time


def task(user, items, case):
    list_key = "live_tape"
    redis_client = redis.from_url(settings.REDIS_CONNECTION_STRING)

    new_items = []

    for i in items:
        item = ItemListSerializer(i[0]).data
        item.update({"user_item_id": i[1].id})
        item.update(
            {
                "user": {
                    "id": user.profile.id,
                    "image": str(user.profile.image),
                    "username": user.username,
                }
            }
        )
        if case:
            item.update({"open_case": {"name": case.name, "translit_name": case.translit_name, "image": str(case.image)}})
        else:
            item.update({"open_case": None})
        
        item.update({"timestamp": time.time()})
        new_items.append(dict(item))

    for item in new_items:
        redis_client.rpush(list_key, json.dumps(item))


def write_items_in_redis(user, items, case):
    th = threading.Thread(target=task, args=(user, items, case))
    th.start()
