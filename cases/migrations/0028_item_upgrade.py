# Generated by Django 4.2.9 on 2024-02-26 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0027_alter_contests_conditions"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="upgrade",
            field=models.BooleanField(default=True, verbose_name="Доступно в апгрейде"),
        ),
    ]