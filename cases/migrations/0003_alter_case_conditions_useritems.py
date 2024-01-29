# Generated by Django 4.2.9 on 2024-01-29 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cases", "0002_alter_case_case_id_alter_case_conditions_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="conditions",
            field=models.ManyToManyField(
                to="cases.conditioncase", verbose_name="Условия открытия кейса"
            ),
        ),
        migrations.CreateModel(
            name="UserItems",
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
                    "active",
                    models.BooleanField(default=True, verbose_name="Есть на аккаунте"),
                ),
                (
                    "item",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="user_items",
                        to="cases.item",
                        verbose_name="Приз",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="items",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
        ),
    ]
