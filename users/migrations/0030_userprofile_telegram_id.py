# Generated by Django 4.2.9 on 2024-03-07 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0029_userverify"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="telegram_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
