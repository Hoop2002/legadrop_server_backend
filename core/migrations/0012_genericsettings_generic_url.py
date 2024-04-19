# Generated by Django 4.2.9 on 2024-04-17 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_genericsettings_telegram_verify_bot_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="genericsettings",
            name="generic_url",
            field=models.CharField(
                default="legadrop.org",
                help_text="Вводим только домен, без протокола. По дефолту связывается по https",
                max_length=256,
                verbose_name="Основной домен сервиса",
            ),
        ),
    ]