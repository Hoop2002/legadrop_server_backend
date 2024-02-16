# Generated by Django 4.2.9 on 2024-02-16 18:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0037_output_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="output",
            name="remove_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_remove_outputs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Удаливший пользователь",
            ),
        ),
    ]
