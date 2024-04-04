# Generated by Django 4.2.9 on 2024-04-04 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0035_alter_case_options_alter_category_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="case",
            options={
                "ordering": ("-id",),
                "verbose_name": "Кейс",
                "verbose_name_plural": "Кейсы",
            },
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ("-id",),
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.AlterModelOptions(
            name="conditioncase",
            options={
                "ordering": ("-id",),
                "verbose_name": "Условие",
                "verbose_name_plural": "Условия",
            },
        ),
        migrations.AlterModelOptions(
            name="contests",
            options={
                "ordering": ("-id",),
                "verbose_name": "Конкурс",
                "verbose_name_plural": "Конкурсы",
            },
        ),
        migrations.AlterModelOptions(
            name="item",
            options={
                "ordering": ("-id",),
                "verbose_name": "Предмет",
                "verbose_name_plural": "Предметы",
            },
        ),
        migrations.AlterModelOptions(
            name="openedcases",
            options={
                "ordering": ("-id",),
                "verbose_name": "Открытый кейс",
                "verbose_name_plural": "Открытые кейсы",
            },
        ),
        migrations.AlterModelOptions(
            name="raritycategory",
            options={
                "ordering": ("-id",),
                "verbose_name": "Категория редкости",
                "verbose_name_plural": "Категории редкости",
            },
        ),
    ]
