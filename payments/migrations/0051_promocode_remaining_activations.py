# Generated by Django 4.2.9 on 2024-04-03 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0050_rename_include_service_lava_paymentorder_include_service"),
    ]

    operations = [
        migrations.AddField(
            model_name="promocode",
            name="remaining_activations",
            field=models.IntegerField(default=0, verbose_name="Остаток активаций"),
        ),
    ]
