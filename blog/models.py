import datetime
import json

from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import RichTextBlock, CharBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['posts'] = BlogPost.objects.live().order_by('-first_published_at')
        return ctx

    class Meta:
        verbose_name = 'Índice del Blog'


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPost', related_name='tagged_items', on_delete=models.CASCADE)


class BlogPost(Page):
    date = models.DateField('Fecha de publicación', default=datetime.date.today)
    intro = models.CharField(max_length=280, blank=True)
    body = StreamField([
        ('richtext', RichTextBlock(label='Texto')),
        ('imagen', ImageChooserBlock(label='Imagen')),
    ], use_json_field=True, blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    cta_text = models.CharField('Texto del CTA', max_length=80, blank=True)
    cta_url = models.URLField('URL del CTA', blank=True)

    author_name = models.CharField(max_length=120, blank=True)
    is_community = models.BooleanField('Publicado por la comunidad', default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('intro'),
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading='Información'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('cta_text'),
            FieldPanel('cta_url'),
        ], heading='Llamada a la acción'),
        MultiFieldPanel([
            FieldPanel('author_name'),
            FieldPanel('is_community'),
        ], heading='Autoría'),
    ]

    def get_structured_data(self):
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "description": self.intro,
            "datePublished": self.first_published_at.isoformat() if self.first_published_at else '',
            "author": {
                "@type": "Person" if self.author_name else "Organization",
                "name": self.author_name or "Endonautas",
            },
            "publisher": {
                "@type": "Organization",
                "name": "Endonautas",
                "url": "https://endonautas.cl",
            },
            "isPartOf": {
                "@type": "WebSite",
                "name": "Endonautas",
                "url": "https://endonautas.cl",
            }
        }

    def get_structured_data_json(self):
        return json.dumps(self.get_structured_data(), ensure_ascii=False)

    class Meta:
        verbose_name = 'Artículo del Blog'


class BlogSubmission(models.Model):
    SOURCE_ESPEJO = 'espejo'
    SOURCE_TEST   = 'test'
    SOURCE_BIRTH  = 'birth'
    SOURCE_FREE   = 'free'
    SOURCE_CHOICES = [
        (SOURCE_ESPEJO, 'Sesión del Espejo'),
        (SOURCE_TEST,   'Resultado de Test'),
        (SOURCE_BIRTH,  'Lectura de Nacimiento'),
        (SOURCE_FREE,   'Texto libre'),
    ]

    STATUS_DRAFT     = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_APPROVED  = 'approved'
    STATUS_REJECTED  = 'rejected'
    STATUS_CHOICES = [
        (STATUS_DRAFT,     'Borrador'),
        (STATUS_SUBMITTED, 'En revisión'),
        (STATUS_APPROVED,  'Aprobado'),
        (STATUS_REJECTED,  'Rechazado'),
    ]

    author_email       = models.EmailField('Email del autor')
    author_name        = models.CharField('Nombre del autor', max_length=120, blank=True)
    title              = models.CharField('Título', max_length=200)
    body               = models.TextField('Texto')
    source_type        = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_FREE)
    source_description = models.TextField('Descripción del origen', blank=True)
    status             = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    reviewer_notes     = models.TextField('Notas del revisor', blank=True)
    blog_post          = models.OneToOneField('blog.BlogPost', null=True, blank=True, on_delete=models.SET_NULL, related_name='submission')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Postulación al Blog'
        verbose_name_plural = 'Postulaciones al Blog'

    def __str__(self):
        return f'{self.author_email} — {self.title[:60]} [{self.status}]'

    @property
    def is_editable(self):
        return self.status in (self.STATUS_DRAFT, self.STATUS_REJECTED)


# ── Artículos generados por IA ────────────────────────────────────────────────

