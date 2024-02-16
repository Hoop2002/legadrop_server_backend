from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from users.models import ActivatedPromo
from utils.functions import (
    payment_order_id_generator,
    id_generator,
    output_id_generator,
    id_generator_X64,
    get_genshin_server,
)
from gateways.economia_api import get_currency
from users.models import User, ActivatedPromo
from cases.models import Item


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
    APPROVAL = "manually approved"

    STATUS_TYPE_CHOICES = (
        (CREATE, "Создан"),
        (EXPIRED, "Отменен"),
        (SUCCESS, "Оплачен"),
        (APPROVAL, "Одобрен вручную"),
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
    manually_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approval_user = models.ForeignKey(
        verbose_name="Одобривший пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_approval_payments_order",
    )

    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def __str__(self):
        return self.order_id

    def approval_payment_order(self, approval_user: User):
        from users.models import ActivatedLinks

        activate_promo = ActivatedPromo.objects.filter(
            user=self.user, promo__type=PromoCode.BONUS, bonus_using=False
        ).first()

        activated_link = ActivatedLinks.objects.filter(
            user=self.user, bonus_using=False
        ).first()

        if activate_promo or activated_link:
            if activate_promo:
                comment = f'Пополнение с использованием промокода {activate_promo.promo.name} \
                           f"{activate_promo.promo.code_data}" пользоватeлем {self.user.username} на сумму {round(self.sum, 2)} \nService: NONE\nОдобрен вручную'
                credit = float(self.sum) * float(activate_promo.promo.percent)
            else:
                comment = f'Пополнение с использованием реферальной ссылки {activated_link.link.code_data} \
                            "{activated_link.link.code_data}" пользоватeлем {self.user.username} на сумму {round(self.sum, 2)} \nService: NONE\nОдобрен вручную'
                credit = float(self.sum) * float(activated_link.link.bonus)
            debit = (credit - float(self.sum)) * -1
            balance = credit

            calc = Calc.objects.create(
                user=self.user,
                credit=credit,
                debit=debit,
                balance=balance,
                comment=comment,
                demo=self.user.profile.demo,
                order=self,
            )
            if activate_promo:
                activate_promo.calc_promo.add(calc)
                activate_promo.save()
            else:
                activated_link.calc_link.add(calc)
                activated_link.save()
        else:
            comment = f"Пополнение пользоватeлем {self.user.username} на сумму {round(self.sum, 2)} \nService: NONE\nОдобрен вручную"

            credit = float(self.sum)
            debit = 0
            balance = credit

            calc = Calc.objects.create(
                user=self.user,
                credit=credit,
                debit=debit,
                balance=balance,
                comment=comment,
                demo=self.user.profile.demo,
                order=self,
            )

        self.active = False
        self.status = self.APPROVAL
        self.manually_approved = True
        self.approval_user = approval_user
        self.save()

        return f"{self.order_id} одобрен вручную", True

    def __str__(self):
        return (
            f"Пополение {self.order_id} на сумму {self.sum} пользователем {self.user}"
        )

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"


class PromoCode(models.Model):
    BALANCE = "balance"
    BONUS = "bonus"
    PROMO_TYPES = ((BALANCE, "На баланс"), (BONUS, "Бонус к пополнению"))

    code_data = models.CharField(
        default=id_generator, unique=True, max_length=128, db_index=True
    )
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
    percent = models.FloatField(
        verbose_name="Процент",
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(2.0)],
    )
    limit_activations = models.IntegerField(
        verbose_name="Лимит активаций", null=True, blank=True
    )
    to_date = models.DateTimeField(verbose_name="Действует до", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def activate_promo(self, user: User) -> (str, bool):
        time = timezone.localtime()
        if not self.active or self.removed or (self.to_date and self.to_date >= time):
            return "Промокод не действителен", False
        _activated = ActivatedPromo.objects.filter(user=user, promo=self).count()
        if _activated >= self.limit_for_user:
            return "Вы уже использовали этот промокод", False

        calc = None
        if self.type == self.BALANCE:
            calc = Calc.objects.create(
                user=user,
                credit=self.summ,
                balance=self.summ,
                debit=-self.summ,
                demo=user.profile.demo,
                comment=f"Активация промокода {self.name}",
            )
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


class RefLinks(models.Model):
    code_data = models.CharField(
        default=id_generator, unique=True, max_length=128, db_index=True
    )
    active = models.BooleanField(verbose_name="Активен", default=True)
    from_user = models.ForeignKey(
        verbose_name="От пользователя",
        to="users.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ref_links",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    @cached_property
    def bonus(self) -> float:
        return self.from_user.partner_percent

    def activate_link(self, user: User) -> (str, bool):
        from users.models import ActivatedLinks

        if not self.active or self.removed:
            return "Истёк срок действия акции", False
        _activated = ActivatedLinks.objects.filter(user=user, link=self).exists()
        if _activated:
            return "Вы уже использовали этот бонус", False

        activation = ActivatedLinks.objects.create(user=user, link=self)
        activation.save()
        return "Успешно активирован", True

    def __str__(self):
        return f"{self.code_data} от пользователя {self.from_user}"

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Реферальная ссылка"
        verbose_name_plural = "Реферальные ссылки"


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
        - Пополнение баланса с использованием промокода с бонусом к пополнению: credit = сумма пополнения * коэф пополнения, debit = (credit - сумма пополнеия) * -1, balance = credit;
        - При пополнении баланса промокодом: credit = сумма промокода, debit = сумма промокода * -1, balance = сумма промокода;
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
    ref_link = models.ForeignKey(
        verbose_name="Реферальная ссылка",
        to="users.ActivatedLinks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calc_link",
    )

    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)
    demo = models.BooleanField(verbose_name="Демо начисление", default=False)

    def __str__(self):
        return f"Начисление {self.calc_id}"

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"


class Output(models.Model):
    MOOGOLD = "moogold"
    TEST = "test"

    OUTPUT_TYPES = (
        (MOOGOLD, "Вывод с платформы Moogold"),
        (TEST, "Тестовый вывод (не использовать!)"),
    )

    COMPLETED = "completed"
    PROCCESS = "proccess"
    TECHNICAL_ERR = "technical-error"

    OUTPUT_STATUS = (
        (COMPLETED, "Завершенный"),
        (PROCCESS, "В процессе"),
        (TECHNICAL_ERR, "Техническая ошибка"),
    )

    output_id = models.CharField(
        default=output_id_generator, unique=True, max_length=32, editable=False
    )

    type = models.CharField(
        max_length=64, choices=OUTPUT_TYPES, null=False, default=MOOGOLD
    )
    status = models.CharField(
        max_length=32, choices=OUTPUT_STATUS, null=False, default=PROCCESS
    )

    player_id = models.CharField(
        verbose_name="Идентификатор аккаунта вывода", max_length=512, null=True
    )

    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_outputs",
    )

    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    approval_user = models.ForeignKey(
        verbose_name="Одобривший пользователь",
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_approval_output",
    )

    active = models.BooleanField(verbose_name="Активный", default=True)

    def __str__(self):
        return f"Вывод {self.output_id}"

    def approval_output(self, approval_user: User):
        from .manager import PaymentManager

        if not self.active:
            return f"Вывод {self.output_id} уже в процессе закупки или уже выведен", 400

        pay_manager = PaymentManager()

        is_output_moogold = pay_manager._enough_money_moogold_balance(
            self.cost_withdrawal_of_items
        )

        if not is_output_moogold:
            return "На балансе MOOGOLD не хватает денег", 400

        composites = CompositeItems.objects.all()

        crystal_items = self.output_items.filter(item__type=Item.CRYSTAL)
        blessing_items = self.output_items.filter(item__type=Item.BLESSING)
        ghost_items = self.output_items.filter(item__type=Item.GHOST_ITEM)

        if crystal_items:
            crystal_composite = composites.filter(type=CompositeItems.CRYSTAL)
            value_set = [i.crystals_quantity for i in crystal_composite]

            for crystal_item in crystal_items:
                combination = crystal_item.item.get_crystal_combinations(
                    value_set=value_set
                )

                for com in combination:
                    com_item = crystal_composite.filter(crystals_quantity=com).get()

                    if com_item.service == CompositeItems.MOOGOLD:

                        pay_manager._create_moogold_output(
                            output=self,
                            product_id=com_item.ext_id,
                            quantity=1,
                            server=get_genshin_server.get_server(self.player_id),
                            uid=self.player_id,
                            user_item=crystal_item,
                        )

                crystal_item.withdrawal_process = True
                crystal_item.save()

        if blessing_items:
            blessing_composite = composites.filter(type=CompositeItems.BLESSING).first()
            for blessing_item in blessing_items:
                pay_manager._create_moogold_output(
                    output=self,
                    product_id=blessing_composite.ext_id,
                    quantity=1,
                    server=get_genshin_server.get_server(self.player_id),
                    uid=self.player_id,
                    user_item=blessing_item,
                )
                blessing_item.withdrawal_process = True
                blessing_item.save()

        if ghost_items:
            crystal_composite = composites.filter(type=CompositeItems.CRYSTAL)
            value_set = [i.crystals_quantity for i in crystal_composite]

            for ghost_item in ghost_items:
                combination = ghost_item.item.get_crystal_combinations(
                    value_set=value_set
                )
                for com in combination:
                    com_item = crystal_composite.filter(crystals_quantity=com).get()

                    if com_item.service == CompositeItems.MOOGOLD:
                        pay_manager._create_moogold_output(
                            output=self,
                            product_id=com_item.ext_id,
                            quantity=1,
                            server=get_genshin_server.get_server(self.player_id),
                            uid=self.player_id,
                            user_item=ghost_item,
                        )
                ghost_item.withdrawal_process = True
                blessing_item.save()

        self.approval_user = approval_user
        self.active = False
        self.save()

        return f"{self.output_id} одобрен пользователем {approval_user}", 200

    @cached_property
    def cost_withdrawal_of_items(self) -> float:
        price = 0.0

        composites = CompositeItems.objects.all()

        crystal_items = self.output_items.filter(item__type=Item.CRYSTAL)
        blessing_items = self.output_items.filter(item__type=Item.BLESSING)
        ghost_items = self.output_items.filter(item__type=Item.GHOST_ITEM)

        if crystal_items:
            crystal_composite = composites.filter(type=CompositeItems.CRYSTAL)
            value_set = [i.crystals_quantity for i in crystal_composite]
            for crystal_item in crystal_items:
                combination = crystal_item.item.get_crystal_combinations(
                    value_set=value_set
                )
                for com in combination:
                    com_item = crystal_composite.filter(crystals_quantity=com).get()
                    price += com_item.price_dollar

        if blessing_items:
            blessing_composite = composites.filter(type=CompositeItems.BLESSING).first()
            for _ in blessing_items:
                price += blessing_composite.price_dollar

        if ghost_items:
            crystal_composite = composites.filter(type=CompositeItems.CRYSTAL)
            value_set = [i.crystals_quantity for i in crystal_composite]
            for ghost_item in ghost_items:
                combination = ghost_item.item.get_crystal_combinations(
                    value_set=value_set
                )
                for com in combination:
                    com_item = crystal_composite.filter(crystals_quantity=com).get()
                    price += com_item.price_dollar
        return price

    class Meta:
        verbose_name = "Вывод предмета"
        verbose_name_plural = "Выводы предметов"


