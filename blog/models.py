import datetime
import json

from django.conf import settings
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

    # Author info (optional MirrorWork user link)
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

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_submissions')
    title       = models.CharField('Título', max_length=200)
    body        = models.TextField('Texto')
    source_type = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_FREE)

    # Solo uno de estos estará activo según source_type
    espejo_session = models.ForeignKey('mirror.ConflictSession',   null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_submissions')
    test_result    = models.ForeignKey('psychometrics.TestResult', null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_submissions')
    birth_report   = models.ForeignKey('birth.BirthReport',       null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_submissions')

    status         = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    reviewer_notes = models.TextField('Notas del revisor', blank=True)
    blog_post      = models.OneToOneField('blog.BlogPost', null=True, blank=True, on_delete=models.SET_NULL, related_name='submission')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Postulación al Blog'
        verbose_name_plural = 'Postulaciones al Blog'

    def __str__(self):
        return f'{self.user.email} — {self.title[:60]} [{self.status}]'

    @property
    def is_editable(self):
        return self.status in (self.STATUS_DRAFT, self.STATUS_REJECTED)

    def source_label(self):
        if self.espejo_session:
            return f'Espejo: {self.espejo_session.title or self.espejo_session.conflict_description[:50]}'
        if self.test_result:
            return f'Test: {self.test_result.test.name}'
        if self.birth_report:
            return f'Nacimiento: {self.birth_report.get_report_type_display()}'
        return 'Texto libre'
