from django.utils import timezone

from celery import shared_task
from cases.models import Contests
from users.models import ContestsWinners, UserItems


@shared_task
def get_winner_contest():
    """Таска должна бежать рвз в 10 секунд"""
    now = timezone.localtime()
    contests = Contests.objects.filter(
        next_start__lte=now,
        active=True,
        removed=False,
        current_award__isnull=False,
        participants__isnull=False,
    ).distinct()

    if not contests:
        return "Нет активных конкурсов"
    for contest in contests:
        winner = contest.participants.order_by("?").first()
        ContestsWinners.objects.create(
            contest=contest, user=winner, item=contest.current_award
        )
        UserItems.objects.create(
            user=winner, item=contest.current_award, contest=contest
        )
        contest.participants.set([])
        contest.set_new_award()
        contest.set_next_start(force=True)
