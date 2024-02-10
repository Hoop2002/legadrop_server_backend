# Generated by Django 4.2.9 on 2024-02-08 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GenericSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("opened_cases_buff", models.IntegerField(default=0)),
                ("users_buff", models.IntegerField(default=0)),
                ("online_buff", models.IntegerField(default=0)),
                ("purchase_buff", models.IntegerField(default=0)),
                ("output_crystal_buff", models.IntegerField(default=0)),
            ],
        ),
    ]