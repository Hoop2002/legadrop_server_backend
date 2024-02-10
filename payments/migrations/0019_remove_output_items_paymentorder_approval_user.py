# Generated by Django 4.2.9 on 2024-02-10 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0018_alter_output_items"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="output",
            name="items",
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="approval_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_approval_payments_order",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Одобривший пользователь",
            ),
        ),
    ]
