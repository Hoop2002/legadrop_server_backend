# Generated by Django 4.2.9 on 2024-01-30 13:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cases", "0006_delete_useritems"),
        ("users", "0002_alter_userprofile_image"),
    ]

    operations = [
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
                        verbose_name="Предмет",
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
            options={
                "verbose_name": "Предмет пользователя",
                "verbose_name_plural": "Предметы пользователей",
            },
        ),
    ]
