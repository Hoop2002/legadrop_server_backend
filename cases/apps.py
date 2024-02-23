from django.apps import AppConfig
from django.db.models.signals import post_save


def set_price(sender, instance, **kwargs):
    if not instance.items.exists():
        return
    if instance.case_free:
        return
    if not instance.price:
        instance.set_recommendation_price()


class CasesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cases"

    def ready(self):
        from cases.models import Case

        post_save.connect(
            set_price,
            sender=Case,
        )
