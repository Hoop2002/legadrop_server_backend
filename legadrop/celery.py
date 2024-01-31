from celery import Celery, shared_task
from django.conf import settings
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legadrop.settings")

app = Celery("legadrop")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def debug_task():
    print(f"debug test")
