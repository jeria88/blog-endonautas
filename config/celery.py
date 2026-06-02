import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("endonautas")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Usar base de datos como broker (no necesita Redis)
app.conf.broker_url = os.environ.get("REDIS_URL", "django-db://")
app.conf.result_backend = "django-db"
app.conf.task_always_eager = os.environ.get("CELERY_ALWAYS_EAGER", "False") == "True"

# Tareas programadas
app.conf.beat_schedule = {
    "check-pending-emails": {
        "task": "crm.tasks.check_pending_emails",
        "schedule": 300,  # Cada 5 minutos
    },
}
