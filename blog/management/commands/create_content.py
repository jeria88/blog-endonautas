"""
Creador de contenido unificado.

Flujo completo:
1. Generar artículo de blog con DeepSeek
2. Generar copy RRSS (carrusel + reel) a partir del artículo
3. Generar carrusel HTML → PNG
4. Generar video del reel

Uso:
    python manage.py create_content --topic "Herida de abandono" --all
    python manage.py create_content --article-id 5 --rrss --carrusel --reel
    python manage.py create_content --list-topics
"""
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.models import GeneratedArticle, SocialPost
from blog.services import (
    generate_article, generate_carrusel_copy, generate_reel_copy,
    BLOG_TOPICS, get_topic_title, get_topic_keywords, get_topic_cta, get_topic_capa,
)

logger = logging.getLogger(__name__)

# Paths para generación de carruseles
BASE_DIR = Path(settings.BASE_DIR)
SOCIAL_BASE = BASE_DIR.parent / 'brand' / 'social' / 'plantilla'
CARRUSEL_TEMPLATE = SOCIAL_BASE / '05-post-completo' / 'generate_v4.py'
OUTPUT_DIR = BASE_DIR.parent / 'contenido' / 'carruseles' / 'generated'


class Command(BaseCommand):
    help = "Creador de contenido unificado: artículos + RRSS + carruseles + reels"

    def add_arguments(self, parser):
        parser.add_argument('--topic', type=str, help='Tema específico para generar')
        parser.add_argument('--article-id', type=int, help='ID de artículo existente')
        parser.add_argument('--all', action='store_true', help='Genera todo: artículo + RRSS + carrusel')
        parser.add_argument('--rrss', action='store_true', help='Genera copy RRSS')
        parser.add_argument('--carrusel', action='store_true', help='Genera carrusel HTML→PNG')
        parser.add_argument('--reel', action='store_true', help='Genera video del reel')
        parser.add_argument('--count', type=int, default=1, help='Cantidad de artículos (default: 1)')
        parser.add_argument('--list-topics', action='store_true', help='Lista temas disponibles')
        parser.add_argument('--platform', type=str, default='instagram',
                            choices=['instagram', 'tiktok', 'linkedin'])

    def handle(self, *args, **options):
        if options['list_topics']:
            self._list_topics()
            return

        # Determinar el artículo fuente
        article = None
        if options['article_id']:
            try:
                article = GeneratedArticle.objects.get(pk=options['article_id'])
            except GeneratedArticle.DoesNotExist:
                raise CommandError(f"Artículo {options['article_id']} no encontrado")
        elif options['topic'] or options['all'] or options['rrss']:
            # Generar artículo primero
            article = self._generate_article(options)

        if not article and (options['rrss'] or options['carrusel'] or options['reel']):
            raise CommandError("Necesitas un artículo. Usa --topic o --article-id")

        # Generar RRSS
        if options['rrss'] or options['all']:
            self._generate_rrss(article, options)

        # Generar carrusel
        if options['carrusel'] or options['all']:
            self._generate_carrusel(article, options)

        # Generar reel
        if options['reel'] or options['all']:
            self._generate_reel(article, options)

    def _list_topics(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Temas disponibles:"))
        for i, topic in enumerate(BLOG_TOPICS, 1):
            capa = get_topic_capa(topic)
            self.stdout.write(f"  {i:2d}. [{capa}] {get_topic_title(topic)}")

    def _generate_article(self, options):
        """Genera un artículo con DeepSeek."""
        topic = options['topic']
        if not topic:
            # Usar el primer tema disponible sin artículo generado
            existing_slugs = set(GeneratedArticle.objects.values_list('slug', flat=True))
            for t in BLOG_TOPICS:
                from django.utils.text import slugify
                if slugify(get_topic_title(t))[:200] not in existing_slugs:
                    topic = get_topic_title(t)
                    break
            if not topic:
                self.stdout.write(self.style.WARNING("Todos los temas ya tienen artículos generados."))
                return None

        self.stdout.write(f"Generando artículo: {topic}...")
        try:
            article = generate_article(
                topic,
                source_type='tema',
                source_detail=f"Capa SEO: {get_topic_capa(next((t for t in BLOG_TOPICS if get_topic_title(t) == topic), BLOG_TOPICS[0]))}"
            )
            # Actualizar keywords y CTA
            topic_tuple = next((t for t in BLOG_TOPICS if get_topic_title(t) == topic), None)
            if topic_tuple:
                article.keywords = get_topic_keywords(topic_tuple)
                article.cta_url = get_topic_cta(topic_tuple)
                article.save(update_fields=['keywords', 'cta_url'])

            self.stdout.write(self.style.SUCCESS(f"  ✓ Artículo creado: {article.title}"))
            self.stdout.write(f"    ID: {article.pk}")
            self.stdout.write(f"    Admin: /admin/blog/generatedarticle/{article.pk}/change/")
            return article
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error: {e}"))
            return None

    def _generate_rrss(self, article, options):
        """Genera copy RRSS (carrusel + reel) a partir del artículo."""
        self.stdout.write("Generando copy RRSS...")

        plataforma = options['platform']

        # Generar carrusel
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
            self.stdout.write(self.style.SUCCESS(f"  ✓ Carrusel generado ({len(slides)} slides)"))
            self.stdout.write(f"    ID: {carrusel.pk}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error carrusel: {e}"))

        # Generar reel
        try:
            copy_data = generate_reel_copy(article)
            texto_pantalla = copy_data.get('texto_pantalla', '')
            descripcion = copy_data.get('descripcion', '')
            hashtags = copy_data.get('hashtags', '')

            reel = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=SocialPost.FORMATO_REEL,
                copy_reel_texto=texto_pantalla,
                copy_reel_descripcion=f"{descripcion}\n\n{hashtags}",
                status=SocialPost.STATUS_DRAFT,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Reel generado"))
            self.stdout.write(f"    ID: {reel.pk}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error reel: {e}"))

    def _generate_carrusel(self, article, options):
        """Genera carrusel HTML → PNG usando Chrome headless."""
        self.stdout.write("Generando carrusel HTML→PNG...")

        # Obtener el copy del carrusel
        try:
            social_post = SocialPost.objects.filter(
                generated_article=article,
                formato=SocialPost.FORMATO_CARRUSEL
            ).first()
        except SocialPost.DoesNotExist:
            self.stderr.write(self.style.ERROR("  ✗ No hay copy de carrusel generado. Usa --rrss primero."))
            return

        slides = social_post.get_slides_text()
        if not slides:
            self.stderr.write(self.style.ERROR("  ✗ No hay slides en el copy."))
            return

        # Crear directorio de salida
        output_dir = OUTPUT_DIR / f"article-{article.pk}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generar HTML para cada slide
        html_files = []
        for i, slide_text in enumerate(slides):
            html = self._build_slide_html(slide_text, i + 1, len(slides), article)
            html_path = output_dir / f"slide-{i+1:02d}.html"
            html_path.write_text(html, encoding='utf-8')
            html_files.append(html_path)

        # Convertir a PNG usando Chrome headless
        png_count = 0
        for html_path in html_files:
            png_path = html_path.with_suffix('.png')
            try:
                subprocess.run([
                    'google-chrome', '--headless', '--disable-gpu',
                    f'--screenshot={png_path}',
                    '--window-size=1080,1080',
                    '--hide-scrollbars',
                    f'file://{html_path}'
                ], capture_output=True, check=True, timeout=30)

                if png_path.exists():
                    png_count += 1
                    self.stdout.write(f"  ✓ {png_path.name}")
            except subprocess.CalledProcessError as e:
                self.stderr.write(self.style.ERROR(f"  ✗ Error en {html_path.name}: {e}"))
            except FileNotFoundError:
                self.stderr.write(self.style.ERROR("  ✗ google-chrome no encontrado. Instalalo con: apt install chromium"))
                break

        # Actualizar el SocialPost
        social_post.carrusel_html_path=str(output_dir)
        social_post.carrusel_png_count=png_count
        social_post.save(update_fields=['carrusel_html_path', 'carrusel_png_count'])

        self.stdout.write(self.style.SUCCESS(f"  ✓ {png_count}/{len(slides)} slides generados"))
        self.stdout.write(f"    Directorio: {output_dir}")

    def _build_slide_html(self, text, slide_num, total_slides, article):
        """Genera HTML para una slide del carrusel."""
        # Limpiar texto
        text = text.strip()
        # Si el texto es muy largo, truncar
        if len(text) > 300:
            text = text[:297] + "..."

        return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Slide {slide_num} — {article.title}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700;900&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;position:relative;
  background:#040810;font-family:'Space Grotesk',sans-serif;color:#F0E8DC}}
