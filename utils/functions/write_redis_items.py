from django.conf import settings
from cases.serializers import ItemListSerializer, CaseLive
from core.models import GenericSettings
import redis
import json
import threading
import time


def task(user, items, case):
    list_key = "live_tape"
    redis_client = redis.from_url(settings.REDIS_CONNECTION_STRING)

    generic = GenericSettings.objects.first()

    new_items = []

    for i in items:
        item = ItemListSerializer(i[0]).data
        item.update(
            {
                "image": (
                    "https://" + generic.domain_url + item.get("image")
                    if item.get("image", False)
                    else None
                )
            }
        )
        item.update({"user_item_id": i[1].id})
        item.update(
            {
                "user": {
                    "id": user.profile.id,
                    "image": "https://"
                    + generic.domain_url
                    + "/media/"
                    + str(user.profile.image),
                    "username": user.username,
                }
            }
        )
        if case:

            open_case = CaseLive(case).data
            open_case.update(
                {
                    "image": (
                        "https://" + generic.domain_url + open_case.get("image")
                        if open_case.get("image", False)
                        else None
                    )
                }
            )
            item.update({"open_case": open_case})
        else:
            item.update({"open_case": None})

        item.update({"timestamp": time.time()})
        new_items.append(dict(item))

    for item in new_items:
        redis_client.rpush(list_key, json.dumps(item))


def write_items_in_redis(user, items, case):
    th = threading.Thread(target=task, args=(user, items, case))
    th.start()
