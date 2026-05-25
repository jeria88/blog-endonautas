from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
import json


class HomePage(Page):
    tagline = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)
    cta_app_text = models.CharField(max_length=80, default='Comenzar el viaje')
    cta_app_url = models.URLField(default='https://app.endonautas.cl')
    cta_ebook_text = models.CharField(max_length=80, default='Descargar Endonautica')
    cta_ebook_url = models.URLField(default='https://ebook.endonautas.cl')

    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        FieldPanel('intro'),
        FieldPanel('cta_app_text'),
        FieldPanel('cta_app_url'),
        FieldPanel('cta_ebook_text'),
        FieldPanel('cta_ebook_url'),
    ]

    def get_structured_data_json(self):
        data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Endonautas",
            "url": "https://endonautas.cl",
            "description": self.tagline,
            "potentialAction": {
                "@type": "SearchAction",
                "target": "https://endonautas.cl/blog/?q={search_term_string}",
                "query-input": "required name=search_term_string"
            }
        }
        return json.dumps(data, ensure_ascii=False)

    class Meta:
        verbose_name = 'Página de Inicio'


class SimplePage(Page):
    body = RichTextField(blank=True)
    cta_text = models.CharField(max_length=80, blank=True)
    cta_url = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('cta_text'),
        FieldPanel('cta_url'),
    ]

    class Meta:
        verbose_name = 'Página Simple'