.bg{{position:absolute;inset:0;z-index:1;
  background:linear-gradient(135deg,#0a0a1a 0%,#1a1a35 50%,#0a0a1a 100%)}}
.content{{position:absolute;inset:0;z-index:10;padding:80px 90px;
  display:flex;flex-direction:column;justify-content:center}}
.slide-num{{position:absolute;top:40px;right:50px;z-index:10;
  font-size:14px;letter-spacing:0.15em;color:rgba(126,207,168,0.5);
  font-family:'Plus Jakarta Sans'}}
.logo{{position:absolute;bottom:40px;left:50px;z-index:10;
  font-size:16px;font-weight:700;letter-spacing:0.04em;color:rgba(240,232,220,0.6)}}
.cta{{position:absolute;bottom:40px;right:50px;z-index:10;
  font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.6);
  text-transform:uppercase;font-family:'Plus Jakarta Sans'}}
h1{{font-size:72px;font-weight:900;line-height:0.92;letter-spacing:-0.04em;
  color:#F0E8DC;margin-bottom:30px}}
p{{font-family:'Plus Jakarta Sans';font-size:28px;line-height:1.55;
  color:rgba(240,232,220,0.65);max-width:800px}}
em{{font-style:italic;color:#7ecfa8;-webkit-text-fill-color:#7ecfa8}}
</style>
</head>
<body>
<div class="bg"></div>
<div class="slide-num">{slide_num} / {total_slides}</div>
<div class="content">
  <h1>{text}</h1>
</div>
<div class="logo">Endonautas</div>
<div class="cta">Desliza →</div>
</body>
</html>'''

    def _generate_reel(self, article, options):
        """Genera video del reel (texto sobre fondo visual)."""
        self.stdout.write("Generando video del reel...")

        # Obtener el copy del reel
        try:
            social_post = SocialPost.objects.filter(
                generated_article=article,
                formato=SocialPost.FORMATO_REEL
            ).first()
        except SocialPost.DoesNotExist:
            self.stderr.write(self.style.ERROR("  ✗ No hay copy de reel generado. Usa --rrss primero."))
            return

        texto_pantalla = social_post.copy_reel_texto
        if not texto_pantalla:
            self.stderr.write(self.style.ERROR("  ✗ No hay texto para el reel."))
            return

        # Crear directorio de salida
        output_dir = OUTPUT_DIR / f"article-{article.pk}" / "reel"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generar HTML del reel (1080x1920 para vertical)
        html = self._build_reel_html(texto_pantalla, article)
        html_path = output_dir / "reel.html"
        html_path.write_text(html, encoding='utf-8')

        # Convertir a video usando ffmpeg
        video_path = output_dir / "reel.mp4"
        try:
            # Primero generar un frame PNG
            png_path = output_dir / "reel_frame.png"
            subprocess.run([
                'google-chrome', '--headless', '--disable-gpu',
                f'--screenshot={png_path}',
                '--window-size=1080,1920',
                '--hide-scrollbars',
                f'file://{html_path}'
            ], capture_output=True, check=True, timeout=30)

            if png_path.exists():
                # Convertir a video de 15 segundos con ffmpeg
                subprocess.run([
                    'ffmpeg', '-y',
                    '-loop', '1', '-i', str(png_path),
                    '-c:v', 'libx264', '-t', '15',
                    '-pix_fmt', 'yuv420p',
                    '-vf', 'scale=1080:1920',
                    str(video_path)
                ], capture_output=True, check=True, timeout=60)

                if video_path.exists():
                    social_post.reel_video_path=str(video_path)
                    social_post.save(update_fields=['reel_video_path'])
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Reel generado: {video_path}"))
                else:
                    self.stderr.write(self.style.ERROR("  ✗ Error generando video con ffmpeg"))
            else:
                self.stderr.write(self.style.ERROR("  ✗ Error generando frame PNG"))

        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Herramienta no encontrada: {e}"))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"  ✗ Error en conversión: {e}"))

    def _build_reel_html(self, texto_pantalla, article):
        """Genera HTML para el reel (1080x1920 vertical)."""
        return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reel — {article.title}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700;900&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;
  background:#040810;font-family:'Space Grotesk',sans-serif;color:#F0E8DC}}
.bg{{position:absolute;inset:0;z-index:1;
  background:linear-gradient(180deg,#0a0a1a 0%,#1a1a35 40%,#0a0a1a 100%)}}
.content{{position:absolute;inset:0;z-index:10;
  display:flex;flex-direction:column;justify-content:center;align-items:center;
  padding:120px 80px;text-align:center}}
h1{{font-size:96px;font-weight:900;line-height:0.92;letter-spacing:-0.04em;
  color:#F0E8DC;margin-bottom:60px}}
p{{font-family:'Plus Jakarta Sans';font-size:36px;line-height:1.5;
  color:rgba(240,232,220,0.6);max-width:800px}}
em{{font-style:italic;color:#7ecfa8;-webkit-text-fill-color:#7ecfa8}}
.logo{{position:absolute;bottom:60px;left:0;right:0;text-align:center;
  font-size:18px;font-weight:700;letter-spacing:0.04em;color:rgba(240,232,220,0.4)}}
</style>
</head>
<body>
<div class="bg"></div>
<div class="content">
  <h1>{texto_pantalla}</h1>
  <p>Descubre más en endonautas.cl</p>
</div>
<div class="logo">Endonautas</div>
</body>
</html>'''
