# Generated by Django 4.2.9 on 2024-02-10 21:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0020_output_approval_user_promocode_from_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promocode",
            name="from_user",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"profile__partner": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="promo_owner",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
