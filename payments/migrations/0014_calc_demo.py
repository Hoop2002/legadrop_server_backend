# Generated by Django 4.2.9 on 2024-02-06 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0013_alter_paymentorder_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="calc",
            name="demo",
            field=models.BooleanField(default=False, verbose_name="Демо начисление"),
        ),
    ]