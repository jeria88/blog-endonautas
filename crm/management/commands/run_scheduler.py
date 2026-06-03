"""
Scheduler interno del flywheel.

Corre como proceso en background dentro del container (ver scripts/start.sh).
No requiere Celery, Redis, ni Railway Cron Jobs externos.

Intervalos:
  - run_flywheel:     cada hora  (3600 s) — procesa pasos de secuencia vencidos
  - send_queued_mail: cada 5 min (300 s)  — despacha la cola de post_office al SMTP
"""
import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)

FLYWHEEL_INTERVAL = 3600   # 1 hora
MAIL_INTERVAL = 300        # 5 minutos
TICK = 60                  # revisión cada 60 s


class Command(BaseCommand):
    help = "Scheduler interno — iniciar en background antes de gunicorn (ver scripts/start.sh)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Ejecutar ambos jobs una sola vez y salir (útil para testing)",
        )

    def handle(self, *args, **options):
        if options["once"]:
            self._run_flywheel()
            self._run_queued_mail()
            return

        self.stdout.write("Scheduler iniciado (flywheel=1h, mail=5min).")

        # Arrancar inmediatamente en el primer tick
        last_flywheel = 0.0
        last_mail = 0.0

        while True:
            now = time.monotonic()

            if now - last_flywheel >= FLYWHEEL_INTERVAL:
                self._run_flywheel()
                last_flywheel = now

            if now - last_mail >= MAIL_INTERVAL:
                self._run_queued_mail()
                last_mail = now

            time.sleep(TICK)

    def _run_flywheel(self):
        try:
            from crm.tasks import _process_sequence_steps
            result = _process_sequence_steps()
            logger.info(f"[scheduler] flywheel: {result}")
            self.stdout.write(f"[flywheel] {result}")
        except Exception as e:
            logger.error(f"[scheduler] flywheel error: {e}", exc_info=True)
            self.stderr.write(f"[flywheel] ERROR: {e}")

    def _run_queued_mail(self):
        """Respaldo: despacha emails encolados en post_office (si los hay)."""
        try:
            call_command("send_queued_mail", verbosity=0)
        except Exception as e:
            logger.debug(f"[scheduler] send_queued_mail (respaldo): {e}")
