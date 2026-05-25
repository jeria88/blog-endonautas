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
