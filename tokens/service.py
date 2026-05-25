"""
API pública para gastar y acreditar fractones desde otras apps.

Uso:
    from tokens.service import spend, credit_mission, complete_onboarding

    ok = spend(user, 'espejo_exchange')   # True si hay saldo, False si no
    credit_mission(user, 'onboarding')
"""
from django.conf import settings


def _balance(user):
    from tokens.models import TokenBalance
    b, _ = TokenBalance.objects.get_or_create(user=user, defaults={'permanent': 0, 'monthly': 0})
    return b


def spend(user, cost_key, reason=None):
    """
    Descuenta fractones según TOKEN_COSTS[cost_key].
    Retorna True si el gasto fue exitoso, False si saldo insuficiente.
    """
    amount = settings.TOKEN_COSTS.get(cost_key, 0)
    if amount == 0:
        return True
    label = reason or cost_key.replace('_', ' ').capitalize()
    return _balance(user).spend(amount, reason=label)


def has_balance(user, cost_key):
    """Verifica si el usuario puede pagar cost_key sin descontar."""
    amount = settings.TOKEN_COSTS.get(cost_key, 0)
    return _balance(user).balance >= amount


def credit_mission(user, slug):
    """Completa una misión verificando prerequisito (idempotente). Retorna True si se completó ahora."""
    from tokens.models import Mission, MissionCompletion
    try:
        mission = Mission.objects.get(slug=slug, active=True)
    except Mission.DoesNotExist:
        return False
    if mission.prerequisite_slug:
        if not MissionCompletion.objects.filter(user=user, mission__slug=mission.prerequisite_slug).exists():
            return False
    _, created = MissionCompletion.objects.get_or_create(user=user, mission=mission)
    if created and mission.fracton_reward:
        _balance(user).credit_permanent(mission.fracton_reward, reason=f'Misión: {mission.name}')
    return created


def credit_pack(user, fractones, offer_code=''):
    """Acredita fractones de un pack Hotmart (pago único → permanente)."""
    _balance(user).credit_permanent(fractones, reason=f'Pack Hotmart {offer_code}')


def renew_monthly(user):
    """
    Renueva el bolsillo mensual según el plan activo.
    Llamar desde el webhook de Hotmart y desde el cron mensual.
    """
    try:
        plan = user.profile.plan
    except Exception:
        plan = 'free'
    amount = settings.TOKEN_PLANS.get(plan, {}).get('monthly_fractones', 0)
    if amount:
        _balance(user).credit_monthly(amount, reason=f'Recarga mensual plan {plan}')
