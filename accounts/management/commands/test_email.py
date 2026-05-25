from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Envía un email de prueba para verificar configuración SMTP'

    def add_arguments(self, parser):
        parser.add_argument('destinatario', type=str)

    def handle(self, *args, **options):
        dest = options['destinatario']
        self.stdout.write(f'EMAIL_HOST:      {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT:      {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'DEFAULT_FROM:    {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'Enviando a:      {dest}')
        try:
            send_mail(
                subject='Test email — MirrorWork',
                message='Si recibes esto, el SMTP está configurado correctamente.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[dest],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Email enviado sin errores.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: {type(e).__name__}: {e}'))
