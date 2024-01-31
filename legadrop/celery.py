from celery import Celery
from django.conf import settings
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legadrop.settings")

app = Celery("legadrop")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
