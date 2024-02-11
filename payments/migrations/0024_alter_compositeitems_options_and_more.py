# Generated by Django 4.2.9 on 2024-02-11 13:20

from django.db import migrations, models
from utils.functions.id_generator import id_generator


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0023_merge_20240211_1249"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="compositeitems",
            options={
                "verbose_name": "Составной предмет",
                "verbose_name_plural": "Составные предметов",
            },
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="composite_item_id",
            field=models.CharField(
                default=id_generator,
                editable=False,
                max_length=32,
                verbose_name="Идентификатор",
            ),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="ext_id",
            field=models.CharField(null=True, verbose_name="Внешний идентификатор"),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="name",
            field=models.CharField(
                max_length=256, null=True, verbose_name="Внутреннее название"
            ),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="price_dollar",
            field=models.FloatField(default=0.0, verbose_name="Стоимость в долларах"),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="service",
            field=models.CharField(
                choices=[
                    ("moogold", "Предмет с платформы Moogold"),
                    ("test", "Тестовый предмет (не использовать!)"),
                ],
                max_length=256,
                null=True,
                verbose_name="Внешний сервис",
            ),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="technical_name",
            field=models.CharField(
                max_length=256, null=True, verbose_name="Техническое название"
            ),
        ),
        migrations.AddField(
            model_name="compositeitems",
            name="type",
            field=models.CharField(
                choices=[("crystal", "Кристалл"), ("blessing", "Благословение")],
                max_length=256,
                null=True,
                verbose_name="Тип предмета",
            ),
        ),
    ]
