# Generated by Django 4.2.9 on 2024-02-12 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0022_item_ghost_crystals_quantity_alter_item_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="service",
            field=models.CharField(
                choices=[
                    ("moogold", "Предмет с Moogold"),
                    ("test", "Тестовый (не использовать!)"),
                ],
                max_length=32,
                null=True,
                verbose_name="Тип предмета",
            ),
        ),
    ]
