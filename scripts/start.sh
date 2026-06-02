#!/bin/bash
# scripts/start.sh — comando de arranque de Railway
# Orden: migraciones → seeds → static → scheduler background → gunicorn

set -e

SETTINGS="config.settings.production"

echo "==> prepare_db"
python manage.py prepare_db --settings=$SETTINGS

echo "==> migrate"
python manage.py migrate --settings=$SETTINGS

echo "==> seed_superuser"
python manage.py seed_superuser --settings=$SETTINGS

echo "==> seed_wagtail"
python manage.py seed_wagtail --settings=$SETTINGS

echo "==> seed_centro"
python manage.py seed_centro --settings=$SETTINGS

echo "==> setup_flywheel"
python manage.py setup_flywheel --settings=$SETTINGS

echo "==> collectstatic"
python manage.py collectstatic --noinput --settings=$SETTINGS

echo "==> run_scheduler (background)"
python manage.py run_scheduler --settings=$SETTINGS &

echo "==> gunicorn"
exec gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
