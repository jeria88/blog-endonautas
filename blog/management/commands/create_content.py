"""
Creador de contenido unificado — Fase 2: RRSS profesional.

Usa la plantilla generate_v4.py (estilos A/B/C) con fondos de Pexels
para generar carruseles PNG profesionales.

Flujo:
1. Generar artículo de blog con DeepSeek
2. Generar copy RRSS (carrusel + reel) a partir del artículo
3. Generar carrusel PNG usando plantilla v4 (estilo A, B o C)
4. Generar video del reel

Uso:
    python manage.py create_content --topic "Herida de abandono" --all --style A
    python manage.py create_content --article-id 5 --carrusel --style B
    python manage.py create_content --list-styles
"""
import importlib.util
import logging
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.models import GeneratedArticle, SocialPost
from blog.services import (
    generate_article, generate_carrusel_copy, generate_reel_copy,
    BLOG_TOPICS, get_topic_title, get_topic_keywords, get_topic_cta, get_topic_capa,
)

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(settings.BASE_DIR)
SOCIAL_BASE = BASE_DIR.parent / 'brand' / 'social' / 'plantilla'
GENERATE_V4 = SOCIAL_BASE / '05-post-completo' / 'generate_v4.py'
OUTPUT_DIR = BASE_DIR.parent / 'contenido' / 'carruseles' / 'generated'

