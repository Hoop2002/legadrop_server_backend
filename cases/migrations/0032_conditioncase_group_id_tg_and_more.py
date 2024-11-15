# Generated by Django 4.2.9 on 2024-03-07 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0031_conditioncase_group_id_vk"),
    ]

    operations = [
        migrations.AddField(
            model_name="conditioncase",
            name="group_id_tg",
            field=models.CharField(
                max_length=1024,
                null=True,
                verbose_name="ID канала 'telegram.com' формат '-1009999999'",
            ),
        ),
        migrations.AlterField(
            model_name="conditioncase",
            name="type_condition",
            field=models.CharField(
                choices=[
                    ("calc", "Начисление"),
                    ("time", "Время"),
                    ("group_vk", "Подписка на группу VK"),
                    ("group_tg", "Подписка на канал Telegram"),
                ],
                max_length=128,
            ),
        ),
    ]
