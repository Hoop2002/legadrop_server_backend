from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField
from django.contrib.auth.models import User

from utils.functions import id_generator, generate_upload_name, transliterate


class RarityCategory(models.Model):
    rarity_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256)
    rarity_color = ColorField(default="#FF0000", verbose_name="Цвет категории")
    category_percent = models.FloatField(default=1, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория редкости"
        verbose_name_plural = "Категории редкости"


class Item(models.Model):
    item_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256)
    price = models.FloatField(verbose_name="Стоимость", default=0, null=False)
    purchase_price = models.FloatField(
        verbose_name="Закупочная цена", default=0, null=False
    )
    sale_price = models.FloatField(verbose_name="Цена продажи", default=0)
    percent_price = models.FloatField(
        verbose_name="Процент от начальной цены при продаже",
        default=0,
        validators=[MinValueValidator(0)],
    )
    sale = models.BooleanField(verbose_name="Продаётся в магазине", default=False)
    image = models.ImageField(upload_to=generate_upload_name, verbose_name="Картинка")
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлён", auto_now=True)
    step_down_factor = models.FloatField(verbose_name="Понижающий фактор", default=1)
    rarity_category = models.ForeignKey(
        verbose_name="Категория уникальности",
        to="RarityCategory",
        to_field="rarity_id",
        related_name="items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class Category(models.Model):
    category_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class ConditionCase(models.Model):
    CALC = "calc"
    TIME = "time"
    CONDITION_TYPES_CHOICES = (
        (CALC, "Начисление"),
        (TIME, "Время"),
    )
    name = models.CharField(max_length=256, unique=True)
    condition_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    type_condition = models.CharField(max_length=128, choices=CONDITION_TYPES_CHOICES)
    price = models.FloatField(verbose_name="Сумма внесения", null=True, blank=True)
    time = models.TimeField(verbose_name="Глубина проверки")
    time_reboot = models.TimeField(verbose_name="Снова открыть кейс через")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Условие"
        verbose_name_plural = "Условия"


class Case(models.Model):
    case_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256, unique=True)
    translit_name = models.CharField(
        verbose_name="Транслитерация названия",
        default="name",
        editable=False,
        unique=True,
    )
    active = models.BooleanField(verbose_name="Активен", default=True)
    image = models.ImageField(
        upload_to=generate_upload_name,
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    price = models.FloatField(verbose_name="Стоимость", default=0)
    case_free = models.BooleanField(verbose_name="Кейс бесплатный", default=False)
    category = models.ForeignKey(
        verbose_name="Категория кейса",
        to="Category",
        to_field="category_id",
        on_delete=models.SET_NULL,
        related_name="cases",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлён", auto_now=True)
    items = models.ManyToManyField(
        verbose_name="Предметы в кейсе", to="Item", limit_choices_to={"removed": False}
    )
    conditions = models.ManyToManyField(
        verbose_name="Условия открытия кейса", to=ConditionCase, blank=True
    )
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def save(self, *args, **kwargs):
        if not self.removed:
            self.translit_name = transliterate(self.name)
        return super().save(*args, **kwargs)

    def check_conditions(self, user: User) -> tuple[str, bool]:
        from payments.models import PaymentOrder

        if self.conditions.exists():
            for condition in self.conditions.iterator():
                time = timezone.localtime() - timezone.timedelta(
                    hours=condition.time.hour,
                    minutes=condition.time.minute,
                    seconds=condition.time.second,
                )
                reboot = timezone.localtime() - timezone.timedelta(
                    hours=condition.time_reboot.hour,
                    minutes=condition.time_reboot.minute,
                    seconds=condition.time_reboot.second,
                )

                if condition.type_condition == ConditionCase.CALC:
                    if OpenedCases.objects.filter(
                        user=user, case=self, open_date__gte=reboot
                    ).exists():
                        return (
                            f"До следующего открытия этого кейса НАДО УКАЗАТЬ ВРЕМЯ",
                            False,
                        )
                    amount = (
                        PaymentOrder.objects.filter(
                            user=user,
                            created_at__gte=time,
                            status__in=(PaymentOrder.SUCCESS, PaymentOrder.APPROVAL),
                        ).aggregate(models.Sum("sum"))["sum__sum"]
                        or 0
                    )
                    if amount < condition.price:
                        return (
                            f"Для открытия этого кейса требуется внести {condition.price - amount}, в течении {condition.time}",
                            False,
                        )
            return "", True

    def open_case(self, user: User):
        from payments.models import Calc

        # todo возвращать предмет по системе шансов
        item = self.items.first()
        debit = self.price - item.price
        OpenedCases.objects.create(case=self, user=user)
        Calc.objects.create(balance=-self.price, debit=debit, credit=debit * -1)
        return item

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"


class OpenedCases(models.Model):
    history_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    open_date = models.DateTimeField("Дата открытия кейса", auto_now_add=True)
    case = models.ForeignKey(
        verbose_name="Кейс",
        to="Case",
        to_field="case_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_opening",
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opened_cases",
    )

    def __str__(self):
        return f"{self.user} открыл {self.case}"

    class Meta:
        verbose_name = "Открытый кейс"
        verbose_name_plural = "Открытые кейсы"
