import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea superusuario si no existe (idempotente). Lee DJANGO_SUPERUSER_* de env vars.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'seed_superuser: DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD no definidas — saltando'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'seed_superuser: {username} ya existe'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'seed_superuser: superusuario {username} creado'))
