# Generated by Django 4.2.9 on 2024-04-03 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0033_openedcases_item"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="purchase_price_cached",
            field=models.FloatField(default=0, verbose_name="Закупочная цена в базе"),
        ),
    ]
