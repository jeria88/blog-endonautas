"""
Vistas del CGM — Content Generation Management.
"""
import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from blog.models import GeneratedArticle, SocialPost, BlogPost
from blog.services import (
    generate_article, generate_carrusel_copy, generate_reel_copy,
    BLOG_TOPICS, get_topic_title,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(settings.BASE_DIR)
SOCIAL_BASE = BASE_DIR.parent / 'brand' / 'social' / 'plantilla'


# ════════════════════════════════════════════════════════════════════════════
# Páginas
# ════════════════════════════════════════════════════════════════════════════

@staff_member_required
def cgm_dashboard(request):
    """Dashboard principal del CGM."""
    articles = GeneratedArticle.objects.all()[:20]
    recent_articles = GeneratedArticle.objects.all()[:6]
    social_posts = SocialPost.objects.all()[:10]

    # Temas sugeridos (los primeros 8)
    suggested_topics = [
        {'title': get_topic_title(t), 'capa': t[1], 'keywords': t[2]}
        for t in BLOG_TOPICS[:8]
    ]

    context = {
        'tab': 'dashboard',
        'articles': articles,
        'recent_articles': recent_articles,
        'social_posts': social_posts,
        'total_articles': GeneratedArticle.objects.count(),
        'total_social': SocialPost.objects.count(),
        'total_published': GeneratedArticle.objects.filter(status=GeneratedArticle.STATUS_PUBLISHED).count(),
        'topics_count': len(BLOG_TOPICS),
        'suggested_topics': suggested_topics,
    }
    return render(request, 'blog/cgm/dashboard.html', context)


@staff_member_required
def cgm_articles(request):
    """Lista de artículos con CRUD."""
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
    """Editor de un artículo."""
    article = get_object_or_404(GeneratedArticle, pk=pk)
    return render(request, 'blog/cgm/article_edit.html', {
        'tab': 'articles',
        'article': article,
    })


@staff_member_required
def cgm_rrss(request):
    """Generador de contenido RRSS."""
    articles = GeneratedArticle.objects.filter(status__in=['draft', 'review', 'approved'])
    social_posts = SocialPost.objects.all()[:20]

    # Si viene un artículo seleccionado
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
        return JsonResponse({
            'ok': True,
            'article_id': article.pk,
            'title': article.title,
            'slug': article.slug,
            'status': article.status,
        })
    except Exception as e:
        logger.error(f"Error generando artículo: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_save_article(request, pk):
    """API: Guarda los cambios de un artículo."""
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
        article.status = data.get('status', article.status)
        article.save()

        return JsonResponse({'ok': True})
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_delete_article(request, pk):
    """API: Elimina un artículo."""
    try:
        article = GeneratedArticle.objects.get(pk=pk)
        article.delete()
        return JsonResponse({'ok': True})
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)


@staff_member_required
@require_POST
def api_publish_article(request, pk):
    """API: Publica un artículo en Wagtail."""
    try:
        article = GeneratedArticle.objects.get(pk=pk)
        ok, msg = article.publish_to_blog()
        if ok:
            return JsonResponse({'ok': True, 'msg': msg})
        else:
            return JsonResponse({'error': msg}, status=400)
    except GeneratedArticle.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)


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
    formato = data.get('formato', 'carrusel')

    try:
        if formato == 'carrusel':
            copy_data = generate_carrusel_copy(article)
            post = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=formato,
                carrusel_gancho=copy_data.get('slides', [''])[0] if copy_data.get('slides') else '',
                carrusel_cuerpo='\n---\n'.join(copy_data.get('slides', [])[1:]) if len(copy_data.get('slides', [])) > 1 else '',
                carrusel_cta='Descubre más en endonautas.cl',
                carrusel_hashtags=copy_data.get('hashtags', ''),
                carrusel_descripcion=copy_data.get('descripcion', ''),
                copy_instagram=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_tiktok=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_linkedin=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
            )
        elif formato == 'reel':
            copy_data = generate_reel_copy(article)
            post = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=formato,
                reel_gancho=copy_data.get('texto_pantalla', ''),
                reel_cuerpo=copy_data.get('descripcion', ''),
                reel_ctA='Descubrí más en endonautas.cl',
                reel_hashtags=copy_data.get('hashtags', ''),
                reel_descripcion=copy_data.get('descripcion', ''),
                copy_instagram=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_tiktok=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_linkedin=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
            )
        else:  # post
            copy_data = generate_carrusel_copy(article)
            post = SocialPost.objects.create(
                generated_article=article,
                plataforma=plataforma,
                formato=formato,
                post_gancho=copy_data.get('slides', [''])[0] if copy_data.get('slides') else '',
                post_cuerpo='\n\n'.join(copy_data.get('slides', [])[1:]) if len(copy_data.get('slides', [])) > 1 else '',
                post_cta='Descubrí más en endonautas.cl',
                post_hashtags=copy_data.get('hashtags', ''),
                copy_instagram=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_tiktok=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
                copy_linkedin=copy_data.get('descripcion', '') + '\n\n' + copy_data.get('hashtags', ''),
            )

        return JsonResponse({
            'ok': True,
            'post_id': post.pk,
            'plataforma': plataforma,
            'formato': formato,
        })
    except Exception as e:
        logger.error(f"Error generando RRSS: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def api_delete_social_post(request, pk):
    """API: Elimina un post RRSS."""
    try:
        post = SocialPost.objects.get(pk=pk)
        post.delete()
        return JsonResponse({'ok': True})
    except SocialPost.DoesNotExist:
        return JsonResponse({'error': 'Post no encontrado'}, status=404)
