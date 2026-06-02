"""
Fix Wagtail Site configuration.
Run once: python manage.py fix_wagtail_site
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site, Page


class Command(BaseCommand):
    help = "Crea/actualiza el Site de Wagtail para que las páginas tengan URL"

    def handle(self, *args, **options):
        # Find the home page (depth=2, first child of root)
        home = Page.objects.filter(depth=2).first()
        if not home:
            self.stderr.write("ERROR: No se encontró página de inicio (depth=2)")
            return

        self.stdout.write(f"Home page encontrada: '{home.title}' (id={home.id}, slug={home.slug})")

        # Check existing sites
        site = Site.objects.filter(is_default_site=True).first()

        if site:
            old_root = site.root_page
            site.root_page = home
            site.hostname = "endonautas.cl"
            site.port = 443
            site.site_name = "Endonautas"
            site.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Site actualizado: hostname={site.hostname}, "
                    f"root_page: '{old_root}' → '{home.title}'"
                )
            )
        else:
            site = Site.objects.create(
                hostname="endonautas.cl",
                port=443,
                root_page=home,
                site_name="Endonautas",
                is_default_site=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Site creado: hostname={site.hostname}, root_page='{home.title}'"
                )
            )

        # Verify child pages
        children = home.get_children().live()
        self.stdout.write(f"\nPáginas hijas de '{home.title}':")
        for child in children:
            url = child.url
            self.stdout.write(f"  - {child.title}: {url}")

        self.stdout.write(self.style.SUCCESS("\nListo. Las páginas deberían tener URL ahora."))