# Cargar generate_v4.py como módulo
def _load_generate_v4():
    """Carga el módulo generate_v4.py dinámicamente."""
    if not GENERATE_V4.exists():
        raise FileNotFoundError(f"No se encontró {GENERATE_V4}")
    spec = importlib.util.spec_from_file_location("generate_v4", str(GENERATE_V4))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Command(BaseCommand):
    help = "Creador de contenido unificado con plantilla profesional v4"

    def add_arguments(self, parser):
        parser.add_argument('--topic', type=str, help='Tema específico')
        parser.add_argument('--article-id', type=int, help='ID de artículo existente')
        parser.add_argument('--all', action='store_true', help='Genera todo el pipeline')
        parser.add_argument('--rrss', action='store_true', help='Genera copy RRSS')
        parser.add_argument('--carrusel', action='store_true', help='Genera carrusel PNG')
        parser.add_argument('--reel', action='store_true', help='Genera video del reel')
        parser.add_argument('--count', type=int, default=1, help='Cantidad de artículos')
        parser.add_argument('--style', type=str, default='A', choices=['A', 'B', 'C'],
                            help='Estilo del carrusel (A=Editorial Dark, B=Canva Premium, C=Bold)')
        parser.add_argument('--platform', type=str, default='instagram',
                            choices=['instagram', 'tiktok', 'linkedin'])
        parser.add_argument('--list-topics', action='store_true', help='Lista temas disponibles')
        parser.add_argument('--list-styles', action='store_true', help='Lista estilos disponibles')

    def handle(self, *args, **options):
        if options['list_topics']:
            self._list_topics()
            return
        if options['list_styles']:
            self._list_styles()
            return

        # Determinar el artículo fuente
        article = None
        if options['article_id']:
            try:
                article = GeneratedArticle.objects.get(pk=options['article_id'])
            except GeneratedArticle.DoesNotExist:
                raise CommandError(f"Artículo {options['article_id']} no encontrado")
        elif options['topic'] or options['all'] or options['rrss']:
            article = self._generate_article(options)

        if not article and (options['rrss'] or options['carrusel'] or options['reel']):
            raise CommandError("Necesitas un artículo. Usa --topic o --article-id")

        # Generar RRSS
        if options['rrss'] or options['all']:
            self._generate_rrss(article, options)

        # Generar carrusel con plantilla v4
        if options['carrusel'] or options['all']:
            self._generate_carrusel_v4(article, options)

        # Generar reel
        if options['reel'] or options['all']:
            self._generate_reel(article, options)

    def _list_topics(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Temas disponibles:"))
        for i, topic in enumerate(BLOG_TOPICS, 1):
            capa = get_topic_capa(topic)
            self.stdout.write(f"  {i:2d}. [{capa}] {get_topic_title(topic)}")

    def _list_styles(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Estilos de carrusel:"))
        self.stdout.write("  A — Editorial Dark (estrellas visibles, glassmorphism)")
        self.stdout.write("  B — Canva Premium (nebula, sidebar jade, numeración)")
        self.stdout.write("  C — Bold Statement (tipografía brutal, máximo impacto)")

    def _generate_article(self, options):
        """Genera un artículo con DeepSeek."""
        topic = options['topic']
        if not topic:
            existing_slugs = set(GeneratedArticle.objects.values_list('slug', flat=True))
            for t in BLOG_TOPICS:
                from django.utils.text import slugify
                if slugify(get_topic_title(t))[:200] not in existing_slugs:
                    topic = get_topic_title(t)
                    break
            if not topic:
                self.stdout.write(self.style.WARNING("Todos los temas ya tienen artículos."))
                return None

        self.stdout.write(f"Generando artículo: {topic}...")
        try:
            article = generate_article(topic, source_type='tema')
            topic_tuple = next((t for t in BLOG_TOPICS if get_topic_title(t) == topic), None)
            if topic_tuple:
                article.keywords = get_topic_keywords(topic_tuple)
                article.cta_url = get_topic_cta(topic_tuple)
                article.save(update_fields=['keywords', 'cta_url'])
            self.stdout.write(self.style.SUCCESS(f"  ✓ {article.title} (ID: {article.pk})"))
            return article
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error: {e}"))
            return None

    def _generate_rrss(self, article, options):
        """Genera copy RRSS con DeepSeek."""
        self.stdout.write("Generando copy RRSS...")
        plataforma = options['platform']

        # Carrusel
        try:
            copy_data = generate_carrusel_copy(article)
            slides = copy_data.get('slides', [])
            descripcion = copy_data.get('descripcion', '')
            hashtags = copy_data.get('hashtags', '')

            carrusel = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=SocialPost.FORMATO_CARRUSEL,
                copy_carrusel='\n---\n'.join(slides),
                copy_descripcion=f"{descripcion}\n\n{hashtags}",
                status=SocialPost.STATUS_DRAFT,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Carrusel ({len(slides)} slides)"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error carrusel: {e}"))

        # Reel
        try:
            copy_data = generate_reel_copy(article)
            reel = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=SocialPost.FORMATO_REEL,
                copy_reel_texto=copy_data.get('texto_pantalla', ''),
                copy_reel_descripcion=f"{copy_data.get('descripcion', '')}\n\n{copy_data.get('hashtags', '')}",
                status=SocialPost.STATUS_DRAFT,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Reel"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error reel: {e}"))

    def _generate_carrusel_v4(self, article, options):
        """Genera carrusel PNG usando la plantilla v4 profesional."""
        self.stdout.write(f"Generando carrusel con estilo {options['style']}...")

        # Cargar módulo v4
        try:
            v4 = _load_generate_v4()
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"  ✗ {e}"))
            return

        # Obtener copy del carrusel
        social_post = SocialPost.objects.filter(
            generated_article=article,
            formato=SocialPost.FORMATO_CARRUSEL
        ).first()

        if not social_post:
            self.stderr.write(self.style.ERROR("  ✗ No hay copy de carrusel. Usa --rrss primero."))
            return

        slides_text = social_post.get_slides_text()
        if not slides_text:
            self.stderr.write(self.style.ERROR("  ✗ No hay slides en el copy."))
            return

        # Crear directorio de salida
        output_dir = OUTPUT_DIR / f"article-{article.pk}" / f"style-{options['style']}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Mapear textos a slides según el estilo
        style = options['style']
        html_files = []

        for i, text in enumerate(slides_text):
            # Generar HTML según el estilo
            if style == 'A':
                html = self._build_style_a(text, i + 1, len(slides_text), article, v4)
            elif style == 'B':
                html = self._build_style_b(text, i + 1, len(slides_text), article, v4)
            else:  # C
                html = self._build_style_c(text, i + 1, len(slides_text), article, v4)

            html_path = output_dir / f"slide-{i+1:02d}.html"
            html_path.write_text(html, encoding='utf-8')
            html_files.append(html_path)

        # Renderizar PNGs usando Chrome headless (como generate_v4.py)
        png_count = 0
        for html_path in html_files:
            jpg_path = html_path.with_suffix('.jpg')
            try:
                v4.chrome_render(str(html_path), str(jpg_path))
                if jpg_path.exists():
                    png_count += 1
                    self.stdout.write(f"  ✓ {jpg_path.name}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  ✗ Error en {html_path.name}: {e}"))

        # Actualizar SocialPost
        social_post.carrusel_html_path = str(output_dir)
        social_post.carrusel_png_count = png_count
        social_post.save(update_fields=['carrusel_html_path', 'carrusel_png_count'])

        self.stdout.write(self.style.SUCCESS(f"  ✓ {png_count}/{len(slides_text)} slides generados"))
        self.stdout.write(f"    Directorio: {output_dir}")

    def _build_style_a(self, text, slide_num, total, article, v4):
        """Genera slide con estilo A (Editorial Dark)."""
        # Usar las funciones base de v4 pero con texto personalizado
        s = v4.a_base(v4.BG_STARS, "brightness(0.68)contrast(1.15)saturate(0.30)")

        if slide_num == 1:
            # Portada
            s += f"""<div class="ui">
  <div class="nav">
    <div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div>
    <span class="nt">Blog · Artículo</span>
  </div>
  <div>
    <div style="width:36px;height:1.5px;background:{v4.JADE};margin-bottom:22px;"></div>
    <h1 style="font-weight:900;font-size:95px;line-height:0.88;letter-spacing:-0.04em;color:{v4.CREAM};margin-bottom:32px;">
      {text}
    </h1>
  </div>
  <div class="foot">
    <span class="fl">Desliza para ver →</span>
    <span class="fn">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        elif slide_num == total:
            # Cierre con CTA
            s += f"""<div class="ui">
  <div class="nav">
    <div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div>
    <span class="nt">Mapa Interior</span>
  </div>
  <div>
    <div style="width:36px;height:1.5px;background:{v4.JADE};margin-bottom:22px;"></div>
    <h2 style="font-weight:900;font-size:86px;line-height:0.88;letter-spacing:-0.04em;color:{v4.CREAM};margin-bottom:28px;">
      {text}
    </h2>
    <div style="width:fit-content;padding:18px 44px;border-radius:60px;background:{v4.JADE};color:#030c07;font-weight:700;font-size:14px;letter-spacing:0.12em;text-transform:uppercase;box-shadow:0 0 70px rgba(126,207,168,0.42);">
      LEER ARTÍCULO COMPLETO →
    </div>
  </div>
  <div class="foot">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.10em;color:rgba(240,232,220,0.22);">endonautas.cl</span>
    <span class="fn">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        else:
            # Slide de contenido
            s += f"""<div class="ui">
  <div class="nav">
    <div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div>
    <span class="nt">Idea {slide_num - 1}</span>
  </div>
  <div>
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;">
      <div style="width:32px;height:1.5px;background:{v4.JADE};"></div>
      <span style="font-family:'Plus Jakarta Sans';font-size:13px;letter-spacing:0.28em;text-transform:uppercase;color:rgba(240,232,220,0.38);">IDEA {slide_num - 1}</span>
    </div>
    <h2 style="font-weight:900;font-size:72px;line-height:0.90;letter-spacing:-0.036em;color:{v4.CREAM};margin-bottom:24px;">
      {text}
    </h2>
  </div>
  <div class="foot">
    <span class="fl">Continúa →</span>
    <span class="fn">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        return s

    def _build_style_b(self, text, slide_num, total, article, v4):
        """Genera slide con estilo B (Canva Premium)."""
        s = v4.b_base(v4.BG_NEBULA, "brightness(0.65)contrast(1.18)saturate(0.55)hue-rotate(15deg)")

        if slide_num == 1:
            s += f"""<div style="position:absolute;left:0;top:0;bottom:0;width:4px;z-index:10;background:linear-gradient(to bottom,transparent 8%,{v4.JADE} 25%,{v4.JADE} 75%,transparent 92%);opacity:0.65;"></div>