class GeneratedArticle(models.Model):
    """Artículo generado por IA para revisión antes de publicar en el blog."""
    STATUS_DRAFT     = 'draft'
    STATUS_REVIEW    = 'review'
    STATUS_APPROVED  = 'approved'
    STATUS_PUBLISHED = 'published'
    STATUS_REJECTED  = 'rejected'
    STATUS_CHOICES = [
        (STATUS_DRAFT,     'Borrador'),
        (STATUS_REVIEW,    'En revisión'),
        (STATUS_APPROVED,  'Aprobado'),
        (STATUS_PUBLISHED, 'Publicado'),
        (STATUS_REJECTED,  'Rechazado'),
    ]

    title         = models.CharField('Título', max_length=200)
    slug          = models.SlugField('Slug', max_length=200, unique=True)
    meta_description = models.CharField('Meta description', max_length=160, blank=True)
    keywords      = models.CharField('Keywords', max_length=300, blank=True, help_text="Separadas por coma")
    intro         = models.CharField('Introducción', max_length=280, blank=True)
    body          = models.TextField('Contenido (HTML)')
    cta_text      = models.CharField('Texto del CTA', max_length=80, blank=True)
    cta_url       = models.URLField('URL del CTA', blank=True)
    tags          = models.CharField('Tags', max_length=300, blank=True, help_text="Separados por coma")

    source_type   = models.CharField(max_length=20, choices=[
        ('test',    'Basado en test'),
        ('espejo',  'Basado en Espejo'),
        ('tema',    'Tema libre'),
        ('keyword', 'Keyword SEO'),
    ], default='tema')
    source_detail = models.CharField('Detalle de la fuente', max_length=200, blank=True)

    status        = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    blog_post     = models.OneToOneField('blog.BlogPost', null=True, blank=True, on_delete=models.SET_NULL, related_name='generated_article')
    reviewer_notes = models.TextField('Notas del revisor', blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    published_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Artículo generado'
        verbose_name_plural = 'Artículos generados'

    def __str__(self):
        return f'{self.title} [{self.get_status_display()}]'

    def publish_to_blog(self):
        """Publica este artículo como un BlogPost de Wagtail."""
        from wagtail.models import Page
        from blog.models import BlogPost, BlogIndexPage

        if self.status != self.STATUS_APPROVED:
            return False, 'El artículo debe estar aprobado para publicar'

        if self.blog_post:
            return False, 'Ya fue publicado'

        try:
            blog_index = BlogIndexPage.objects.live().first()
        except BlogIndexPage.DoesNotExist:
            return False, 'No se encontró el índice del blog'

        if not blog_index:
            return False, 'No se encontró el índice del blog'

        post = BlogPost(
            title=self.title,
            slug=self.slug,
            intro=self.intro or '',
            cta_text=self.cta_text or '',
            cta_url=self.cta_url or '',
            author_name='Endonautas',
        )
        post.body = [('richtext', self.body)]

        blog_index.add_child(instance=post)
        post.save_revision().publish()

        self.blog_post = post
        self.status = self.STATUS_PUBLISHED
        self.published_at = datetime.datetime.now()
        self.save(update_fields=['blog_post', 'status', 'published_at'])

        return True, f'Publicado: {post.full_url}'


# ── Contenido de RRSS ──────────────────────────────────────────────────────────

class SocialPost(models.Model):
    """Contenido de RRSS generado a partir de un artículo del blog."""

    generated_article = models.ForeignKey(
        GeneratedArticle, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='social_posts',
        help_text="Artículo generado por IA (opcional)"
    )
    blog_post = models.ForeignKey(
        BlogPost, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='social_posts',
        help_text="Artículo de Wagtail (opcional)"
    )

    # Copys generados
    copy_carrusel = models.TextField('Copy carrusel', blank=True,
        help_text="Texto para las slides del carrusel (un párrafo por slide, separados por ---)")
    copy_descripcion = models.TextField('Copy descripción', blank=True,
        help_text="Texto de la descripción del carrusel en Instagram")
    copy_reel_texto = models.TextField('Copy reel (texto en pantalla)', blank=True,
        help_text="Texto que aparece sobre el video del reel")
    copy_reel_descripcion = models.TextField('Copy reel (descripción)', blank=True,
        help_text="Descripción del reel que se lee mientras el video se reproduce en loop")

    # Plataforma y formato
    PLATAFORMA_INSTAGRAM = 'instagram'
    PLATAFORMA_TIKTOK = 'tiktok'
    PLATAFORMA_LINKEDIN = 'linkedin'
    PLATAFORMA_CHOICES = [
        (PLATAFORMA_INSTAGRAM, 'Instagram'),
        (PLATAFORMA_TIKTOK, 'TikTok'),
        (PLATAFORMA_LINKEDIN, 'LinkedIn'),
    ]
    plataforma = models.CharField(max_length=15, choices=PLATAFORMA_CHOICES, default=PLATAFORMA_INSTAGRAM)

    FORMATO_CARRUSEL = 'carrusel'
    FORMATO_REEL = 'reel'
    FORMATO_POST = 'post'
    FORMATO_CHOICES = [
        (FORMATO_CARRUSEL, 'Carrusel'),
        (FORMATO_REEL, 'Reel'),
        (FORMATO_POST, 'Post simple'),
    ]
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default=FORMATO_CARRUSEL)

    # Estado
    STATUS_DRAFT = 'draft'
    STATUS_READY = 'ready'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_READY, 'Listo para publicar'),
        (STATUS_PUBLISHED, 'Publicado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Assets generados
    carrusel_html_path = models.CharField(max_length=500, blank=True)
    carrusel_png_count = models.PositiveIntegerField(default=0)
    reel_video_path = models.CharField(max_length=500, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post de RRSS'
        verbose_name_plural = 'Posts de RRSS'

    def __str__(self):
        fuente = self.blog_post or self.generated_article
        fuente_titulo = fuente.title if fuente else 'Sin fuente'
        return f'[{self.plataforma}] {fuente_titulo} ({self.status})'

    @property
    def fuente_titulo(self):
        if self.blog_post:
            return self.blog_post.title
        if self.generated_article:
            return self.generated_article.title
        return 'Sin fuente'

    def get_slides_text(self):
        """Lista de textos para cada slide del carrusel."""
        if not self.copy_carrusel:
            return []
        return [s.strip() for s in self.copy_carrusel.split('---') if s.strip()]
