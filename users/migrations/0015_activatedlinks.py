# Generated by Django 4.2.9 on 2024-02-12 11:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0028_reflinks"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0014_remove_userprofile_partner"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivatedLinks",
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
                    "bonus_using",
                    models.BooleanField(
                        default=False, verbose_name="Бонус к пополнению использован"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "link",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="payments.reflinks",
                        verbose_name="Промо",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Переход по реф ссылке",
                "verbose_name_plural": "Переходы по реф ссылкам",
            },
        ),
    ]
