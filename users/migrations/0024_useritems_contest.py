# Generated by Django 4.2.9 on 2024-02-20 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0027_alter_contests_conditions"),
        ("users", "0023_alter_contestswinners_contest_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="useritems",
            name="contest",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="user_item_contest",
                to="cases.contests",
                to_field="contest_id",
                verbose_name="Конкурс",
            ),
        ),
    ]