from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
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


class FeatureBlock(blocks.StructBlock):
    icon = blocks.CharBlock(max_length=10, help_text='Símbolo Unicode, ej: ◇ ◈ ✦')
    title = blocks.CharBlock(max_length=80)
    description = blocks.TextBlock()

    class Meta:
        icon = 'list-ul'
        label = 'Característica'


class EndonauticaPage(Page):
    headline = models.CharField(max_length=200, blank=True, verbose_name='Titular')
    intro = RichTextField(blank=True, verbose_name='Introducción')
    hotmart_url = models.URLField(blank=True, verbose_name='URL de compra (Hotmart)')
    hotmart_cta = models.CharField(max_length=80, default='Conseguir el libro', verbose_name='Texto del CTA')
    features = StreamField([('feature', FeatureBlock())], blank=True, use_json_field=True, verbose_name='Características')
    excerpt = models.TextField(blank=True, verbose_name='Extracto del libro')

    content_panels = Page.content_panels + [
        FieldPanel('headline'),
        FieldPanel('intro'),
        FieldPanel('features'),
        FieldPanel('excerpt'),
        MultiFieldPanel([
            FieldPanel('hotmart_url'),
            FieldPanel('hotmart_cta'),
        ], heading='Compra'),
    ]

    class Meta:
        verbose_name = 'Página Endonautica (libro)'


class MascaraPage(Page):
    headline = models.CharField(max_length=200, blank=True, verbose_name='Titular')
    subheadline = models.CharField(max_length=300, blank=True, verbose_name='Subtitular')
    description = RichTextField(blank=True, verbose_name='Descripción del lead magnet')
    brevo_list_id = models.PositiveIntegerField(default=7, verbose_name='ID de lista Brevo')
    hotmart_url = models.URLField(blank=True, verbose_name='URL Hotmart (upsell post-suscripción)')
    thank_you_text = models.TextField(
        blank=True,
        default='¡Listo! Te enviamos el PDF a tu correo.',
        verbose_name='Mensaje de confirmación',
    )

    content_panels = Page.content_panels + [
        FieldPanel('headline'),
        FieldPanel('subheadline'),
        FieldPanel('description'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldPanel('brevo_list_id'),
            FieldPanel('hotmart_url'),
        ], heading='Integración'),
    ]

    class Meta:
        verbose_name = 'Página MÁSCARA (lead magnet)'


class EquipoPage(Page):
    intro = RichTextField(blank=True, verbose_name='Intro filosófica')
    bio = RichTextField(blank=True, verbose_name='Biografía de Franco')
    photo_url = models.URLField(
        blank=True,
        default='https://ebook.endonautas.cl/assets/img/franco-jeria.jpeg',
        verbose_name='URL foto',
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('photo_url'),
        FieldPanel('bio'),
    ]

    class Meta:
        verbose_name = 'Página Equipo'


class HacksPage(Page):
    subheadline = models.CharField(max_length=300, blank=True, verbose_name='Subtitular')
    description = RichTextField(blank=True, verbose_name='Descripción')
    brevo_list_id = models.PositiveIntegerField(default=5, verbose_name='ID de lista Brevo')
    thank_you_text = models.TextField(
        blank=True,
        default='¡Listo! Revisa tu correo. No la leas de corrido — lee un hack, desaparece un día, vuelve al siguiente.',
        verbose_name='Mensaje de confirmación',
    )

    content_panels = Page.content_panels + [
        FieldPanel('subheadline'),
        FieldPanel('description'),
        FieldPanel('thank_you_text'),
        FieldPanel('brevo_list_id'),
    ]

    class Meta:
        verbose_name = 'Página Hacks (3 Hacks de Endonáutica)'


class ViajePage(Page):
    subheadline = models.CharField(max_length=300, blank=True, verbose_name='Subtitular')
    description = RichTextField(blank=True, verbose_name='Descripción')
    brevo_list_id = models.PositiveIntegerField(default=6, verbose_name='ID de lista Brevo')
    thank_you_text = models.TextField(
        blank=True,
        default='¡Listo! Revisa tu correo. El viaje no tiene deadline — pero hoy es un buen día para arrancar.',
        verbose_name='Mensaje de confirmación',
    )

    content_panels = Page.content_panels + [
        FieldPanel('subheadline'),
        FieldPanel('description'),
        FieldPanel('thank_you_text'),
        FieldPanel('brevo_list_id'),
    ]

    class Meta:
        verbose_name = 'Página Viaje (Guía Viaje Interior)'
