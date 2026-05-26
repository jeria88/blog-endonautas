from django.core.management.base import BaseCommand
from accounts.models import User, UserProfile
from tokens.models import TokenBalance, TokenTransaction


class Command(BaseCommand):
    help = 'Crea usuario admin de testing si no existe'

    def handle(self, *args, **options):
        import os
        email = os.environ.get('ADMIN_EMAIL', 'fjeriacastro@gmail.com')
        password = os.environ.get('ADMIN_PASSWORD', 'Mirror2026!')

        u, created = User.objects.get_or_create(email=email, defaults={
            'username': 'admin',
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            u.set_password(password)
            u.save()
            self.stdout.write(self.style.SUCCESS(f'Admin creado: {email}'))
        else:
            self.stdout.write(f'Admin ya existe: {email}')

        profile, _ = UserProfile.objects.get_or_create(user=u)
        if profile.plan != 'empresa':
            profile.plan = 'empresa'
            profile.save()

        balance, _ = TokenBalance.objects.get_or_create(user=u)
        if balance.permanent < 999999:
            balance.permanent = 999999
            balance.save()
            TokenTransaction.objects.create(user=u, amount=999999, reason='Admin test — ilimitado')
