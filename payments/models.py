from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

from users.models import ActivatedPromo
from utils.functions import payment_order_id_generator, id_generator


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
    sum = models.DecimalField(default=0.0, decimal_places=2, max_digits=20)
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


class PromoCode(models.Model):
    BALANCE = "balance"
    BONUS = "bonus"
    PROMO_TYPES = ((BALANCE, "На баланс"), (BONUS, "Бонус к пополнению"))

    code_data = models.CharField(default=id_generator, unique=True, max_length=128)
    name = models.CharField(max_length=256, null=False)
    type = models.CharField(max_length=64, choices=PROMO_TYPES, null=False)
    active = models.BooleanField(verbose_name="Активен", default=True)
    summ = models.FloatField(verbose_name="Баланс", null=True, blank=True)
    limit_for_user = models.IntegerField(
        verbose_name="Количество активации на 1 пользователя", default=1
    )
    bonus_limit = models.IntegerField(
        verbose_name="Количество активаций бонуса на пользователя", default=1
    )
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def activate_promo(self, user: User) -> (str, bool):
        time = timezone.localdate()
        if not self.active or (self.to_date and self.to_date >= time):
            return "Промокод не действителен", False
        _activated = ActivatedPromo.objects.filter(user=user, promo=self).count()
        if _activated >= self.limit_for_user:
            return "Вы уже использовали этот промокод", False

        calc = None
        if self.type == self.BALANCE:
            calc = Calc.objects.create(user=user, credit=self.summ, balance=self.summ)
        activation = ActivatedPromo.objects.create(user=user, promo=self)
        activation.calc_promo.add(calc)
        activation.save()
        return "Успешно активирован", True

    @cached_property
    def activations(self) -> int:
        activations = ActivatedPromo.objects.filter(promo=self).count()
        return activations

    activations.short_description = "Количество активации"

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
        - Вывод предмета пользователем с аккаунта: credit 0, debit = 0, потому что credit и так есть в остатке, делать ли запись?;
        - Продажа предмета пользователем сервису: credit = (стоимость предмета * на коэф) - стоимость закупки, debit = credit * -1;
        ИЛИ если указана прямая стоимость продажи, то credit = (стоимость предмета - (стоимость предмета - стоимость продажи)) - стоимость закупки, debit = credit * -1;
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
    promo_using = models.ForeignKey(
        verbose_name="Промокод",
        to="users.ActivatedPromo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calc_promo",
    )

    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    creation_date = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True
    )
    update_date = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)

    def __str__(self):
        return f"Начисление {self.calc_id}"

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"
