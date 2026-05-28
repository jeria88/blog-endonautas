from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Corrige BD inconsistente (tablas parciales) reseteando el schema antes de migrar'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)

            if 'auth_user' in tables:
                self.stdout.write(self.style.SUCCESS('prepare_db: BD OK'))
                return

            self.stdout.write(self.style.WARNING(
                'prepare_db: auth_user ausente — reseteando schema public para migrate limpio'
            ))
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
            cursor.execute("GRANT ALL ON SCHEMA public TO public")
            self.stdout.write(self.style.SUCCESS('prepare_db: schema reseteado'))
