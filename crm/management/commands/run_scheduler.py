import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)

MAIL_INTERVAL = 300    # 5 minutos
FLYWHEEL_INTERVAL = 3600  # 1 hora


class Command(BaseCommand):
    help = "Scheduler interno: despacha emails cada 5 min y procesa secuencias cada hora."

    def handle(self, *args, **options):
        self.stdout.write("Scheduler iniciado.")
        last_flywheel = 0

        while True:
            now = time.time()
            try:
                call_command("send_queued_mail", "--settings=config.settings.production")
            except Exception as e:
                logger.error(f"send_queued_mail error: {e}")

            if now - last_flywheel >= FLYWHEEL_INTERVAL:
                try:
                    call_command("run_flywheel")
                    last_flywheel = now
                except Exception as e:
                    logger.error(f"run_flywheel error: {e}")

            time.sleep(MAIL_INTERVAL)
