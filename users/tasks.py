from celery import shared_task
from django.utils import timezone

from users.models import UserVerify, UserProfile
from utils.decorators import single_task


@shared_task
@single_task(None)
def save_profile_data():
    profiles = UserProfile.objects.filter(user__is_active=True)
    for profile in profiles:
        profile.balance_save = profile.balance
        profile.winrate_save = profile.winrate
        profile.debit_save = profile.all_debit()
        profile.output_save = profile.all_output()
        profile.save()


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
