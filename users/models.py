from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from cases.models import Item
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

    @cached_property
    def balance(self) -> float:
        balance = self.user.calc.aggregate(models.Sum("balance"))["balance__sum"]
        if balance is None:
            return 0
        return balance

    def __str__(self):
        return self.user.username


class UserItems(models.Model):
    from_case = models.BooleanField(verbose_name="Выпал из кейса", default=False)
    active = models.BooleanField(verbose_name="Есть на аккаунте", default=True)
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
