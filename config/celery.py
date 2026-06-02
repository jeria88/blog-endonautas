import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("endonautas")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Tareas programadas
app.conf.beat_schedule = {
    "process-pending-emails": {
        "task": "crm.tasks.process_pending_emails",
        "schedule": crontab(minute="*/5"),  # Cada 5 minutos
    },
}
