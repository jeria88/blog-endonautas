from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Procesa pasos de secuencias vencidos. Diseñado para Railway Cron Jobs."

    def handle(self, *args, **options):
        from crm.tasks import _process_sequence_steps
        result = _process_sequence_steps()
        self.stdout.write(self.style.SUCCESS(result))
