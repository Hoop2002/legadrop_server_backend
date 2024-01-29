from django.db import models

# Create your models here.

from utils import payment_order_id_generator


class PaymentOrder(models.Model):
    UKASA = "yookassa"
    LAVA = "lava"

    CONDITION_TYPES_CHOICES = (
        (LAVA, "Платежная система ЛАВА(LAVA)"),
        (UKASA, "Платежная система ЮКасса(Yookassa)"),
    )
    order_id = models.CharField(max_length=128, default=payment_order_id_generator)
    sum = models.DecimalField(default=0.0, decimal_places=2, max_digits=17)
    type_payments = models.CharField(max_length=64, choices=CONDITION_TYPES_CHOICES)

    def __str__(self):
        return self.order_id 
    

    class Meta:
        verbose_name = 'Пополнение'
        verbose_name_plural = 'Пополнения'