# Generated by Django 4.2.9 on 2024-01-30 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0005_alter_calc_options_alter_promocode_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="calc",
            name="balance",
            field=models.FloatField(default=0, verbose_name="Пользовательский баланс"),
        ),
    ]
