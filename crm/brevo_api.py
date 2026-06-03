import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_via_brevo(subject, html_content, to_email, to_name="", plain_text=""):
    """Envía un email usando la API REST de Brevo (sin restricción de IP)."""
    api_key = settings.BREVO_API_KEY
    if not api_key:
        logger.error("BREVO_API_KEY no configurada")
        return False, "BREVO_API_KEY no configurada", ""

    payload = {
        "sender": {"name": "Endonautas", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": to_email, "name": to_name or to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }
    if plain_text:
        payload["textContent"] = plain_text

    try:
        resp = requests.post(
            BREVO_API_URL,
            json=payload,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            message_id = data.get("messageId", data.get("message_id", ""))
            logger.info(f"Brevo API OK: {subject} -> {to_email}")
            return True, "", message_id
        else:
            error = f"Brevo API error {resp.status_code}: {resp.text[:200]}"
            logger.error(error)
            return False, error, ""
    except requests.exceptions.Timeout:
        return False, "Timeout conectando con API de Brevo", ""
    except Exception as e:
        return False, str(e), ""
