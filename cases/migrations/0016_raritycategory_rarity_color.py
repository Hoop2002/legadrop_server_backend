# Generated by Django 4.2.9 on 2024-02-03 16:14

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0015_alter_case_items"),
    ]

    operations = [
        migrations.AddField(
            model_name="raritycategory",
            name="rarity_color",
            field=colorfield.fields.ColorField(
                default="#FF0000",
                image_field=None,
                max_length=25,
                samples=None,
                verbose_name="Цвет категории",
            ),
        ),
    ]
