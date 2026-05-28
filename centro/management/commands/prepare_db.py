from django.core.management.base import BaseCommand
from django.db import connection, ProgrammingError


class Command(BaseCommand):
    help = 'Detecta y corrige estado de migraciones inconsistente (registros sin tablas)'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'auth_user'
                    )
                """)
                auth_user_exists = cursor.fetchone()[0]
            except ProgrammingError:
                auth_user_exists = False

            if not auth_user_exists:
                self.stdout.write(self.style.WARNING(
                    'prepare_db: auth_user ausente — limpiando django_migrations para re-migrar'
                ))
                try:
                    cursor.execute("DELETE FROM django_migrations")
                except ProgrammingError:
                    pass  # django_migrations tampoco existe — base de datos vacía
            else:
                self.stdout.write(self.style.SUCCESS('prepare_db: estado de BD OK'))
