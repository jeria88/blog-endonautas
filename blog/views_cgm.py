"""
Vistas del CGM — Content Generation Management.
"""
import json
import logging
import sys
import zipfile
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from blog.models import GeneratedArticle, SocialPost
from blog.services import (
    generate_article, generate_carrusel_copy, generate_reel_copy,
    BLOG_TOPICS, get_topic_title,
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# Páginas
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
def cgm_dashboard(request):
    recent_articles = GeneratedArticle.objects.all()[:6]
    suggested_topics = [
        {'title': get_topic_title(t), 'capa': t[1], 'keywords': t[2]}
        for t in BLOG_TOPICS[:8]
    ]
    context = {
        'tab': 'dashboard',
        'recent_articles': recent_articles,
        'total_articles': GeneratedArticle.objects.count(),
        'total_social': SocialPost.objects.count(),
        'total_published': GeneratedArticle.objects.filter(status=GeneratedArticle.STATUS_PUBLISHED).count(),
        'topics_count': len(BLOG_TOPICS),
        'suggested_topics': suggested_topics,
    }
    return render(request, 'blog/cgm/dashboard.html', context)


@staff_member_required
def cgm_articles(request):
    articles = GeneratedArticle.objects.all()
    suggested_topics = [
        {'title': get_topic_title(t), 'capa': t[1], 'keywords': t[2]}
        for t in BLOG_TOPICS[:12]
    ]
    context = {
        'tab': 'articles',
        'articles': articles,
        'suggested_topics': suggested_topics,
    }
    return render(request, 'blog/cgm/articles.html', context)


@staff_member_required
def cgm_article_edit(request, pk):
    article = get_object_or_404(GeneratedArticle, pk=pk)
    return render(request, 'blog/cgm/article_edit.html', {
        'tab': 'articles',
        'article': article,
    })


@staff_member_required
def cgm_rrss(request):
    articles = GeneratedArticle.objects.filter(status__in=['draft', 'review', 'approved'])
    social_posts = SocialPost.objects.all()[:20]
    selected_article = None
    article_id = request.GET.get('article')
    if article_id:
        try:
            selected_article = GeneratedArticle.objects.get(pk=article_id)
        except GeneratedArticle.DoesNotExist:
            pass
    context = {
        'tab': 'rrss',
        'articles': articles,
        'social_posts': social_posts,
        'selected_article': selected_article,
    }
    return render(request, 'blog/cgm/rrss.html', context)


# ════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
@require_POST
def api_generate_article(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    topic = data.get('topic', '').strip()
    if not topic:
        return JsonResponse({'error': 'Falta el tema'}, status=400)
    try:
        article = generate_article(topic, source_type='tema')
        return JsonResponse({'ok': True, 'article_id': article.pk, 'title': article.title})
    except Exception as e:
        logger.error(f"Error generando artículo: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_save_article(request, pk):
    try:
        article = GeneratedArticle.objects.get(pk=pk)
        data = json.loads(request.body)
        article.title = data.get('title', article.title)
        article.slug = data.get('slug', article.slug)
        article.intro = data.get('intro', article.intro)
        article.body = data.get('body', article.body)
        article.cta_text = data.get('cta_text', article.cta_text)
        article.cta_url = data.get('cta_url', article.cta_url)
        article.keywords = data.get('keywords', article.keywords)
        article.tags = data.get('tags', article.tags)
        article.meta_description = data.get('meta_description', article.meta_description)
        article.featured_image_url = data.get('featured_image_url', article.featured_image_url)
        article.slides_data = data.get('slides_data', article.slides_data)
        article.status = data.get('status', article.status)
        article.save()
        return JsonResponse({'ok': True})
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
@require_POST
def api_delete_article(request, pk):
    try:
        GeneratedArticle.objects.get(pk=pk).delete()
        return JsonResponse({'ok': True})
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
@require_POST
def api_publish_article(request, pk):
    try:
        article = GeneratedArticle.objects.get(pk=pk)
        ok, msg = article.publish_to_blog()
        if ok:
            return JsonResponse({'ok': True, 'msg': msg})
        return JsonResponse({'error': msg}, status=400)
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
def api_search_pexels(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Falta query'}, status=400)
    from blog.services import search_pexels_images
    images = search_pexels_images(query, count=12)
    return JsonResponse({'ok': True, 'images': images})


@staff_member_required
def api_article_info(request, pk):
    try:
        article = GeneratedArticle.objects.get(pk=pk)
        return JsonResponse({'ok': True, 'title': article.title, 'intro': article.intro or ''})
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
@require_POST
def api_generate_rrss(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    article_id = data.get('article_id')
    if not article_id:
        return JsonResponse({'error': 'Falta article_id'}, status=400)
    plataforma = data.get('plataforma', 'instagram')
    formato = data.get('formato', 'carrusel')
    try:
        article = GeneratedArticle.objects.get(pk=article_id)
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

    try:
        if formato == 'carrusel':
            copy_data = generate_carrusel_copy(article)
            gancho = copy_data.get('gancho', '')
            cuerpo_slides = copy_data.get('cuerpo', [])
            if isinstance(cuerpo_slides, str):
                cuerpo_slides = [s.strip() for s in cuerpo_slides.split('---') if s.strip()]
            cta = copy_data.get('cta', '')
            descripcion = copy_data.get('descripcion', '')
            hashtags = copy_data.get('hashtags', '')
            full_desc = descripcion + '\n\n' + hashtags if hashtags else descripcion
            post = SocialPost.objects.create(
                generated_article=article, plataforma=plataforma, formato=formato,
                carrusel_gancho=gancho,
                carrusel_cuerpo='\n---\n'.join(cuerpo_slides),
                carrusel_cta=cta,
                carrusel_hashtags=hashtags,
                carrusel_descripcion=descripcion,
                copy_instagram=full_desc, copy_tiktok=full_desc, copy_linkedin=full_desc,
            )
        elif formato == 'reel':
            copy_data = generate_reel_copy(article)
            texto_pantalla = copy_data.get('texto_pantalla', '')
            descripcion = copy_data.get('descripcion', '')
            hashtags = copy_data.get('hashtags', '')
            full_desc = descripcion + '\n\n' + hashtags if hashtags else descripcion
            post = SocialPost.objects.create(
                generated_article=article, plataforma=plataforma, formato=formato,
                reel_gancho=texto_pantalla, reel_cuerpo=descripcion,
                reel_cta='Descubrí más en endonautas.cl',
                reel_hashtags=hashtags, reel_descripcion=descripcion,
                copy_instagram=full_desc, copy_tiktok=full_desc, copy_linkedin=full_desc,
            )
        else:
            copy_data = generate_carrusel_copy(article)
            gancho = copy_data.get('gancho', '')
            cuerpo_slides = copy_data.get('cuerpo', [])
            if isinstance(cuerpo_slides, str):
                cuerpo_slides = [s.strip() for s in cuerpo_slides.split('---') if s.strip()]
            cta = copy_data.get('cta', '')
            hashtags = copy_data.get('hashtags', '')
            partes = [p for p in [gancho] + cuerpo_slides + [cta] if p]
            full_desc = '\n\n'.join(partes)
            if hashtags:
                full_desc += '\n\n' + hashtags
            post = SocialPost.objects.create(
                generated_article=article, plataforma=plataforma, formato=formato,
                post_gancho=gancho, post_cuerpo='\n\n'.join(cuerpo_slides), post_cta=cta,
                post_hashtags=hashtags,
                copy_instagram=full_desc, copy_tiktok=full_desc, copy_linkedin=full_desc,
            )
        return JsonResponse({'ok': True, 'post_id': post.pk, 'formato': formato})
    except Exception as e:
        logger.error(f"Error generando RRSS: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_delete_social_post(request, pk):
    try:
        SocialPost.objects.get(pk=pk).delete()
        return JsonResponse({'ok': True})
    except SocialPost.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
@require_POST
def api_save_social_post(request, pk):
    try:
        post = SocialPost.objects.get(pk=pk)
        data = json.loads(request.body)
        formato = post.formato
        if formato == 'carrusel':
            post.carrusel_gancho = data.get('gancho', post.carrusel_gancho)
            post.carrusel_cuerpo = data.get('cuerpo', post.carrusel_cuerpo)
            post.carrusel_cta = data.get('cta', post.carrusel_cta)
            post.carrusel_descripcion = data.get('descripcion', post.carrusel_descripcion)
        elif formato == 'reel':
            post.reel_gancho = data.get('gancho', post.reel_gancho)
            post.reel_descripcion = data.get('descripcion', post.reel_descripcion)
        else:
            post.post_gancho = data.get('gancho', post.post_gancho)
            post.post_cuerpo = data.get('cuerpo', post.post_cuerpo)
            post.post_cta = data.get('cta', post.post_cta)
        post.save()
        return JsonResponse({'ok': True})
    except SocialPost.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)


@staff_member_required
@require_POST
def api_generate_slides(request):
    """API: Genera PNGs de slides para un artículo."""
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
        return JsonResponse({'error': 'No encontrado'}, status=404)

    slides = data.get('slides', [])
    template_style = data.get('template_style', 'A')
    bg_image_url = data.get('bg_image_url', '')
    if not slides:
        return JsonResponse({'error': 'No hay slides'}, status=400)

    try:
        brand_template = Path(settings.BASE_DIR).parent / 'brand' / 'social' / 'plantilla' / '05-post-completo'
        sys.path.insert(0, str(brand_template))
        from layouts import render_slide_html, LAYOUTS
        output_dir = Path(settings.MEDIA_ROOT) / 'slides' / str(article_id)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = []
        for i, slide_data in enumerate(slides):
            layout_id = slide_data.get('layout', 'portada')
            slide_text = slide_data.get('text', '')
            slide_bg = slide_data.get('bg_url', bg_image_url)

            # Renderizar HTML de la slide
            html_content = render_slide_html(
                layout_id=layout_id,
                data={"title": slide_text, "body": slide_text, "quote": slide_text, **slide_data},
                slide_num=i+1,
                total=len(slides),
                bg_url=slide_bg
            )

            # Guardar HTML
            html_path = output_dir / f"slide-{i+1:02d}.html"
            html_path.write_text(html_content, encoding='utf-8')

            # Renderizar PNG con Chrome
            jpg_path = output_dir / f"slide-{i+1:02d}.jpg"
            try:
                chrome_render(str(html_path), str(jpg_path))
                png_path = Path(str(jpg_path).replace('.jpg', '.png'))
                generated.append(str(png_path if png_path.exists() else jpg_path))
            except Exception as e:
                logger.error(f"Error renderizando slide {i+1}: {e}")
                generated.append(str(html_path))  # Fallback a HTML

        article.slides_data = {
            'slides': slides,
            'template_style': template_style,
            'bg_image_url': bg_image_url,
            'generated_files': generated,
        }
        article.save()

        return JsonResponse({'ok': True, 'files': generated})
        article.slides_data = {
            'slides': slides, 'template_style': template_style,
            'bg_image_url': bg_image_url, 'generated_files': generated,
        }
        article.save()
        return JsonResponse({'ok': True, 'files': generated})
    except Exception as e:
        logger.error(f"Error generando slides: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def api_download_slides(request, pk):
    """API: Descarga ZIP con los PNGs de slides."""
    article = get_object_or_404(GeneratedArticle, pk=pk)
    slides_data = article.slides_data or {}
    files = slides_data.get('generated_files', [])
    if not files:
        return JsonResponse({'error': 'No hay slides generados'}, status=404)
    zip_path = Path(settings.MEDIA_ROOT) / 'slides' / str(pk) / f'{article.slug}.zip'
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        for f in files:
            fp = Path(f)
            if fp.exists():
                zf.write(str(fp), arcname=fp.name)
    return FileResponse(open(str(zip_path), 'rb'), as_attachment=True, filename=f'{article.slug}-slides.zip')
