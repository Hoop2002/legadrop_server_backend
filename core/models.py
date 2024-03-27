from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class GenericSettings(models.Model):
    opened_cases_buff = models.IntegerField("Баф для открытых кейсов", default=0)
    users_buff = models.IntegerField("Баф всего пользователей", default=0)
    online_buff = models.IntegerField("Баф онлайна", default=0)
    purchase_buff = models.IntegerField("Баф покупок", default=0)
    output_crystal_buff = models.IntegerField("Баф выводов", default=0)

    min_ref_output = models.FloatField(
        "Минимальная сумма вывода с реферальной программы", default=500.00
    )

    domain_url = models.CharField(
        "Домен реферальной ссылки",
        default="legadrop.org",
        max_length=256,
        help_text="Вводим только домен, без протокола. По дефолту связывается по https",
    )
    redirect_domain = models.CharField(
        "Домен для переадресации",
        default="legadrop.org",
        max_length=256,
        help_text="Вводим только домен, без протокола. По дефолту связывается по https",
    )

    default_mark_up_case = models.FloatField(
        verbose_name="Дефолтная наценка на кейсы",
        default=0.1,
        validators=[MinValueValidator(0)],
    )
    base_upgrade_percent = models.FloatField(
        verbose_name="Базовая ставка расчёта",
        default=0.85,
        validators=[MinValueValidator(0.5), MaxValueValidator(1)],
    )
    minimal_price_upgrade = models.FloatField(
        verbose_name="Минимальная ставка при апгрейде",
        default=20,
        validators=[MinValueValidator(0)],
    )
    base_upper_ratio = models.FloatField(
        verbose_name="Минимальный коэффициент возвышения",
        default=1.25,
        validators=[MinValueValidator(1)],
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super(GenericSettings, self).save(*args, **kwargs)

    def delete(self, safe=True, *args, **kwargs):
        if safe:
            return None
        return super().delete(*args, **kwargs)

    @classmethod
    def load(cls):
        """Загрузка единственной записи под id = 1"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Основная настройка"
        verbose_name_plural = "Основные настройки"
