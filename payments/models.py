from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.functions import payment_order_id_generator, id_generator

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
    genshin_uid = models.CharField(max_length=16, null=True)

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"


class PromoCode(models.Model):
    BALANCE = "balance"
    BONUS = "bonus"
    PROMO_TYPES = ((BALANCE, "На баланс"), (BONUS, "Бонус к пополнению"))
    code_data = models.CharField(default=id_generator, unique=True, max_length=128)
    name = models.CharField(max_length=256, null=False)
    type = models.CharField(max_length=64, choices=PROMO_TYPES, null=False)
    summ = models.FloatField(verbose_name="Баланс", null=True, blank=True)
    percent = models.IntegerField(
        verbose_name="Процент",
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    limit_activations = models.IntegerField(
        verbose_name="Лимит активаций", null=True, blank=True
    )
    to_date = models.DateTimeField(verbose_name="Действует до", null=True, blank=True)

    def __str__(self):
        return f"{self.name}_{self.code_data}"

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"


class Calc(models.Model):
    """
    Модель начислений.
    debit -- поступление денег на сервис, не зависит откуда идут поступления, пополнение баланса или возврат средст
    credit -- Расход средств сервиса, когда делаем возврат пользователю или закупаем предметы
    balance -- Используется для расчёта начислений пользователя, как начальный баланс
    + balance -- пополнение баланса
    - balance -- списание с баланса

    Использование сочетания credit, debit и balance, при наличии credit и debit, они должны быть с разным знаком

    Описание структуры работы:
        - Пополнение баланса пользователем: credit + (наши нереализованные деньги) debit 0, balance + (учёт пользовательского баланса);
        - Покупка кейса: balance - (списание у пользователя стоимости кейса), debit = стоимость кейса - закупочная стоимость предмета выпавшего из кейса, credit = debit * -1;
        - Покупка предмета пользователем: balance - (списание у пользователя стоимости), debit = стоимость продажи предмета пользователю - закупочная стоимость. credit = debit * -1;
        - Вывод предмета пользователем с аккаунта: credit 0, debit = 0, потому что credit и так есть в остатке, делать ли запись? ;
    """

    calc_id = models.CharField(
        default=id_generator, unique=True, max_length=9, editable=False
    )
    debit = models.FloatField(verbose_name="Приход", null=False, default=0)
    credit = models.FloatField(verbose_name="Расход", null=False, default=0)
    balance = models.FloatField(
        verbose_name="Пользовательский баланс", null=False, default=0
    )
    order = models.ForeignKey(
        verbose_name="Оплата",
        to=PaymentOrder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="calc",
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="calc",
        related_query_name="calcs",
    )
    promo_code = models.ForeignKey(
        verbose_name="Промокод",
        to=PromoCode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="calc",
        related_query_name="calcs",
    )

    creation_date = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True
    )
    update_date = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"
