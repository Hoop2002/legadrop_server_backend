# Generated by Django 4.2.9 on 2024-02-02 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_activatedpromo"),
    ]

    operations = [
        migrations.AddField(
            model_name="useritems",
            name="withdrawn",
            field=models.BooleanField(default=False, verbose_name="Выведен с аккаунта"),
        ),
    ]
