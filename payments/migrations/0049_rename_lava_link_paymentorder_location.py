# Generated by Django 4.2.9 on 2024-02-29 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0048_alter_refoutput_sum"),
    ]

    operations = [
        migrations.RenameField(
            model_name="paymentorder",
            old_name="lava_link",
            new_name="location",
        ),
    ]
