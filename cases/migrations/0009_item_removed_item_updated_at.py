# Generated by Django 4.2.9 on 2024-01-31 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0008_alter_case_conditions_alter_case_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="removed",
            field=models.BooleanField(default=False, verbose_name="Удалено"),
        ),
        migrations.AddField(
            model_name="item",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Обновлён"),
        ),
    ]