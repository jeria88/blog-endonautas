"""
Automatización de fractones:
  - Completar test          → +FRACTON_REWARDS['test_completed']
  - Completar dimensión     → +FRACTON_REWARDS['dimension_completed']  (bonus)
  - Streak semanal          → verificado al completar test
  - Misiones                → se evalúan tras cada evento relevante
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


def _get_or_create_balance(user):
    from tokens.models import TokenBalance
    balance, _ = TokenBalance.objects.get_or_create(user=user, defaults={'permanent': 0, 'monthly': 0})
    return balance


def _try_complete_mission(user, slug):
    from tokens.models import Mission, MissionCompletion
    try:
        mission = Mission.objects.get(slug=slug, active=True)
    except Mission.DoesNotExist:
        return
    _, created = MissionCompletion.objects.get_or_create(user=user, mission=mission)
    if created and mission.fracton_reward:
        balance = _get_or_create_balance(user)
        balance.credit_permanent(mission.fracton_reward, reason=f'Misión: {mission.name}')


def _check_weekly_streak(user):
    """Otorga bonus si el usuario completó ≥3 tests en los últimos 7 días."""
    from datetime import timedelta

    from django.utils import timezone

    from psychometrics.models import TestResult
    from tokens.models import TokenTransaction

    week_ago = timezone.now() - timedelta(days=7)
    recent = TestResult.objects.filter(user=user, completed_at__gte=week_ago).count()
    if recent < 3:
        return

    # Solo una vez por semana: verificar si ya se otorgó en los últimos 7 días
    already = TokenTransaction.objects.filter(
        user=user,
        reason='Streak semanal',
        created_at__gte=week_ago,
    ).exists()
    if not already:
        reward = settings.FRACTON_REWARDS.get('streak_weekly', 15)
        balance = _get_or_create_balance(user)
        balance.credit_permanent(reward, reason='Streak semanal')


def _check_dimension_complete(user, dimension):
    """Otorga bonus si el usuario completó todos los tests de una dimensión."""
    from psychometrics.models import Test, TestResult
    from tokens.models import TokenTransaction

    total = Test.objects.filter(dimension=dimension, active=True).count()
    if not total:
        return
    done = (
        TestResult.objects.filter(user=user, test__dimension=dimension)
        .values('test').distinct().count()
    )
    if done < total:
        return

    already = TokenTransaction.objects.filter(
        user=user,
        reason=f'Dimensión completa: {dimension}',
    ).exists()
    if not already:
        reward = settings.FRACTON_REWARDS.get('dimension_completed', 25)
        balance = _get_or_create_balance(user)
        balance.credit_permanent(reward, reason=f'Dimensión completa: {dimension}')


@receiver(post_save, sender='psychometrics.TestResult')
def on_test_completed(sender, instance, created, **kwargs):
    if not created or not instance.user:
        return

    reward = settings.FRACTON_REWARDS.get('test_completed', 8)
    balance = _get_or_create_balance(instance.user)
    balance.credit_permanent(reward, reason=f'Test completado: {instance.test.name}')

    _check_dimension_complete(instance.user, instance.test.dimension)
    _check_weekly_streak(instance.user)

    _try_complete_mission(instance.user, 'first_test')
    _try_complete_mission(instance.user, 'first_dimension')


@receiver(post_save, sender='mirror.ConflictSession')
def on_session_archived(sender, instance, **kwargs):
    if not instance.user or instance.status != 'archived':
        return
    from mirror.models import ConflictSession
    from tokens.service import credit_mission
    count = ConflictSession.objects.filter(user=instance.user, status='archived').count()
    if count >= 3:
        credit_mission(instance.user, 'multi_sesion_espejo')
