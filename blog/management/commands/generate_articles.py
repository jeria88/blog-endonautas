"""
Comando para generar artículos de blog con IA.

Uso:
    python manage.py generate_articles                    # Genera 1 artículo de temas predefinidos
    python manage.py generate_articles --count 3          # Genera 3 artículos
    python manage.py generate_articles --topic "Mi tema"  # Genera sobre un tema específico
    python manage.py generate_articles --list             # Lista temas disponibles
    python manage.py generate_articles --approve-all      # Aprueba todos los borradores
"""
import logging

from django.core.management.base import BaseCommand, CommandError

from blog.models import GeneratedArticle
from blog.services import generate_article, generate_articles_batch, BLOG_TOPICS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Genera artículos de blog usando DeepSeek"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=1,
            help='Cantidad de artículos a generar (default: 1)',
        )
        parser.add_argument(
            '--topic', type=str, default=None,
            help='Tema específico para el artículo',
        )
        parser.add_argument(
            '--source-type', type=str, default='tema',
            choices=['test', 'espejo', 'tema', 'keyword'],
            help='Tipo de fuente (default: tema)',
        )
        parser.add_argument(
            '--list', action='store_true',
            help='Lista los temas predefinidos disponibles',
        )
        parser.add_argument(
            '--approve-all', action='store_true',
            help='Aprueba todos los artículos en estado draft',
        )
        parser.add_argument(
            '--status', action='store_true',
            help='Muestra estadísticas de artículos generados',
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_topics()
            return

        if options['approve_all']:
            self._approve_all()
            return

        if options['status']:
            self._show_status()
            return

        if options['topic']:
            self._generate_single(options['topic'], options['source_type'])
        else:
            self._generate_batch(options['count'], options['source_type'])

    def _list_topics(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Temas predefinidos para artículos:"))
        for i, topic in enumerate(BLOG_TOPICS, 1):
            self.stdout.write(f"  {i:2d}. {topic}")
        self.stdout.write(f"\nTotal: {len(BLOG_TOPICS)} temas")

    def _generate_single(self, topic, source_type):
        self.stdout.write(f"Generando artículo: {topic}...")
        try:
            article = generate_article(topic, source_type=source_type)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Creado: {article.title}"))
            self.stdout.write(f"    Slug: {article.slug}")
            self.stdout.write(f"    Status: {article.get_status_display()}")
            self.stdout.write(f"    Admin: /admin/blog/generatedarticle/{article.pk}/change/")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error: {e}"))
            raise CommandError(f"Error generando artículo: {e}")

    def _generate_batch(self, count, source_type):
        # Seleccionar temas que no tengan artículos generados
        existing_slugs = set(GeneratedArticle.objects.values_list('slug', flat=True))
        available_topics = []
        for topic in BLOG_TOPICS:
            from django.utils.text import slugify
            slug = slugify(topic)[:200]
            if slug not in existing_slugs:
                available_topics.append(topic)

        if not available_topics:
            self.stdout.write(self.style.WARNING("Todos los temas predefinidos ya tienen artículos generados."))
            self.stdout.write("Usa --topic para generar sobre un tema específico.")
            return

        topics_to_generate = available_topics[:count]
        self.stdout.write(f"Generando {len(topics_to_generate)} artículo(s)...")

        created = 0
        for topic in topics_to_generate:
            try:
                article = generate_article(topic, source_type=source_type)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {article.title}"))
                created += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  ✗ {topic[:50]}...: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n{created} artículo(s) generado(s)."))
        self.stdout.write("Revisa y aprueba en: /admin/blog/generatedarticle/")

    def _approve_all(self):
        drafts = GeneratedArticle.objects.filter(status=GeneratedArticle.STATUS_DRAFT)
        count = drafts.count()
        if count == 0:
            self.stdout.write("No hay artículos en borrador.")
            return
        drafts.update(status=GeneratedArticle.STATUS_REVIEW)
        self.stdout.write(self.style.SUCCESS(f"{count} artículo(s) movido(s) a 'En revisión'."))

    def _show_status(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Estadísticas de artículos generados:"))
        for status, label in GeneratedArticle.STATUS_CHOICES:
            count = GeneratedArticle.objects.filter(status=status).count()
            self.stdout.write(f"  {label}: {count}")
        total = GeneratedArticle.objects.count()
        self.stdout.write(f"  Total: {total}")
