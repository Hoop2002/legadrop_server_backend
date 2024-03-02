from celery import shared_task
from legaemail.models import SendMail
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def send_mails():
    mails = SendMail.objects.filter(active=True).all()

    if not mails:
        return "Нет сообщений"

    for mail in mails:

        if mail.type == mail.VERIFY:
            try:
                send_mail("LEGADROP VERIFY", mail.text, settings.EMAIL_ADMIN, [mail.to_email])
                mail.active = False
                mail.save()
            except:
                print(f"Ошибка {mail.id}")