<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.75);">Endonautas</span>
  </div>
  <div style="border:1px solid rgba(126,207,168,0.30);border-radius:2px;padding:8px 16px;font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;text-transform:uppercase;color:rgba(126,207,168,0.65);">Blog · Artículo</div>
</div>
<div style="position:absolute;left:64px;right:64px;bottom:52px;z-index:10;">
  <div style="display:inline-block;background:rgba(126,207,168,0.10);border-left:3px solid {v4.JADE};padding:9px 18px;margin-bottom:24px;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.28em;text-transform:uppercase;color:{v4.JADE};">Post 01</span>
  </div>
  <h1 style="font-weight:900;font-size:104px;line-height:0.87;letter-spacing:-0.042em;color:{v4.CREAM};margin-bottom:30px;">{text}</h1>
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.60);text-transform:uppercase;">Desliza para ver →</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        elif slide_num == total:
            s += f"""<div style="position:absolute;left:0;top:0;bottom:0;width:4px;z-index:10;background:linear-gradient(to bottom,transparent 8%,{v4.JADE} 25%,{v4.JADE} 75%,transparent 92%);opacity:0.65;"></div>
<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.70);">Endonautas</span>
  </div>
  <div style="border:1px solid rgba(126,207,168,0.30);border-radius:2px;padding:8px 16px;font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;text-transform:uppercase;color:rgba(126,207,168,0.60);">PRÓXIMO PASO</div>
</div>
<div style="position:absolute;left:64px;right:64px;bottom:52px;z-index:10;">
  <div style="display:inline-block;background:rgba(126,207,168,0.10);border-left:3px solid {v4.JADE};padding:9px 18px;margin-bottom:22px;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.28em;text-transform:uppercase;color:{v4.JADE};">Mapa Interior</span>
  </div>
  <h2 style="font-weight:900;font-size:96px;line-height:0.87;letter-spacing:-0.042em;color:{v4.CREAM};margin-bottom:26px;">{text}</h2>
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div style="padding:18px 44px;border-radius:60px;background:{v4.JADE};color:#030c07;font-weight:700;font-size:14px;letter-spacing:0.12em;text-transform:uppercase;box-shadow:0 0 80px rgba(126,207,168,0.45);">LEER ARTÍCULO →</div>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.22);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        else:
            s += f"""<div style="position:absolute;left:0;top:0;bottom:0;width:4px;z-index:10;background:linear-gradient(to bottom,transparent 8%,{v4.JADE} 25%,{v4.JADE} 75%,transparent 92%);opacity:0.65;"></div>
