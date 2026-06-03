"""
Vistas del CGM — Content Generation Management.
"""
import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from blog.models import GeneratedArticle, SocialPost
from blog.services import (
    generate_article, generate_carrusel_copy, generate_reel_copy,
    BLOG_TOPICS, get_topic_title, get_topic_keywords, get_topic_cta, get_topic_capa,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(settings.BASE_DIR)
SOCIAL_BASE = BASE_DIR.parent / 'brand' / 'social' / 'plantilla'
OUTPUT_DIR = BASE_DIR.parent / 'contenido' / 'carruseles' / 'generated'


# ════════════════════════════════════════════════════════════════════════════
# Páginas
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
def cgm_dashboard(request):
    """Dashboard principal del CGM."""
    articles = GeneratedArticle.objects.all()[:20]
    social_posts = SocialPost.objects.all()[:20]
    topics = [get_topic_title(t) for t in BLOG_TOPICS]

    context = {
        'title': 'CGM — Content Generation',
        'articles': articles,
        'social_posts': social_posts,
        'topics': topics,
        'total_articles': GeneratedArticle.objects.count(),
        'total_social': SocialPost.objects.count(),
    }
    return render(request, 'blog/cgm/dashboard.html', context)


@staff_member_required
def cgm_generate(request):
    """Página para generar nuevo contenido."""
    topics = [
        {'title': get_topic_title(t), 'capa': get_topic_capa(t), 'keywords': get_topic_keywords(t)}
        for t in BLOG_TOPICS
    ]
    articles = GeneratedArticle.objects.filter(status__in=['draft', 'review'])[:10]

    context = {
        'title': 'Generar Contenido',
        'topics': topics,
        'articles': articles,
        'styles': ['A', 'B', 'C'],
        'platforms': ['instagram', 'tiktok', 'linkedin'],
        'formats': ['carrusel', 'reel'],
    }
    return render(request, 'blog/cgm/generate.html', context)


@staff_member_required
def cgm_article_detail(request, pk):
    """Detalle de un artículo generado."""
    article = get_object_or_404(GeneratedArticle, pk=pk)
    social_posts = SocialPost.objects.filter(generated_article=article)

    context = {
        'title': article.title,
        'article': article,
        'social_posts': social_posts,
    }
    return render(request, 'blog/cgm/article_detail.html', context)


@staff_member_required
def cgm_social_detail(request, pk):
    """Detalle de un post RRSS."""
    post = get_object_or_404(SocialPost, pk=pk)

    context = {
        'title': f'Post RRSS #{post.pk}',
        'post': post,
        'slides': post.get_slides_text(),
    }
    return render(request, 'blog/cgm/social_detail.html', context)


# ════════════════════════════════════════════════════════════════════════════
# API Endpoints (AJAX)
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
@require_POST
def api_generate_article(request):
    """API: Genera un artículo con DeepSeek."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    topic = data.get('topic', '').strip()
    if not topic:
        return JsonResponse({'error': 'Falta el tema'}, status=400)

    try:
        article = generate_article(topic, source_type='tema')
        # Actualizar keywords y CTA desde los temas predefinidos
        topic_tuple = next((t for t in BLOG_TOPICS if get_topic_title(t) == topic), None)
        if topic_tuple:
            article.keywords = get_topic_keywords(topic_tuple)
            article.cta_url = get_topic_cta(topic_tuple)
            article.save(update_fields=['keywords', 'cta_url'])

        return JsonResponse({
            'ok': True,
            'article_id': article.pk,
            'title': article.title,
            'slug': article.slug,
            'status': article.status,
            'url': f'/cgm/article/{article.pk}/',
        })
    except Exception as e:
        logger.error(f"Error generando artículo: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_generate_rrss(request):
    """API: Genera copy RRSS a partir de un artículo."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    article_id = data.get('article_id')
    if not article_id:
        return JsonResponse({'error': 'Falta article_id'}, status=400)

    try:
        article = GeneratedArticle.objects.get(pk=article_id)
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)

    plataforma = data.get('plataforma', 'instagram')
    formatos = data.get('formatos', ['carrusel', 'reel'])

    created = []

    if 'carrusel' in formatos:
        try:
            copy_data = generate_carrusel_copy(article)
            slides = copy_data.get('slides', [])
            carrusel = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=SocialPost.FORMATO_CARRUSEL,
                copy_carrusel='\n---\n'.join(slides),
                copy_descripcion=f"{copy_data.get('descripcion', '')}\n\n{copy_data.get('hashtags', '')}",
                status=SocialPost.STATUS_DRAFT,
            )
            created.append({'type': 'carrusel', 'id': carrusel.pk, 'slides': len(slides)})
        except Exception as e:
            logger.error(f"Error generando carrusel: {e}")

    if 'reel' in formatos:
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
            created.append({'type': 'reel', 'id': reel.pk})
        except Exception as e:
            logger.error(f"Error generando reel: {e}")

    return JsonResponse({'ok': True, 'created': created})


