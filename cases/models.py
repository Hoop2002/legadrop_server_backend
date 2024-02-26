from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from random import choices

from utils.functions import (
    id_generator,
    generate_upload_name,
    transliterate,
    find_combination,
)


class Contests(models.Model):
    contest_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256)
    timer = models.DurationField(
        verbose_name="Промежуток",
        default=timezone.timedelta(seconds=3600 * 24),
        help_text="Формат указания в виде 'дни часы:минуты:секунды'",
    )
    next_start = models.DateTimeField(
        verbose_name="Время следующего розыгрыша", null=True, blank=True
    )
    active = models.BooleanField(verbose_name="Активен", default=True)
    one_time = models.BooleanField(verbose_name="Конкурс одноразовый", default=False)
    items = models.ManyToManyField(
        verbose_name="Список призов",
        to="Item",
        related_name="contests",
        limit_choices_to={"removed": False},
    )
    current_award = models.ForeignKey(
        verbose_name="Текущий приз",
        to="Item",
        related_name="current_award_contests",
        to_field="item_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    participants = models.ManyToManyField(
        verbose_name="Участники",
        to=User,
        related_name="contests",
        blank=True,
    )
    conditions = models.ManyToManyField(
        verbose_name="Условия участия",
        to="ConditionCase",
        related_name="contests",
        blank=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def set_new_award(self):
        if self.items.count() == 1:
            return "Не возможно выбрать приз, Должно быть больше 1"

        while True:
            item = self.items.order_by("?").first()
            if item != self.current_award:
                break

        self.current_award = item
        self.save()

    def set_next_start(self, force=False):
        from users.models import ContestsWinners

        if (not self.next_start and self.active and not self.removed) or force:
            last_winner = (
                ContestsWinners.objects.filter(contest=self)
                .order_by("created_at")
                .last()
            )
            if last_winner:
                self.next_start = last_winner.created_at + self.timer
            else:
                _next = self.updated_at + self.timer
                if _next < timezone.localtime():
                    _next = timezone.localtime() + self.timer
                self.next_start = _next
            self.save()

    def check_conditions(self, user: User) -> tuple[str, bool]:
        from payments.models import PaymentOrder

        if self.conditions.exists():
            for condition in self.conditions.iterator():
                now = timezone.localtime()
                time = now - timezone.timedelta(
                    hours=condition.time.hour,
                    minutes=condition.time.minute,
                    seconds=condition.time.second,
                )

                if condition.type_condition == ConditionCase.CALC:
                    amount = (
                        PaymentOrder.objects.filter(
                            user=user,
                            created_at__gte=time,
                            status__in=(PaymentOrder.SUCCESS, PaymentOrder.APPROVAL),
                        ).aggregate(models.Sum("sum"))["sum__sum"]
                        or 0
                    )
                    amount = float(amount)
                    if amount < condition.price:
                        return (
                            f"Для участия в этом конкурсе требуется внести {condition.price - amount}, в течении {condition.time}",
                            False,
                        )
        return "", True

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Конкурс"
        verbose_name_plural = "Конкурсы"


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
    """
    Модель предметов

    Типы предметов:
    1. CRYSTAL - кристаллы, основная валюта в игре Genshin Impact.
    2. BLESSING - платная 30-ти дневная подписка внутри игры, которая при покупке дает 300 кристаллов сотворения и начисляет по 90 примогемов ежедневно в течении этих 30 дней.
    3. GHOST_ITEM - предметы которые в нашей системе являются каким-то объектом, но на деле пользователю выводится сумма кристаллов для приобретения оного предмета внутри игры,
       поле ghost_price является количеством кристаллов для покупки этого предмета внутри игры, и в нашей системе является количеством кристаллов.
    """

    CRYSTAL = "crystal"
    BLESSING = "blessing"
    GHOST_ITEM = "ghost_item"

    ITEMS_TYPE = (
        (CRYSTAL, "Кристалл"),
        (BLESSING, "Благословение"),
        (GHOST_ITEM, "Призрачный пердмет"),
    )

    MOOGOLD = "moogold"
    TEST = "test"

    SERVICE_TYPES = (
        (MOOGOLD, "Предмет с Moogold"),
        (TEST, "Тестовый (не использовать!)"),
    )

    item_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    name = models.CharField(verbose_name="Название", max_length=256)
    price = models.FloatField(verbose_name="Стоимость", default=0, null=False)
    type = models.CharField(
        verbose_name="Тип предмета", max_length=32, choices=ITEMS_TYPE, null=True
    )
    service = models.CharField(
        verbose_name="Тип предмета", max_length=32, choices=SERVICE_TYPES, null=True
    )
    crystals_quantity = models.IntegerField(
        verbose_name="Количество кристаллов", null=True, default=0
    )
    purchase_price = models.FloatField(
        verbose_name="Закупочная цена", default=0, null=False
    )
    is_output = models.BooleanField(
        verbose_name="Выводимый предмет с сервиса", null=False, default=True
    )
    sale_price = models.FloatField(verbose_name="Цена продажи", default=0)
    percent_price = models.FloatField(
        verbose_name="Процент от начальной цены при продаже",
        default=0,
        validators=[MinValueValidator(0)],
    )
    sale = models.BooleanField(verbose_name="Продаётся в магазине", default=False)
    upgrade = models.BooleanField(verbose_name="Доступно в апгрейде", default=True)
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
    is_output = models.BooleanField(verbose_name="Выводимый/Не выводимый", default=True)

    def get_crystal_combinations(self, value_set):
        return find_combination(target=self.crystals_quantity, values=value_set)

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
    description = models.TextField(
        verbose_name="Описание для пользователя", blank=True, null=True
    )
    condition_id = models.CharField(
        default=id_generator, max_length=9, editable=False, unique=True
    )
    type_condition = models.CharField(max_length=128, choices=CONDITION_TYPES_CHOICES)
    price = models.FloatField(verbose_name="Сумма внесения", null=True, blank=True)
    time = models.TimeField(verbose_name="Глубина проверки", null=True, blank=True)
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

    def set_recommendation_price(self):
        if not self.id:
            return
        self.price = self.recommendation_price
        self.save()

    def save(self, *args, **kwargs):
        if not self.removed:
            self.translit_name = transliterate(self.name)
        return super().save(*args, **kwargs)

    def check_conditions(self, user: User) -> tuple[str, bool]:
        from payments.models import PaymentOrder

        if self.conditions.exists():
            for condition in self.conditions.iterator():
                now = timezone.localtime()
                time = now - timezone.timedelta(
                    hours=condition.time.hour,
                    minutes=condition.time.minute,
                    seconds=condition.time.second,
                )
                timedelta_reboot = timezone.timedelta(
                    hours=condition.time_reboot.hour,
                    minutes=condition.time_reboot.minute,
                    seconds=condition.time_reboot.second,
                )
                reboot = now - timedelta_reboot
                opened = OpenedCases.objects.filter(
                    user=user, case=self, open_date__gte=reboot
                )
                if opened.exists():
                    return (
                        f"До следующего открытия этого кейса {timedelta_reboot - (now - opened.last().open_date)}",
                        False,
                    )

                if condition.type_condition == ConditionCase.CALC:
                    amount = (
                        PaymentOrder.objects.filter(
                            user=user,
                            created_at__gte=time,
                            status__in=(PaymentOrder.SUCCESS, PaymentOrder.APPROVAL),
                        ).aggregate(models.Sum("sum"))["sum__sum"]
                        or 0
                    )
                    amount = float(amount)
                    if amount < condition.price:
                        return (
                            f"Для открытия этого кейса требуется внести {condition.price - amount}, в течении {condition.time}",
                            False,
                        )
        return "", True

    def get_items(self):
        """Возвращает json предметов с проставленными процентами"""
        items = self.items.values(
            "item_id", "name", "price", "image", "rarity_category", "purchase_price"
        )
        # считаем коэффициент для айтемов
        items_kfs = {item["item_id"]: 1 / item["purchase_price"] for item in items}
        # из полученных коэффициентов выше считаем нормализацию
        normalise_kof = 1 / sum([items_kfs[item] for item in items_kfs])

        # высчитываем дефолтный процент для каждого айтема
        for item in items:
            item["percent"] = normalise_kof * items_kfs[item["item_id"]] * 100
        return items

    @cached_property
    def recommendation_price(self) -> float:
        from core.models import GenericSettings

        generic = GenericSettings.load()
        items = self.items.all()
        if items.filter(purchase_price=0).exists():
            items = items.exclude(purchase_price=0)
        if items.count() == 0:
            return 0
        items_kfs = [1 / item.purchase_price for item in items]
        normalise_kof = 1 / sum(items_kfs)
        price = len(items_kfs) * normalise_kof
        price = price + price * generic.default_mark_up_case
        return round(price, 2)

    recommendation_price.short_description = "Рекомендованная минимальная цена"

    def _get_rand_item(self, user: User):
        items = self.items.all()
        if items.filter(purchase_price=0).exists():
            items = items.exclude(purchase_price=0)
        # считаем коэффициент для айтемов и берём цену для дальнейших вычислений
        items_kfs = {
            item.item_id: {"kof": 1 / item.purchase_price, "price": item.purchase_price}
            for item in items
        }
        # из полученных коэффициентов выше считаем нормализацию
        normalise_kof = 1 / sum([items_kfs[item]["kof"] for item in items_kfs])
        # высчитываем дефолтный процент для каждого айтема

        for item in items_kfs.keys():
            items_kfs[item]["percent"] = normalise_kof * items_kfs[item]["kof"]

        if user.profile.individual_percent != 0:
            # теперь считаем то же самое, что выше, только с учётом коэффициента пользователя
            user_kof = normalise_kof * (1 + user.profile.individual_percent)
            for item in items_kfs.keys():
                if items_kfs[item]["price"] > self.price:
                    items_kfs[item]["percent"] = user_kof * items_kfs[item]["kof"]
            sum_percent = sum([items_kfs[item]["percent"] for item in items_kfs.keys()])
            # Нормализиуем получившиеся проценты
            for item in items_kfs.keys():
                items_kfs[item]["percent"] = items_kfs[item]["percent"] / sum_percent

        rand_item = choices(
            list(items_kfs.keys()),
            weights=[items_kfs[item]["percent"] for item in items_kfs.keys()],
        )[0]
        rand_item = self.items.get(item_id=rand_item)

        return rand_item

    def open_case(self, user: User):
        """Метод открытия кейса
        Условия проверки бесплатного кейса, только как защита от дурака
        """
        from payments.models import Calc
        from users.models import UserItems

        item = self._get_rand_item(user)
        win = item.purchase_price > self.price if not self.case_free else True
        OpenedCases.objects.create(case=self, user=user, win=win)

        if not self.case_free:
            Calc.objects.create(
                user=user,
                balance=-self.price,
                comment=f"Открытие кейса {self.name}",
            )
        else:
            Calc.objects.create(
                user=user,
                comment=f"Открытие кейса {self.name}",
            )
        UserItems.objects.create(user=user, item=item, from_case=True, case=self)
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
    win = models.BooleanField(verbose_name="Предмет дороже кейса", default=False)

    def __str__(self):
        return f"{self.user} открыл {self.case}"

    class Meta:
        verbose_name = "Открытый кейс"
        verbose_name_plural = "Открытые кейсы"
