# Generated by Django 4.2.9 on 2024-04-08 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0036_userprofile_balance_save_userprofile_debit_save_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="telegram_username",
            field=models.CharField(
                db_index=True,
                max_length=512,
                null=True,
                verbose_name="Телеграм никнейм",
            ),
        ),
    ]
