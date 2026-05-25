"""
Hotmart webhook processing.

Suscripciones (offer_code en HOTMART_OFFER_PLAN_MAP):
  PURCHASE_APPROVED / PURCHASE_COMPLETE → activar plan + recarga mensual
  PURCHASE_REFUNDED / CHARGEBACK / CANCELED / SUBSCRIPTION_CANCELLATION → bajar a free

Packs de fractones (offer_code en HOTMART_PACK_MAP):
  PURCHASE_APPROVED / PURCHASE_COMPLETE → acreditar fractones permanentes
"""
import logging
from datetime import date

from django.conf import settings

logger = logging.getLogger(__name__)

ACTIVATE_EVENTS = {'PURCHASE_APPROVED', 'PURCHASE_COMPLETE'}
REVOKE_EVENTS   = {
    'PURCHASE_REFUNDED',
    'PURCHASE_CHARGEBACK',
    'PURCHASE_CANCELED',
    'SUBSCRIPTION_CANCELLATION',
}


def _get_user(email):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.filter(email__iexact=email.strip()).first()


def activate_plan(user, plan, subscriber_code=''):
    from accounts.models import UserProfile
    from tokens.service import renew_monthly

    profile, _ = UserProfile.objects.get_or_create(user=user)
    old_plan = profile.plan
    profile.plan = plan
    profile.plan_active_since = date.today()
    if subscriber_code:
        profile.hotmart_subscriber_code = subscriber_code
    profile.save()

    renew_monthly(user)
    logger.info(f'[Hotmart] {user.email}: {old_plan} → {plan}')


def revoke_plan(user, reason=''):
    from accounts.models import UserProfile

    profile = UserProfile.objects.filter(user=user).first()
    if not profile or profile.plan == 'free':
        return
    old = profile.plan
    profile.plan = 'free'
    profile.hotmart_subscriber_code = ''
    profile.save()
    logger.info(f'[Hotmart] {user.email}: {old} → free ({reason})')


def process_webhook(payload):
    """Retorna (ok: bool, message: str)."""
    event       = payload.get('event', '')
    data        = payload.get('data', {})
    buyer_email = (data.get('buyer') or {}).get('email', '').strip().lower()
    offer_code  = str((data.get('purchase') or {}).get('offer', {}).get('code', ''))
    sub_data    = data.get('subscription') or {}
    subscriber_code = (sub_data.get('subscriber') or {}).get('code', '')

    if not buyer_email:
        return True, 'no buyer email — ignored'

    user = _get_user(buyer_email)
    if not user:
        logger.warning(f'[Hotmart] {event}: no user for {buyer_email}')
        return True, f'user {buyer_email} not found'

    if event in ACTIVATE_EVENTS:
        # ¿Es un pack de fractones?
        pack_fractones = settings.HOTMART_PACK_MAP.get(offer_code)
        if pack_fractones:
            from tokens.service import credit_pack
            credit_pack(user, pack_fractones, offer_code=offer_code)
            logger.info(f'[Hotmart] pack {pack_fractones} fractones → {buyer_email}')
            return True, f'pack {pack_fractones} fractones credited to {buyer_email}'

        # ¿Es una suscripción de plan?
        plan = settings.HOTMART_OFFER_PLAN_MAP.get(offer_code)
        if plan:
            activate_plan(user, plan, subscriber_code=subscriber_code)
            return True, f'plan {plan} activated for {buyer_email}'

        logger.warning(f'[Hotmart] offer {offer_code} not mapped')
        return True, f'offer {offer_code} not mapped'

    if event in REVOKE_EVENTS:
        revoke_plan(user, reason=event)
        return True, f'plan revoked for {buyer_email} ({event})'

    return True, f'event {event} ignored'
