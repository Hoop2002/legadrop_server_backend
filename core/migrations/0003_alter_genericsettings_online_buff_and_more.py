# Generated by Django 4.2.9 on 2024-02-08 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_genericsettings_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genericsettings",
            name="online_buff",
            field=models.IntegerField(default=0, verbose_name="Баф онлайна"),
        ),
        migrations.AlterField(
            model_name="genericsettings",
            name="opened_cases_buff",
            field=models.IntegerField(
                default=0, verbose_name="Баф для открытых кейсов"
            ),
        ),
        migrations.AlterField(
            model_name="genericsettings",
            name="output_crystal_buff",
            field=models.IntegerField(default=0, verbose_name="Баф выводов"),
        ),
        migrations.AlterField(
            model_name="genericsettings",
            name="purchase_buff",
            field=models.IntegerField(default=0, verbose_name="Баф покупок"),
        ),
        migrations.AlterField(
            model_name="genericsettings",
            name="users_buff",
            field=models.IntegerField(
                default=0, verbose_name="Баф всего пользователей"
            ),
        ),
    ]