@staff_member_required
@require_POST
def api_generate_carrusel(request):
    """API: Genera carrusel PNG usando la plantilla v4."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    social_id = data.get('social_id')
    style = data.get('style', 'A')

    if not social_id:
        return JsonResponse({'error': 'Falta social_id'}, status=400)

    try:
        social_post = SocialPost.objects.get(pk=social_id, formato=SocialPost.FORMATO_CARRUSEL)
    except SocialPost.DoesNotExist:
        return JsonResponse({'error': 'Post no encontrado'}, status=404)

    slides_text = social_post.get_slides_text()
    if not slides_text:
        return JsonResponse({'error': 'No hay slides'}, status=400)

    # Cargar plantilla v4
    try:
        import importlib.util
        v4_path = SOCIAL_BASE / '05-post-completo' / 'generate_v4.py'
        spec = importlib.util.spec_from_file_location("generate_v4", str(v4_path))
        v4 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v4)
    except Exception as e:
        return JsonResponse({'error': f'Error cargando plantilla: {e}'}, status=500)

    # Generar HTMLs
    output_dir = OUTPUT_DIR / f"article-{social_post.generated_article_id}" / f"style-{style}"
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = []
    for i, text in enumerate(slides_text):
        html = _build_slide(text, i + 1, len(slides_text), style, v4)
        html_path = output_dir / f"slide-{i+1:02d}.html"
        html_path.write_text(html, encoding='utf-8')
        html_files.append(html_path)

    # Renderizar PNGs
    png_count = 0
    for html_path in html_files:
        jpg_path = html_path.with_suffix('.jpg')
        try:
            v4.chrome_render(str(html_path), str(jpg_path))
            if jpg_path.exists():
                png_count += 1
        except Exception as e:
            logger.error(f"Error renderizando {html_path}: {e}")

    social_post.carrusel_html_path = str(output_dir)
    social_post.carrusel_png_count = png_count
    social_post.save(update_fields=['carrusel_html_path', 'carrusel_png_count'])

    return JsonResponse({
        'ok': True,
        'png_count': png_count,
        'total': len(slides_text),
        'output_dir': str(output_dir),
    })


@staff_member_required
@require_POST
def api_generate_reel(request):
    """API: Genera video del reel."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    social_id = data.get('social_id')
    if not social_id:
        return JsonResponse({'error': 'Falta social_id'}, status=400)

    try:
        social_post = SocialPost.objects.get(pk=social_id, formato=SocialPost.FORMATO_REEL)
    except SocialPost.DoesNotExist:
        return JsonResponse({'error': 'Post no encontrado'}, status=404)

    texto = social_post.copy_reel_texto
    if not texto:
        return JsonResponse({'error': 'No hay texto para el reel'}, status=400)

    output_dir = OUTPUT_DIR / f"article-{social_post.generated_article_id}" / "reel"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generar HTML del reel
    html = _build_reel_html(texto)
    html_path = output_dir / "reel.html"
    html_path.write_text(html, encoding='utf-8')

    try:
        import importlib.util
        v4_path = SOCIAL_BASE / '05-post-completo' / 'generate_v4.py'
        spec = importlib.util.spec_from_file_location("generate_v4", str(v4_path))
        v4 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v4)

        png_path = output_dir / "reel_frame.png"
        v4.chrome_render(str(html_path), str(png_path).replace('.png', '.jpg'))

        if png_path.exists():
            import subprocess
            video_path = output_dir / "reel.mp4"
            subprocess.run([
                'ffmpeg', '-y', '-loop', '1', '-i', str(png_path),
                '-c:v', 'libx264', '-t', '15', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920', str(video_path)
            ], capture_output=True, check=True, timeout=60)

            if video_path.exists():
                social_post.reel_video_path = str(video_path)
                social_post.save(update_fields=['reel_video_path'])
                return JsonResponse({'ok': True, 'video_path': str(video_path)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Error generando video'}, status=500)


# ════════════════════════════════════════════════════════════════════════════
# Descargas
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
def cgm_download(request, asset_type, pk):
    """Descarga archivos generados (PNG, MP4, ZIP)."""
    import zipfile
    import io

    if asset_type == 'carrusel':
        post = get_object_or_404(SocialPost, pk=pk, formato=SocialPost.FORMATO_CARRUSEL)
        if not post.carrusel_html_path:
            raise Http404("No hay carrusel generado")

        dir_path = Path(post.carrusel_html_path)
        if not dir_path.exists():
            raise Http404("Directorio no encontrado")

        # Crear ZIP con todos los PNGs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for png_file in sorted(dir_path.glob('*.jpg')):
                zf.write(png_file, png_file.name)
        zip_buffer.seek(0)

        return FileResponse(
            zip_buffer,
            as_attachment=True,
            filename=f"carrusel-{pk}.zip",
            content_type='application/zip'
        )

    elif asset_type == 'reel':
        post = get_object_or_404(SocialPost, pk=pk, formato=SocialPost.FORMATO_REEL)
        if not post.reel_video_path:
            raise Http404("No hay reel generado")

        video_path = Path(post.reel_video_path)
        if not video_path.exists():
            raise Http404("Video no encontrado")

        return FileResponse(
            open(video_path, 'rb'),
            as_attachment=True,
            filename=f"reel-{pk}.mp4",
            content_type='video/mp4'
        )

    elif asset_type == 'slide':
        # Descargar un slide específico
        post = get_object_or_404(SocialPost, pk=pk)
        if not post.carrusel_html_path:
            raise Http404("No hay carrusel generado")

        dir_path = Path(post.carrusel_html_path)
        slide_num = request.GET.get('n', '1')
        slide_file = dir_path / f"slide-{int(slide_num):02d}.jpg"

        if not slide_file.exists():
            raise Http404(f"Slide {slide_num} no encontrado")

        return FileResponse(
            open(slide_file, 'rb'),
            as_attachment=True,
            filename=f"slide-{slide_num}.jpg",
            content_type='image/jpeg'
        )

    raise Http404("Tipo de asset no válido")


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _build_slide(text, slide_num, total, style, v4):
    """Genera HTML para una slide según el estilo."""
    text = text.strip()[:300]

    if style == 'A':
        s = v4.a_base(v4.BG_STARS, "brightness(0.68)contrast(1.15)saturate(0.30)")
        if slide_num == 1:
            s += f'''<div class="ui">
  <div class="nav"><div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div><span class="nt">Blog</span></div>
  <div><div style="width:36px;height:1.5px;background:{v4.JADE};margin-bottom:22px;"></div>
  <h1 style="font-weight:900;font-size:95px;line-height:0.88;letter-spacing:-0.04em;color:{v4.CREAM};margin-bottom:32px;">{text}</h1></div>
  <div class="foot"><span class="fl">Desliza →</span><span class="fn">{slide_num}/{total}</span></div>
</div></body></html>'''
        elif slide_num == total:
            s += f'''<div class="ui">
  <div class="nav"><div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div><span class="nt">CTA</span></div>
  <div><h2 style="font-weight:900;font-size:86px;line-height:0.88;letter-spacing:-0.04em;color:{v4.CREAM};margin-bottom:28px;">{text}</h2>
  <div style="padding:18px 44px;border-radius:60px;background:{v4.JADE};color:#030c07;font-weight:700;font-size:14px;letter-spacing:0.12em;text-transform:uppercase;box-shadow:0 0 70px rgba(126,207,168,0.42);">LEER ARTÍCULO →</div></div>
  <div class="foot"><span style="font-size:12px;letter-spacing:0.10em;color:rgba(240,232,220,0.22);">endonautas.cl</span><span class="fn">{slide_num}/{total}</span></div>
</div></body></html>'''
        else:
            s += f'''<div class="ui">
  <div class="nav"><div class="lw"><img class="li" src="{v4.LOGO}"><span class="lt">Endonautas</span></div><span class="nt">Idea {slide_num-1}</span></div>
  <div><div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;"><div style="width:32px;height:1.5px;background:{v4.JADE};"></div><span style="font-size:13px;letter-spacing:0.28em;text-transform:uppercase;color:rgba(240,232,220,0.38);">IDEA {slide_num-1}</span></div>
  <h2 style="font-weight:900;font-size:72px;line-height:0.90;letter-spacing:-0.036em;color:{v4.CREAM};margin-bottom:24px;">{text}</h2></div>
  <div class="foot"><span class="fl">Continúa →</span><span class="fn">{slide_num}/{total}</span></div>
</div></body></html>'''
        return s

    elif style == 'B':
        s = v4.b_base(v4.BG_NEBULA, "brightness(0.65)contrast(1.18)saturate(0.55)hue-rotate(15deg)")
        s += f'''<div style="position:absolute;left:0;top:0;bottom:0;width:4px;z-index:10;background:linear-gradient(to bottom,transparent 8%,{v4.JADE} 25%,{v4.JADE} 75%,transparent 92%);opacity:0.65;"></div>
<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;"><img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}"><span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.75);">Endonautas</span></div>
  <div style="border:1px solid rgba(126,207,168,0.30);border-radius:2px;padding:8px 16px;font-size:12px;letter-spacing:0.24em;text-transform:uppercase;color:rgba(126,207,168,0.65);">Blog</div>
</div>
<div style="position:absolute;left:64px;right:64px;bottom:52px;z-index:10;">
  <h1 style="font-weight:900;font-size:104px;line-height:0.87;letter-spacing:-0.042em;color:{v4.CREAM};margin-bottom:30px;">{text}</h1>
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <span style="font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.60);text-transform:uppercase;">{"Desliza →" if slide_num == 1 else "Continúa →"}</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num}/{total}</span>
  </div>
</div></body></html>'''
        return s

    else:  # C
        s = v4.c_base()
        s += f'''<div style="position:absolute;top:52px;left:64px;right:64px;z-index:10;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:10px;"><img style="width:30px;height:30px;border-radius:50%;" src="{v4.LOGO}"><span style="font-weight:700;font-size:16px;letter-spacing:0.04em;color:rgba(240,232,220,0.72);">Endonautas</span></div>
  <span style="font-size:12px;letter-spacing:0.24em;color:rgba(240,232,220,0.28);text-transform:uppercase;">Blog</span>
</div>
<div style="position:absolute;left:64px;right:0;bottom:52px;z-index:10;">
  <h1 style="font-weight:900;font-size:128px;line-height:0.85;letter-spacing:-0.05em;color:{v4.CREAM};margin-bottom:0;">{text}</h1>
  <div style="width:calc(100% - 64px);height:1px;background:linear-gradient(to right,rgba(126,207,168,0.50),transparent);margin-bottom:22px;margin-right:64px;"></div>
  <div style="display:flex;padding-right:64px;justify-content:space-between;align-items:center;">
    <span style="font-size:12px;letter-spacing:0.18em;color:rgba(126,207,168,0.65);text-transform:uppercase;">{"Desliza →" if slide_num == 1 else "Continúa →"}</span>
    <span style="font-size:12px;letter-spacing:0.14em;color:rgba(240,232,220,0.25);">{slide_num}/{total}</span>
  </div>
</div></body></html>'''
        return s


def _build_reel_html(texto):
    """Genera HTML para el reel (1080x1920)."""
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
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
<div class="content"><h1>{texto}</h1><p>Descubre más en endonautas.cl</p></div>
<div class="logo">Endonautas</div>
</body></html>'''
