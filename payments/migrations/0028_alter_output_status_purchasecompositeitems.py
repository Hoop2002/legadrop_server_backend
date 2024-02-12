# Generated by Django 4.2.9 on 2024-02-11 19:32

from django.db import migrations, models
import django.db.models.deletion
from utils.functions import id_generator_X64


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0027_compositeitems_removed_output_removed_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="output",
            name="status",
            field=models.CharField(
                choices=[
                    ("completed", "Завершенный"),
                    ("proccess", "В процессе"),
                    ("technical-error", "Техническая ошибка"),
                ],
                default="proccess",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="PurchaseCompositeItems",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("moogold", "Вывод с платформы Moogold"),
                            ("test", "Тестовый вывод (не использовать!)"),
                        ],
                        default="moogold",
                        max_length=64,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("completed", "Завершенный"),
                            ("proccess", "В процессе"),
                            ("incorrect-details", "Некорректные данные"),
                            ("restock", "Недостаточно денег на балансе"),
                            ("refunded", "Возврат"),
                        ],
                        default="proccess",
                        max_length=32,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата изменения"),
                ),
                ("removed", models.BooleanField(default=False, verbose_name="Удалено")),
                (
                    "ext_id_order",
                    models.CharField(
                        max_length=1024, verbose_name="Идентификатор во внешнем сервиса"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=1024, verbose_name="Наименование"),
                ),
                (
                    "pci_id",
                    models.CharField(
                        default=id_generator_X64,
                        max_length=64,
                        verbose_name="Внутренний идентификатор",
                    ),
                ),
                (
                    "output",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="purchase_ci_output",
                        to="payments.output",
                        verbose_name="Вывод",
                    ),
                ),
            ],
            options={
                "verbose_name": "Закупка на сторонем сервисе",
                "verbose_name_plural": "Закупки на стороних сервисах",
            },
        ),
    ]
