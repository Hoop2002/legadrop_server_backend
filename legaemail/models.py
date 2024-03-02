from django.db import models


class SendMail(models.Model):
    TEST = "test"
    VERIFY = "verify"

    TYPE_CHOICE = ((TEST, "Тест (не использовать)"), (VERIFY, "Верификация"))

    type = models.CharField(verbose_name="Тип сообщения", max_length=256, choices=TYPE_CHOICE)
    to_email = models.CharField(verbose_name="Имэйл получателя", max_length=256)
    active = models.BooleanField(verbose_name="Активно", default=True)
    text = models.TextField()