class CompositeItems(models.Model):
    MOOGOLD = "moogold"
    TEST = "test"

    SERVICE_TYPES = (
        (MOOGOLD, "Предмет с платформы Moogold"),
        (TEST, "Тестовый предмет (не использовать!)"),
    )

    CRYSTAL = "crystal"
    BLESSING = "blessing"

    ITEMS_TYPE = ((CRYSTAL, "Кристалл"), (BLESSING, "Благословение"))

    ext_id = models.CharField(verbose_name="Внешний идентификатор", null=True)
    technical_name = models.CharField(
        verbose_name="Техническое название", max_length=256, null=True
    )
    name = models.CharField(
        verbose_name="Внутреннее название", max_length=256, null=True
    )
    type = models.CharField(
        verbose_name="Тип предмета", max_length=256, choices=ITEMS_TYPE, null=True
    )
    service = models.CharField(
        verbose_name="Внешний сервис", max_length=256, choices=SERVICE_TYPES, null=True
    )
    composite_item_id = models.CharField(
        verbose_name="Идентификатор",
        default=id_generator,
        max_length=32,
        editable=False,
    )
    crystals_quantity = models.IntegerField(
        verbose_name="Количество кристаллов", null=True, default=0
    )
    price_dollar = models.FloatField(verbose_name="Стоимость в долларах", default=0.0)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    def __str__(self):
        return f"Составной предмет {self.technical_name}"

    @cached_property
    def price_rub(self) -> float:
        currency = float(get_currency()["USDRUB"]["high"])
        return round(currency * self.price_dollar)

    class Meta:
        verbose_name = "Составной предмет"
        verbose_name_plural = "Составные предметов"