<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.65);">Endonautas</span>
  </div>
  <div style="border:1px solid rgba(126,207,168,0.22);border-radius:2px;padding:8px 16px;font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;text-transform:uppercase;color:rgba(126,207,168,0.45);">IDEA {slide_num - 1}</div>
</div>
<div style="position:absolute;left:64px;right:64px;bottom:52px;z-index:10;">
  <div style="display:flex;align-items:center;gap:16px;margin-bottom:22px;">
    <span style="font-size:56px;font-weight:900;color:{v4.JADE};line-height:1;opacity:0.75;">{slide_num - 1:02d}</span>
    <div style="width:1px;height:52px;background:rgba(126,207,168,0.25);"></div>
    <span style="font-family:'Plus Jakarta Sans';font-size:13px;letter-spacing:0.26em;text-transform:uppercase;color:rgba(240,232,220,0.35);">CONTENIDO</span>
  </div>
  <h2 style="font-weight:900;font-size:80px;line-height:0.88;letter-spacing:-0.036em;color:{v4.CREAM};margin-bottom:22px;">{text}</h2>
  <div style="display:flex;justify-content:space-between;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.60);text-transform:uppercase;">Continúa →</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        return s

    def _build_style_c(self, text, slide_num, total, article, v4):
        """Genera slide con estilo C (Bold Statement)."""
        s = v4.c_base()

        if slide_num == 1:
            s += f"""<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.72);">Endonautas</span>
  </div>
  <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;color:rgba(240,232,220,0.28);text-transform:uppercase;">Blog · Artículo</span>
</div>
<div style="position:absolute;left:64px;right:0;bottom:52px;z-index:10;">
  <h1 style="font-weight:900;font-size:128px;line-height:0.85;letter-spacing:-0.05em;color:{v4.CREAM};margin-bottom:0;">{text}</h1>
  <div style="width:calc(100% - 0px);height:1px;background:linear-gradient(to right,rgba(126,207,168,0.50),transparent);margin-bottom:22px;margin-right:64px;"></div>
  <div style="display:flex;padding-right:64px;justify-content:space-between;align-items:center;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.65);text-transform:uppercase;">Desliza →</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        elif slide_num == total:
            s += f"""<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.72);">Endonautas</span>
  </div>
  <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;color:rgba(240,232,220,0.28);text-transform:uppercase;">PRÓXIMO PASO</span>
