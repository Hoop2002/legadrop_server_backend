# Generated by Django 4.2.9 on 2024-02-12 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0016_alter_userprofile_partner_percent"),
    ]

    operations = [
        migrations.AddField(
            model_name="useritems",
            name="withdrawal_process",
            field=models.BooleanField(
                default=False, verbose_name="Находится в процессе вывода"
            ),
        ),
    ]
