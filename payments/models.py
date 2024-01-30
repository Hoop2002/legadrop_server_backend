from django.db import models

from utils.functions import payment_order_id_generator

from django.contrib.auth.models import User


class PaymentOrder(models.Model):
    UKASA = "yookassa"
    LAVA = "lava"

    PAYMENT_TYPES_CHOICES = (
        (LAVA, "Платежная система ЛАВА(LAVA)"),
        (UKASA, "Платежная система ЮКасса(Yookassa)"),
    )

    CREATE = "create"
    EXPIRED = "expired"
    SUCCESS = "success"

    STATUS_TYPE_CHOICES = (
        (CREATE, "Создан"),
        (EXPIRED, "Отменен"),
        (SUCCESS, "Оплачен"),
    )

    order_id = models.CharField(max_length=128, default=payment_order_id_generator)
    sum = models.DecimalField(default=0.0, decimal_places=2, max_digits=17)
    type_payments = models.CharField(max_length=64, choices=PAYMENT_TYPES_CHOICES)

    lava_id = models.CharField(max_length=256, null=True)
    lava_link = models.CharField(max_length=512, null=True)
    lava_expired = models.DateTimeField(null=True)
    project_lava = models.CharField(max_length=256, null=True)
    project_lava_name = models.CharField(max_length=64, null=True)
    include_service_lava = models.CharField(max_length=128, null=True)

    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_payments_orders",
    )

    status = models.CharField(
        max_length=128, choices=STATUS_TYPE_CHOICES, default=CREATE
    )
    status_lava_num = models.IntegerField(default=1)
    email = models.EmailField(default="test@example.com")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"
