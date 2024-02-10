# Generated by Django 4.2.9 on 2024-02-07 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from utils.functions import output_id_generator


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0016_raritycategory_rarity_color"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0016_rename_creation_date_calc_created_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Output",
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
                    "output_id",
                    models.CharField(
                        default=output_id_generator,
                        editable=False,
                        max_length=32,
                        unique=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("moogold", "Вывод с платформы Moogold"),
                            ("test", "Тестовый вывод (не использовать!)"),
                        ],
                        max_length=64,
                    ),
                ),
                (
                    "comment",
                    models.TextField(blank=True, null=True, verbose_name="Комментарий"),
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
                (
                    "items",
                    models.ManyToManyField(
                        blank=True,
                        related_name="output_items",
                        to="cases.item",
                        verbose_name="Предметы",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="user_outputs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вывод предмета",
                "verbose_name_plural": "Выводы предметов",
            },
        ),
    ]