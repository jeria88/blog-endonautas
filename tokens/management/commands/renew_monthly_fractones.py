"""
python3 manage.py renew_monthly_fractones

Renueva el bolsillo mensual de todos los usuarios con plan activo
cuya última renovación fue hace más de 28 días.
Correr en cron el día 1 de cada mes (Railway Cron Jobs).
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from tokens.models import TokenBalance
from tokens.service import renew_monthly


class Command(BaseCommand):
    help = 'Renueva fractones mensuales para todos los usuarios con plan activo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Renovar sin verificar fecha de última renovación'
        )

    def handle(self, *args, **options):
        force = options['force']
        cutoff = date.today() - timedelta(days=28)
        renewed = 0

        balances = TokenBalance.objects.select_related('user__profile').all()
        for b in balances:
            try:
                plan = b.user.profile.plan
            except Exception:
                continue
            if plan == 'free':
                continue
            if not force and b.monthly_last_renewed and b.monthly_last_renewed > cutoff:
                continue
            renew_monthly(b.user)
            renewed += 1

        self.stdout.write(self.style.SUCCESS(f'Renovados: {renewed} usuarios'))
