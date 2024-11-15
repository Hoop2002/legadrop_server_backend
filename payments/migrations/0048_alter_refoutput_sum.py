# Generated by Django 4.2.9 on 2024-02-26 15:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0047_alter_refoutput_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="refoutput",
            name="sum",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Сумма вывода",
            ),
        ),
    ]
