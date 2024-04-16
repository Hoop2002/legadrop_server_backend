import redis
import time
import json

from django.utils import timezone
from django.conf import settings
from celery import shared_task
from cases.models import Contests, Item
from users.models import ContestsWinners, UserItems

from utils.decorators import single_task


@shared_task
@single_task(None)
def get_purchase_price_items():
    """Таска для получения закупочной цены предмета.
    Рассчитана на пересчёт раз в 5-10 минут
    """
    items = Item.objects.filter(removed=False)
    for item in items:
        item.purchase_price_cached = item.purchase_price
        item.save()


@shared_task
def get_winner_contest():
    """Таска должна бежать рвз в 10 секунд"""
    now = timezone.localtime()
    contests = Contests.objects.filter(
        next_start__lte=now,
        active=True,
        removed=False,
        current_award__isnull=False,
    ).distinct()

    if not contests:
        return "Нет активных конкурсов"
    for contest in contests:
        winner = contest.participants.order_by("?").first()
        ContestsWinners.objects.create(
            contest=contest, user=winner, item=contest.current_award
        )
        if winner is not None:
            UserItems.objects.create(
                user=winner, item=contest.current_award, contest=contest
            )
        contest.participants.set([])
        contest.set_new_award()
        contest.set_next_start(force=True)


@shared_task
def clear_live_tape():
    list_key = "live_tape"
    expire_time = 24 * 60 * 60
    current_time = time.time()

    r = redis.from_url(settings.REDIS_CONNECTION_STRING)

    items = r.lrange(list_key, 0, -1)

    if not items:
        return "Нет items в лайв ленте"

    for i in items:
        i_dict = json.loads(i.decode("utf-8"))
        element_timestamp = float(i_dict["timestamp"])
        if current_time - element_timestamp > expire_time:
            r.lrem(list_key, 0, i)
