# Generated by Django 4.2.9 on 2024-03-02 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_genericsettings_free_kassa_failure_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="genericsettings",
            name="email_verify_url",
            field=models.CharField(
                default="https://legadrop.org/verifyed/",
                max_length=256,
                verbose_name="Домен для подтверждения",
            ),
        ),
        migrations.AddField(
            model_name="genericsettings",
            name="email_verify_url_redirect",
            field=models.CharField(
                default="https://legadrop.org",
                max_length=256,
                verbose_name="Домен для переадресации после подтверждения email",
            ),
        ),
    ]
