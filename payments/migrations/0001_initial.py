# Generated by Django 4.2.9 on 2024-01-29 07:00

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PaymentOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order_id",
                    models.CharField(
                        default=utils.payments_id_generator.payment_order_id_generator,
                        max_length=128,
                    ),
                ),
                (
                    "sum",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=17),
                ),
                (
                    "type_payments",
                    models.CharField(
                        choices=[
                            ("lava", "Платежная система ЛАВА(LAVA)"),
                            ("yookassa", "Платежная система ЮКасса(Yookassa)"),
                        ],
                        max_length=64,
                    ),
                ),
            ],
        ),
    ]