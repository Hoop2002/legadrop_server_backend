# Generated by Django 4.2.9 on 2024-02-08 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="genericsettings",
            options={
                "verbose_name": "Основная настройка",
                "verbose_name_plural": "Основные настройки",
            },
        ),
    ]