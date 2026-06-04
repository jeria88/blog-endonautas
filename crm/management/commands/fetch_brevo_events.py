"""
Comando para traer eventos de email desde la API de Brevo.

Uso:
    python manage.py fetch_brevo_events       # Trae eventos de las últimas 24h
    python manage.py fetch_brevo_events --days 7  # Trae eventos de los últimos 7 días
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests

from crm.models import EmailEvent, SentEmail, Subscriber

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/emails"

# Brevo event param values (singular, not comma-separated)
BREVO_EVENTS = ["opened", "clicks", "bounces", "unsubscribed", "delivered"]


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
        date_from = (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        total_fetched = 0
        total_saved = 0

        headers = {
            "api-key": api_key,
            "Accept": "application/json",
        }

        for brevo_event in BREVO_EVENTS:
            params = {
                "limit": 100,
                "offset": 0,
                "startDate": date_from,
                "event": brevo_event,
                "sort": "desc",
            }

            while True:
                try:
                    resp = requests.get(BREVO_API_URL, headers=headers, params=params, timeout=30)
                except Exception as e:
                    logger.error(f"[fetch_brevo_events] Error consultando API ({brevo_event}): {e}")
                    break

                if resp.status_code != 200:
                    logger.error(f"API error {resp.status_code}: {resp.text[:200]}")
                    break

                data = resp.json()
                activities = data.get("transactionalEmails", [])

                if not activities:
                    break

                total_fetched += len(activities)

                for activity in activities:
                    saved = self._process_activity(activity)
                    if saved:
                        total_saved += 1

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
        occurred_at = activity.get("date", "")

        if not email or not event_type:
            return False

        try:
            subscriber = Subscriber.objects.filter(email__iexact=email).first()
            if not subscriber:
                return False
        except Exception:
            return False

        sent_email = None
        message_id = activity.get("messageId", "")
        if message_id:
            sent_email = SentEmail.objects.filter(
                subscriber=subscriber,
                brevo_message_id=message_id,
            ).first()

        if not sent_email and occurred_at:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(occurred_at) if isinstance(occurred_at, str) else occurred_at
                if dt:
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

        try:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(occurred_at) if isinstance(occurred_at, str) else occurred_at
            if not dt:
                dt = timezone.now()
        except Exception:
            dt = timezone.now()

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
        mapping = {
            "opened": "opened",
            "clicks": "clicked",
            "click": "clicked",
            "clicked": "clicked",
            "bounces": "bounced",
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
