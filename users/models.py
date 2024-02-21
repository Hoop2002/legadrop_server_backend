from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.functional import cached_property

from cases.models import Item, Case
from utils.functions import generate_upload_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(
        upload_to=generate_upload_name,
        verbose_name="Фотография пользователя",
        null=True,
        blank=True,
    )
    locale = models.CharField(verbose_name="Локаль", max_length=8, default="ru")
    verified = models.BooleanField(verbose_name="Верифицирован", default=False)
    individual_percent = models.FloatField(
        verbose_name="Индивидуальный процент", default=1
    )
    demo = models.BooleanField(verbose_name="Демо пользователь", default=False)
    partner_percent = models.FloatField(
        verbose_name="Бонус с реферальной ссылки",
        default=1.03,
        validators=[MinValueValidator(1), MaxValueValidator(2)],
    )
    partner_income = models.FloatField(
        verbose_name="Доход с пополнения по реферальной ссылке",
        default=0.03,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    withdrawal_is_allowed = models.BooleanField(
        verbose_name="Разрешение на вывод", default=True
    )

    @cached_property
    def winrate(self) -> float:
        win = self.user.opened_cases.filter(win=True).count()
        all_opened = self.user.opened_cases.count()
        if not all_opened:
            return 0
        winrate = win / all_opened
        return winrate

    @cached_property
    def balance(self) -> float:
        balance = self.user.calc.filter(demo=self.demo).aggregate(
            models.Sum("balance")
        )["balance__sum"]
        if balance is None:
            return 0
        return balance

    @cached_property
    def total_income(self) -> float:
        links = self.ref_links.filter(active=True, removed=False)
        activated = ActivatedLinks.objects.filter(bonus_using=True, link__in=links)
        amounts = activated.aggregate(
            debit=models.Sum("calc_link__debit"), credit=models.Sum("calc_link__credit")
        )
        service_credit = amounts["credit"] or 0
        service_debit = amounts["debit"] or 0
        income = (service_credit + service_debit) * self.partner_income
        return round(float(income), 2)

    def all_debit(self) -> float:
        from payments.models import Calc, PaymentOrder

        debit = PaymentOrder.objects.filter(
            user=self.user, status__in=[PaymentOrder.SUCCESS, PaymentOrder.APPROVAL]
        ).aggregate(models.Sum("sum"))["sum__sum"]
        return debit or 0

    def __str__(self):
        return self.user.username


class UserItems(models.Model):
    from_case = models.BooleanField(verbose_name="Выпал из кейса", default=False)
    case = models.ForeignKey(
        verbose_name="Кейс",
        to=Case,
        to_field="case_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_items",
    )

    active = models.BooleanField(verbose_name="Есть на аккаунте", default=True)
    withdrawn = models.BooleanField(verbose_name="Выведен с аккаунта", default=False)
    withdrawal_process = models.BooleanField(
        verbose_name="Находится в процессе вывода", default=False
    )

    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        related_name="items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    item = models.ForeignKey(
        verbose_name="Предмет",
        to=Item,
        related_name="user_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    calc = models.ForeignKey(
        verbose_name="Начисление",
        to="payments.Calc",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="saled_items",
    )
    contest = models.ForeignKey(
        verbose_name="Конкурс",
        to="cases.Contests",
        to_field="contest_id",
        on_delete=models.PROTECT,
        related_name="user_item_contest",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлён", auto_now=True)

    output = models.ForeignKey(
        verbose_name="Вывод",
        to="payments.Output",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="output_items",
    )

    def sale_item(self):
        from payments.models import Calc

        item = self.item
        self.active = False
        if item.sale_price != 0:
            sale_price = item.sale_price
            credit = (item.price - (item.price - item.sale_price)) - item.purchase_price
        elif item.percent_price != 0:
            sale_price = item.price * item.percent_price
            credit = sale_price - item.purchase_price
        else:
            sale_price = item.purchase_price
            credit = sale_price - item.purchase_price
        calc = Calc.objects.create(
            user=self.user,
            credit=credit,
            debit=credit * -1,
            balance=sale_price,
            comment=f"Продажа пользовательского предмета {self.id}",
        )
        self.calc = calc
        self.save()
        return

    class Meta:
        verbose_name = "Предмет пользователя"
        verbose_name_plural = "Предметы пользователей"


class ActivatedPromo(models.Model):
    """Сначала создаётся начисление, потом активация промокода"""

    user = models.ForeignKey(
        verbose_name="Пользователь", to=User, on_delete=models.CASCADE
    )
    promo = models.ForeignKey(
        verbose_name="Промо", to="payments.PromoCode", on_delete=models.CASCADE
    )
    bonus_using = models.BooleanField(
        verbose_name="Бонус к пополнению использован", default=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.promo.active:
            self.bonus_using = True

        if self.promo.type == "balance" and not self.bonus_using:
            self.bonus_using = True

        if self.promo.type == "bonus" and not self.bonus_using:
            if (
                self.id
                and self.promo.bonus_limit
                and self.promo.bonus_limit >= self.calc_promo.count()
            ):
                self.bonus_using = True
            if self.promo.to_date and self.promo.to_date >= self.created_at:
                self.bonus_using = True

        super(ActivatedPromo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Активированный промокод"
        verbose_name_plural = "Активированные промокоды"


class ActivatedLinks(models.Model):
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activated_links",
    )
    link = models.ForeignKey(
        verbose_name="Промо",
        to="payments.RefLinks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activated_links",
    )
    bonus_using = models.BooleanField(
        verbose_name="Бонус к пополнению использован", default=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.link.active:
            self.bonus_using = True
        if self.calc_link.exists():
            self.bonus_using = True

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Переход по реф ссылке"
        verbose_name_plural = "Переходы по реф ссылкам"


class ContestsWinners(models.Model):
    user = models.ForeignKey(
        verbose_name="Победитель",
        to=User,
        on_delete=models.PROTECT,
        related_name="contests_win",
    )
    contest = models.ForeignKey(
        verbose_name="Конкурс",
        to="cases.Contests",
        on_delete=models.PROTECT,
        related_name="winners",
    )
    item = models.ForeignKey(
        verbose_name="Приз", to="cases.Item", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Победитель конкурса"
        verbose_name_plural = "Победители конкурсов"
