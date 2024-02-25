# Generated by Django 4.2.9 on 2024-02-25 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_genericsettings_default_mark_up_case"),
    ]

    operations = [
        migrations.AddField(
            model_name="genericsettings",
            name="min_ref_output",
            field=models.FloatField(
                default=500.0,
                verbose_name="Минимальная сумма вывода с реферальной программы",
            ),
        ),
    ]
