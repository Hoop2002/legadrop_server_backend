# Generated by Django 4.2.9 on 2024-02-02 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0010_item_percent_price_item_sale_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="color",
            field=models.CharField(max_length=128, null=True, verbose_name="Цвет"),
        ),
    ]