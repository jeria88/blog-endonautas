"""
Comando para traer eventos de email desde la API de Brevo.

Uso:
    python manage.py fetch_brevo_events       # Trae eventos de las últimas 24h
    python manage.py fetch_brevo_events --days 7  # Trae eventos de los últimos 7 días

Programar con celery beat o cron para correr cada 15-30 minutos.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests

from crm.models import EmailEvent, SentEmail, Subscriber

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brebo.com/v3/smtp/activities"


class Command(BaseCommand):
    help = "Trae eventos de apertura/click/bounce desde la API de Brevo y los guarda en la BD"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Cantidad de días hacia atrás para traer eventos (default: 1)",
        )

    def handle(self, *args, **options):
        api_key = getattr(settings, "BREVO_API_KEY", None)
        if not api_key:
            self.stderr.write(self.style.ERROR("BREVO_API_KEY no configurada"))
            return

        days = options["days"]
        date_from = (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")

        self.stdout.write(f"Consultando eventos de Brevo desde {date_from}...")

        headers = {
            "api-key": api_key,
            "Accept": "application/json",
        }

        params = {
            "limit": 100,
            "offset": 0,
            "startDate": date_from,
            "event": "opened,clicked,bounced,unsubscribed,delivered",
        }

        total_fetched = 0
        total_saved = 0

        while True:
            try:
                resp = requests.get(BREVO_API_URL, headers=headers, params=params, timeout=30)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error consultando API: {e}"))
                return

            if resp.status_code != 200:
                self.stderr.write(self.style.ERROR(f"API error {resp.status_code}: {resp.text[:200]}"))
                return

            data = resp.json()
            activities = data if isinstance(data, list) else data.get("activities", data.get("data", []))

            if not activities:
                break

            total_fetched += len(activities)

            for activity in activities:
                saved = self._process_activity(activity)
                if saved:
                    total_saved += 1

            # Paginación
            if len(activities) < params["limit"]:
                break
            params["offset"] += params["limit"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo. {total_fetched} eventos consultados, {total_saved} nuevos guardados."
            )
        )

    def _process_activity(self, activity):
        """Procesa un evento de la API de Brevo. Retorna True si se guardó."""
        email = activity.get("email", "").strip().lower()
        event_type = self._map_event_type(activity.get("event", ""))
        occurred_at = activity.get("date", activity.get("timestamp", ""))

        if not email or not event_type:
            return False

        # Buscar suscriptor
        try:
            subscriber = Subscriber.objects.filter(email__iexact=email).first()
            if not subscriber:
                return False
        except Exception:
            return False

        # Buscar el SentEmail asociado (por message-id o email+fecha)
        sent_email = None
        message_id = activity.get("messageId", activity.get("message_id", ""))
        if message_id:
            sent_email = SentEmail.objects.filter(
                subscriber=subscriber,
                brevo_message_id=message_id,
            ).first()

        # Si no se encontró por message_id, buscar por fecha aproximada
        if not sent_email and occurred_at:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(occurred_at) if isinstance(occurred_at, str) else occurred_at
                if dt:
                    # Buscar un sent_email de los últimos 7 días para este suscriptor
                    sent_email = SentEmail.objects.filter(
                        subscriber=subscriber,
                        sent_at__gte=dt - timedelta(days=7),
                        sent_at__lte=dt + timedelta(hours=1),
                        status="sent",
                    ).order_by("-sent_at").first()
            except Exception:
                pass

        # Evitar duplicados
        if EmailEvent.objects.filter(
            subscriber=subscriber,
            event_type=event_type,
            occurred_at=occurred_at,
        ).exists():
            return False

        # Parsear fecha
        try:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(occurred_at) if isinstance(occurred_at, str) else occurred_at
            if not dt:
                dt = timezone.now()
        except Exception:
            dt = timezone.now()

        # Metadatos adicionales
        metadata = {}
        if "link" in activity:
            metadata["link"] = activity["link"]
        if "ip" in activity:
            metadata["ip"] = activity["ip"]
        if "userAgent" in activity:
            metadata["user_agent"] = activity["userAgent"]

        EmailEvent.objects.create(
            subscriber=subscriber,
            sent_email=sent_email,
            event_type=event_type,
            metadata=metadata,
            occurred_at=dt,
        )

        return True

    def _map_event_type(self, brevo_event):
        """Mapea el tipo de evento de Brevo al nuestro."""
        mapping = {
            "opened": "opened",
            "click": "clicked",
            "clicked": "clicked",
            "bounce": "bounced",
            "bounced": "bounced",
            "softBounce": "bounced",
            "hardBounce": "bounced",
            "unsubscribed": "unsubscribed",
            "unsubscribe": "unsubscribed",
            "delivered": "delivered",
            "spam": "spam",
            "complaint": "spam",
        }
        return mapping.get(brevo_event, "")
