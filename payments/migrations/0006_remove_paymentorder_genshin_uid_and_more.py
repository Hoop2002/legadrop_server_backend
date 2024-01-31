# Generated by Django 4.2.9 on 2024-01-30 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0005_alter_calc_options_alter_promocode_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentorder",
            name="genshin_uid",
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="sum",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]