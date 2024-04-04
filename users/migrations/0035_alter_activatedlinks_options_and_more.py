# Generated by Django 4.2.9 on 2024-04-04 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0034_alter_activatedlinks_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activatedlinks",
            options={
                "ordering": ("-id",),
                "verbose_name": "Переход по реф ссылке",
                "verbose_name_plural": "Переходы по реф ссылкам",
            },
        ),
        migrations.AlterModelOptions(
            name="activatedpromo",
            options={
                "ordering": ("-id",),
                "verbose_name": "Активированный промокод",
                "verbose_name_plural": "Активированные промокоды",
            },
        ),
        migrations.AlterModelOptions(
            name="contestswinners",
            options={
                "ordering": ("-id",),
                "verbose_name": "Победитель конкурса",
                "verbose_name_plural": "Победители конкурсов",
            },
        ),
        migrations.AlterModelOptions(
            name="useritems",
            options={
                "ordering": ("-id",),
                "verbose_name": "Предмет пользователя",
                "verbose_name_plural": "Предметы пользователей",
            },
        ),
        migrations.AlterModelOptions(
            name="userupgradehistory",
            options={"ordering": ("-id",)},
        ),
        migrations.AlterModelOptions(
            name="userverify",
            options={
                "ordering": ("-id",),
                "verbose_name": "Верификация пользователя",
                "verbose_name_plural": "Верификации пользователей",
            },
        ),
    ]