</div>
<div style="position:absolute;left:64px;right:0;bottom:52px;z-index:10;">
  <h1 style="font-weight:900;font-size:120px;line-height:0.85;letter-spacing:-0.05em;color:{v4.CREAM};margin-bottom:30px;">{text}</h1>
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="padding:18px 44px;border-radius:60px;background:{v4.JADE};color:#030c07;font-weight:700;font-size:14px;letter-spacing:0.12em;text-transform:uppercase;box-shadow:0 0 80px rgba(126,207,168,0.45);">LEER ARTÍCULO →</div>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        else:
            s += f"""<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;">
    <img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}">
    <span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.72);">Endonautas</span>
  </div>
  <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.24em;color:rgba(240,232,220,0.28);text-transform:uppercase;">IDEA {slide_num - 1}</span>
</div>
<div style="position:absolute;left:64px;right:0;bottom:52px;z-index:10;">
  <h1 style="font-weight:900;font-size:110px;line-height:0.86;letter-spacing:-0.045em;color:{v4.CREAM};margin-bottom:20px;">{text}</h1>
  <div style="width:calc(100% - 64px);height:1px;background:linear-gradient(to right,rgba(126,207,168,0.50),transparent);margin-bottom:22px;"></div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding-right:64px;">
    <span style="font-family:'Plus Jakarta Sans';font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.65);text-transform:uppercase;">Continúa →</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num} / {total}</span>
  </div>
</div></body></html>"""
        return s

    def _generate_reel(self, article, options):
        """Genera video del reel."""
        self.stdout.write("Generando video del reel...")

        social_post = SocialPost.objects.filter(
            generated_article=article,
            formato=SocialPost.FORMATO_REEL
        ).first()

        if not social_post:
            self.stderr.write(self.style.ERROR("  ✗ No hay copy de reel. Usa --rrss primero."))
            return

        texto = social_post.copy_reel_texto
        if not texto:
            self.stderr.write(self.style.ERROR("  ✗ No hay texto para el reel."))
            return

        output_dir = OUTPUT_DIR / f"article-{article.pk}" / "reel"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Cargar v4 para usar sus funciones
        try:
            v4 = _load_generate_v4()
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("  ✗ No se encontró generate_v4.py"))
            return

        # Generar HTML del reel (1080x1920)
        html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700;900&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;background:#040810;font-family:'Space Grotesk',sans-serif;color:#F0E8DC}}
.bg{{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,#0a0a1a 0%,#1a1a35 40%,#0a0a1a 100%)}}
.content{{position:absolute;inset:0;z-index:10;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:120px 80px;text-align:center}}
h1{{font-size:96px;font-weight:900;line-height:0.92;letter-spacing:-0.04em;color:#F0E8DC;margin-bottom:60px}}
p{{font-family:'Plus Jakarta Sans';font-size:36px;line-height:1.5;color:rgba(240,232,220,0.6);max-width:800px}}
em{{font-style:italic;color:#7ecfa8;-webkit-text-fill-color:#7ecfa8}}
.logo{{position:absolute;bottom:60px;left:0;right:0;text-align:center;font-size:18px;font-weight:700;letter-spacing:0.04em;color:rgba(240,232,220,0.4)}}
</style></head><body>
<div class="bg"></div>
<div class="content">
  <h1>{texto}</h1>
  <p>Descubre más en endonautas.cl</p>
</div>
<div class="logo">Endonautas</div>
</body></html>'''

        html_path = output_dir / "reel.html"
        html_path.write_text(html, encoding='utf-8')

        # Renderizar con Chrome → PNG → ffmpeg → MP4
        try:
            png_path = output_dir / "reel_frame.png"
            subprocess.run([
                'google-chrome', '--headless', '--disable-gpu',
                f'--screenshot={png_path}', '--window-size=1080,1920',
                '--hide-scrollbars', f'file://{html_path}'
            ], capture_output=True, check=True, timeout=30)

            if png_path.exists():
                video_path = output_dir / "reel.mp4"
                subprocess.run([
                    'ffmpeg', '-y', '-loop', '1', '-i', str(png_path),
                    '-c:v', 'libx264', '-t', '15', '-pix_fmt', 'yuv420p',
                    '-vf', 'scale=1080:1920', str(video_path)
                ], capture_output=True, check=True, timeout=60)

                if video_path.exists():
                    social_post.reel_video_path = str(video_path)
                    social_post.save(update_fields=['reel_video_path'])
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Reel: {video_path}"))
                else:
                    self.stderr.write(self.style.ERROR("  ✗ Error generando video"))
            else:
                self.stderr.write(self.style.ERROR("  ✗ Error generando frame PNG"))
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Herramienta no encontrada: {e}"))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error: {e}"))
