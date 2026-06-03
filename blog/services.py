"""
Servicio de generación de contenido RRSS a partir de artículos del blog.

A partir de un artículo (GeneratedArticle o BlogPost), genera:
1. Copy para carrusel (slides)
2. Copy para descripción del carrusel
3. Copy para reel (texto en pantalla)
4. Copy para descripción del reel

Uso:
    from blog.services import generate_social_posts
    posts = generate_social_posts(article, plataformas=['instagram'], formatos=['carrusel', 'reel'])
"""
import logging
import re

import requests
from django.conf import settings
from django.utils.text import slugify

from blog.models import SocialPost

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = getattr(settings, 'DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')


SYSTEM_PROMPT_RRSS = """Eres el community manager de Endonautas, una plataforma de exploración del mundo interior.

Tu trabajo es crear contenido para redes sociales a partir de artículos del blog.

Tono:
- Profundo pero accesible
- Cálido, como un guía que acompaña
- Sin jerga académica ni promesas de transformación instantánea
- Con vocabulario endonáutico: patrón, origen, mapa, sombra, máscara, viaje interior
- Evita: transformar, despertar, vibración, manifestar, empoderar, abundancia

Formato de salida: JSON válido."""


def _call_deepseek(messages, max_tokens=4000):
    """Llama a la API de DeepSeek."""
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY no configurada")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"DeepSeek API error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def _parse_json(raw):
    """Parsea JSON de la respuesta de DeepSeek."""
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        raw = json_match.group()
    import json
    return json.loads(raw)


def _get_article_content(article):
    """Extrae el contenido de un artículo (GeneratedArticle o BlogPost)."""
    if hasattr(article, 'body') and isinstance(article.body, str):
        # GeneratedArticle
        return {
            'title': article.title,
            'intro': article.intro or '',
            'body': article.body,
            'keywords': article.keywords or '',
            'tags': article.tags or '',
        }
    elif hasattr(article, 'body') and hasattr(article.body, '__iter__'):
        # BlogPost (Wagtail StreamField)
        body_text = []
        for block in article.body:
            if block.block_type == 'richtext':
                body_text.append(str(block.value))
        return {
            'title': article.title,
            'intro': article.intro or '',
            'body': '\n\n'.join(body_text),
            'keywords': '',
            'tags': ', '.join(t.name for t in article.tags.all()) if hasattr(article, 'tags') else '',
        }
    return {'title': str(article), 'intro': '', 'body': '', 'keywords': '', 'tags': ''}


def generate_carrusel_copy(article):
    """
    Genera copy para carrusel de Instagram a partir de un artículo.

    Returns:
        dict con: slides (lista de textos), descripcion, hashtags
    """
    content = _get_article_content(article)

    prompt = f"""Genera el copy para un carrusel de Instagram basado en este artículo:

TÍTULO: {content['title']}
INTRO: {content['intro']}
CONTENIDO: {content['body'][:2000]}
KEYWORDS: {content['keywords']}

El carrusel debe tener:
1. Portada (hook que detenga el scroll)
2. 3-5 slides de contenido (una idea por slide, desarrollada)
3. Slide de cierre con CTA hacia endonautas.cl

Devuelve JSON:
{{
    "slides": [
        "Texto portada (hook potente, máx 150 chars)",
        "Texto slide 2 (desarrollo idea 1, máx 200 chars)",
        "Texto slide 3 (desarrollo idea 2, máx 200 chars)",
        "Texto slide 4 (desarrollo idea 3, máx 200 chars)",
        "Texto cierre con CTA (máx 150 chars)"
    ],
    "descripcion": "Descripción del carrusel para Instagram (máx 2200 chars, incluye CTA y pregunta final)",
    "hashtags": "#hashtag1 #hashtag2 #hashtag3 (máx 15 hashtags relevantes)"
}}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_RRSS},
        {"role": "user", "content": prompt},
    ]

    raw = _call_deepseek(messages)
    return _parse_json(raw)


def generate_reel_copy(article):
    """
    Genera copy para reel de Instagram a partir de un artículo.

    Returns:
        dict con: texto_pantalla, descripcion, hashtags
    """
    content = _get_article_content(article)

    prompt = f"""Genera el copy para un Reel de Instagram (15-30 segundos) basado en este artículo:

TÍTULO: {content['title']}
INTRO: {content['intro']}
CONTENIDO: {content['body'][:1500]}

El reel debe:
- Tener un hook potente en los primeros 2 segundos
- Desarrollar UNA idea clave del artículo
- Terminar con CTA hacia endonautas.cl
- La descripción debe mantener el loop (el usuario la lee mientras el video se repite)

Devuelve JSON:
{{
    "texto_pantalla": "Texto que aparece sobre el video (máx 100 chars, frase impactante)",
    "descripcion": "Descripción del reel (máx 1500 chars). Debe funcionar como texto que se lee mientras el video se reproduce en loop. Incluye pregunta final y CTA.",
    "hashtags": "#hashtag1 #hashtag2 (máx 10 hashtags)"
}}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_RRSS},
        {"role": "user", "content": prompt},
    ]

    raw = _call_deepseek(messages)
    return _parse_json(raw)


def generate_social_posts(article, plataformas=None, formatos=None):
    """
    Genera posts de RRSS a partir de un artículo.

    Args:
        article: GeneratedArticle o BlogPost
        plataformas: Lista de plataformas (default: ['instagram'])
        formatos: Lista de formatos (default: ['carrusel', 'reel'])

    Returns:
        Lista de SocialPost creados
    """
    if plataformas is None:
        plataformas = ['instagram']
    if formatos is None:
        formatos = ['carrusel', 'reel']

    posts = []

    for plataforma in plataformas:
        for formato in formatos:
            try:
                if formato == 'carrusel':
                    copy_data = generate_carrusel_copy(article)
                    slides = copy_data.get('slides', [])
                    descripcion = copy_data.get('descripcion', '')
                    hashtags = copy_data.get('hashtags', '')

                    post = SocialPost.objects.create(
                        generated_article=article if isinstance(article, type(article)) and hasattr(article, 'generated_article') else None,
                        blog_post=article if hasattr(article, 'body') and hasattr(article.body, '__iter__') else None,
                        plataforma=plataforma,
                        formato=formato,
                        copy_carrusel='\n---\n'.join(slides),
                        copy_descripcion=f"{descripcion}\n\n{hashtags}",
                        status=SocialPost.STATUS_DRAFT,
                    )
                    posts.append(post)
                    logger.info(f"Carrusel generado: {post}")

                elif formato == 'reel':
                    copy_data = generate_reel_copy(article)
                    texto_pantalla = copy_data.get('texto_pantalla', '')
                    descripcion = copy_data.get('descripcion', '')
                    hashtags = copy_data.get('hashtags', '')

                    post = SocialPost.objects.create(
                        generated_article=article if isinstance(article, type(article)) and hasattr(article, 'generated_article') else None,
                        blog_post=article if hasattr(article, 'body') and hasattr(article.body, '__iter__') else None,
                        plataforma=plataforma,
                        formato=formato,
                        copy_reel_texto=texto_pantalla,
                        copy_reel_descripcion=f"{descripcion}\n\n{hashtags}",
                        status=SocialPost.STATUS_DRAFT,
                    )
                    posts.append(post)
                    logger.info(f"Reel generado: {post}")

            except Exception as e:
                logger.error(f"Error generando {formato} para {plataforma}: {e}")

    return posts
