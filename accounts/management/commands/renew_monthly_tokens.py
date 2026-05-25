from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserProfile
from tokens.models import TokenBalance, TokenTransaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Renueva tokens mensuales para usuarios con plan activo'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        hace_30 = hoy - timedelta(days=30)
        renovados = 0
        omitidos = 0

        planes_pagados = ('navegante', 'practicante', 'empresa')
        perfiles = UserProfile.objects.filter(plan__in=planes_pagados).select_related('user')

        for perfil in perfiles:
            if perfil.tokens_last_renewed and perfil.tokens_last_renewed > hace_30:
                omitidos += 1
                continue

            config = settings.TOKEN_PLANS.get(perfil.plan, {})
            monthly = config.get('monthly_tokens', 0)
            if not monthly:
                continue

            balance, _ = TokenBalance.objects.get_or_create(
                user=perfil.user, defaults={'balance': 0}
            )
            balance.balance += monthly
            balance.save()
            TokenTransaction.objects.create(
                user=perfil.user,
                amount=monthly,
                reason=f'Renovación mensual — plan {perfil.plan}'
            )
            perfil.tokens_last_renewed = hoy
            perfil.save(update_fields=['tokens_last_renewed'])
            renovados += 1
            self.stdout.write(f'  ✓ {perfil.user.email}: +{monthly} tokens ({perfil.plan})')

        self.stdout.write(self.style.SUCCESS(
            f'\nRenovación completa: {renovados} renovados, {omitidos} omitidos.'
        ))
