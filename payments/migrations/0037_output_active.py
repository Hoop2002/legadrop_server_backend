# Generated by Django 4.2.9 on 2024-02-16 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0036_purchasecompositeitems_user_item"),
    ]

    operations = [
        migrations.AddField(
            model_name="output",
            name="active",
            field=models.BooleanField(default=True, verbose_name="Активный"),
        ),
    ]
