from celery import shared_task
from django.utils import timezone

from users.models import UserVerify


@shared_task
def deactive_user_verified():
    verifieds = UserVerify.objects.filter(active=True).all()

    if not verifieds:
        return "Нет активных заявок на верификацию"

    for v in verifieds:
        time = timezone.localtime()
        if v.to_date <= time:
            v.active = False
            v.save()
