import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Prueba la API REST de Brevo directamente'

    def add_arguments(self, parser):
        parser.add_argument('destinatario', type=str)

    def handle(self, *args, **options):
        api_key = getattr(settings, 'BREVO_API_KEY', '')
        self.stdout.write(f'BREVO_API_KEY configurada: {"SÍ (" + api_key[:8] + "...)" if api_key else "NO — FALTA"}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')

        if not api_key:
            self.stdout.write(self.style.ERROR('Sin API key no se puede enviar.'))
            return

        dest = options['destinatario']
        payload = {
            'sender': {'name': 'MirrorWork', 'email': 'hola@endonautas.cl'},
            'to': [{'email': dest}],
            'subject': 'Test API Brevo — MirrorWork',
            'textContent': 'Si recibes esto, la API REST de Brevo funciona correctamente.',
        }
        self.stdout.write(f'\nEnviando a: {dest}')
        self.stdout.write(f'Payload: {payload}')

        try:
            resp = requests.post(
                'https://api.brevo.com/v3/smtp/email',
                json=payload,
                headers={
                    'api-key': api_key,
                    'Content-Type': 'application/json',
                },
                timeout=15,
            )
            self.stdout.write(f'\nStatus: {resp.status_code}')
            self.stdout.write(f'Response: {resp.text}')
            if resp.status_code in (200, 201):
                self.stdout.write(self.style.SUCCESS('Email enviado correctamente.'))
            else:
                self.stdout.write(self.style.ERROR(f'Error de Brevo: {resp.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Excepción: {type(e).__name__}: {e}'))
