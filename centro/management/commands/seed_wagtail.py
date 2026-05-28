from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from home.models import HomePage


class Command(BaseCommand):
    help = 'Crea HomePage de Wagtail y configura el Site (idempotente)'

    def handle(self, *args, **options):
        # Si ya existe HomePage viva, solo verificar Site
        home = HomePage.objects.filter(live=True).first()
        if home:
            self._ensure_site(home)
            self.stdout.write(self.style.SUCCESS(f'seed_wagtail: HomePage OK (id={home.id})'))
            return

        # Raíz del árbol Wagtail (siempre depth=1 tras migrate)
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR('seed_wagtail: root page no existe — migrate primero'))
            return

        home = HomePage(
            title='Endonautas',
            slug='home',
            live=True,
            tagline='Conoce tu mundo interior con profundidad real',
            cta_app_text='Comenzar el viaje',
            cta_app_url='https://app.endonautas.cl',
            cta_ebook_text='Descargar Endonautica',
            cta_ebook_url='https://ebook.endonautas.cl',
        )
        root.add_child(instance=home)
        home.save_revision().publish()

        self._ensure_site(home)
        self.stdout.write(self.style.SUCCESS(f'seed_wagtail: HomePage creada y publicada (id={home.id})'))

    def _ensure_site(self, home_page):
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                'hostname': 'endonautas.cl',
                'port': 443,
                'site_name': 'Endonautas',
                'root_page': home_page,
            }
        )
