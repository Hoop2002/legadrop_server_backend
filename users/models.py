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
