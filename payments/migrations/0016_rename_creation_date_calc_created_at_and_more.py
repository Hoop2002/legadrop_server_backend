# Generated by Django 4.2.9 on 2024-02-06 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0015_paymentorder_created_at_paymentorder_updated_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="calc",
            old_name="creation_date",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="calc",
            old_name="update_date",
            new_name="updated_at",
        ),
    ]