"""
Servicio para enviar notificaciones a Telegram via webhook de Hermes.
Hermes ya tiene el canal de Telegram configurado y conoce el chat_id.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(text, parse_mode='Markdown'):
    """
    Envía un mensaje a Telegram via el webhook de Hermes.
    Hermes se encarga de entregarlo al chat correcto.
    """
    webhook_url = getattr(settings, 'HERMES_WEBHOOK_URL', None)
    if not webhook_url:
        # Fallback: intentar via API directa de Telegram si hay token
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        if bot_token and chat_id:
            return _send_telegram_api(bot_token, chat_id, text, parse_mode)
        logger.warning("No hay HERMES_WEBHOOK_URL ni TELEGRAM_BOT_TOKEN configurado")
        return False

    try:
        resp = requests.post(
            webhook_url,
            json={'message': text, 'parse_mode': parse_mode},
            timeout=10
        )
        return resp.ok
    except Exception as e:
        logger.error(f"Error enviando a Hermes webhook: {e}")
        return False


def _send_telegram_api(bot_token, chat_id, text, parse_mode='Markdown'):
    """Fallback: envía via API directa de Telegram."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.ok
    except Exception as e:
        logger.error(f"Error enviando a Telegram API: {e}")
        return False


def format_post_for_telegram(article, platform='instagram', download_url=None, zip_url=None):
    """
    Formatea un post completo para enviar por Telegram.
    """
    title = article.title
    intro = article.intro or ''
    cta = article.cta_text or 'Descubrí más en endonautas.cl'
    cta_url = article.cta_url or 'https://endonautas.cl'
    tags = article.tags or 'endonautas'

    platform_emoji = {'instagram': '📸', 'tiktok': '🎵', 'linkedin': '💼'}.get(platform, '📱')
    platform_name = {'instagram': 'Instagram', 'tiktok': 'TikTok', 'linkedin': 'LinkedIn'}.get(platform, 'Redes')

    msg = f"""{platform_emoji} *Post listo para {platform_name}*

*📰 {title}*

{intro}

{cta} → {cta_url}

`#{tags.replace(',', ' #').replace(' ', '')}`

━━━━━━━━━━━━━━━━━━
"""

    if zip_url:
        msg += f"📦 *ZIP con todas las slides:* {zip_url}\n\n"
    if download_url:
        msg += f"🖼️ *Slides individuales:* {download_url}\n\n"

    msg += "✅ *Listo para publicar* — Abrí el link, descargá el ZIP, y subí las imágenes con el caption de arriba."

    return msg