class PurchaseCompositeItems(models.Model):
    MOOGOLD = "moogold"
    TEST = "test"

    PURCHASE_TYPES = (
        (MOOGOLD, "Вывод с платформы Moogold"),
        (TEST, "Тестовый вывод (не использовать!)"),
    )

    COMPLETED = "completed"
    PROCCESS = "proccess"
    INCORRECT_DETAILS = "incorrect-details"
    RESTOCK = "restock"
    REFUNDED = "refunded"

    PURCHASE_STATUS = (
        (COMPLETED, "Завершенный"),
        (PROCCESS, "В процессе"),
        (INCORRECT_DETAILS, "Некорректные данные"),
        (RESTOCK, "Недостаточно денег на балансе"),
        (REFUNDED, "Возврат"),
    )

    type = models.CharField(
        max_length=64, choices=PURCHASE_TYPES, null=False, default=MOOGOLD
    )
    status = models.CharField(
        max_length=32, choices=PURCHASE_STATUS, null=False, default=PROCCESS
    )

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)
    removed = models.BooleanField(verbose_name="Удалено", default=False)

    ext_id_order = models.CharField(
        verbose_name="Идентификатор во внешнем сервиса", max_length=1024
    )
    name = models.CharField(verbose_name="Наименование", max_length=1024)

    pci_id = models.CharField(
        verbose_name="Внутренний идентификатор", max_length=70, default=id_generator_X64
    )
    player_id = models.CharField(
        verbose_name="Идентификатор аккаунта вывода", max_length=512, null=True
    )
    server = models.CharField(verbose_name="Сервер", max_length=120, null=True)
    output = models.ForeignKey(
        verbose_name="Вывод",
        to="payments.Output",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_ci_outputs",
    )

    user_item = models.ForeignKey(
        verbose_name="Выводимый предмет",
        to="users.UserItems",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_composite_in_users_item",
    )

    def __str__(self):
        return f"Закупка {self.pci_id} на {self.output}"

    class Meta:
        verbose_name = "Закупка на сторонем сервисе"
        verbose_name_plural = "Закупки на стороних сервисах"
