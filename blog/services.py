"""
Servicio de generación de artículos de blog con DeepSeek.

Uso:
    from blog.services import generate_article
    article = generate_article(
        topic="Herida de abandono en relaciones de pareja",
        source_type="test",
        source_detail="Basado en test de Heridas de Infancia"
    )
"""
import json
import logging
import re

import requests
from django.conf import settings
from django.utils.text import slugify

from blog.models import GeneratedArticle

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = getattr(settings, 'DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')


# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres el escritor del blog de Endonautas, una plataforma de exploración del mundo interior.

Tu voz es:
- Profunda pero accesible, sin jerga académica
- Cálida y cercana, como un guía que acompaña
- Basada en la metodología endonáutica (patrones, arquetipos, sombra, máscara, heridas de infancia)
- Sin promesas de transformación instantánea
- Con metáforas del viaje interior, la navegación, el mapa

Estructura de un artículo:
1. Hook inicial (pregunta o afirmación que genera curiosidad)
2. Desarrollo del concepto (3-4 secciones con subtítulos)
3. Conexión con la experiencia del lector
4. CTA sutil hacia la app de Endonautas

Reglas:
- Usa {{ nombre }} para personalización
- Incluye preguntas retóricas para generar reflexión
- No uses "transformar", "despertar", "vibración", "manifestar"
- Sí usa: patrón, origen, integrar, mapa, navegar, sombra, máscara, proceso, cartografía
- Extensión: 800-1200 palabras
- Formato HTML (h2, h3, p, ul, li, blockquote)
- Incluye meta description (máx 160 chars)
- Incluye 3-5 keywords SEO separadas por coma
- Incluye un CTA (texto + URL sugerida)"""


def _build_user_prompt(topic, source_type, source_detail=""):
    source_context = ""
    if source_type == 'test':
        source_context = f"\n\nEste artículo está inspirado en el siguiente test/resultado: {source_detail}"
    elif source_type == 'espejo':
        source_context = f"\n\nEste artículo está inspirado en una sesión del Espejo: {source_detail}"
    elif source_type == 'keyword':
        source_context = f"\n\nEste artículo debe optimizarse para la keyword SEO: {topic}"

    return f"""Genera un artículo de blog sobre: "{topic}"{source_context}

Devuelve un JSON válido con esta estructura:
{{
    "title": "Título SEO del artículo (máx 70 chars)",
    "slug": "slug-seo-del-articulo",
    "meta_description": "Meta description SEO (máx 160 chars)",
    "keywords": "keyword1, keyword2, keyword3",
    "intro": "Introducción breve (máx 280 chars)",
    "body": "Contenido completo en HTML (h2, h3, p, ul, li, blockquote)",
    "cta_text": "Texto del CTA (máx 80 chars)",
    "cta_url": "URL del CTA (ej: /mascara/, /hacks/, /viaje/)",
    "tags": "tag1, tag2, tag3"
}}"""


# ── API call ────────────────────────────────────────────────────────────────────

def _call_deepseek(messages, max_tokens=4000):
    """Llama a la API de DeepSeek y devuelve el contenido."""
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

    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _parse_response(raw):
    """Parsea la respuesta JSON de DeepSeek."""
    # Intentar extraer JSON si viene con markdown
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        raw = json_match.group()
    return json.loads(raw)


# ── Generación ──────────────────────────────────────────────────────────────────

def generate_article(topic, source_type='tema', source_detail="", save=True):
    """
    Genera un artículo de blog usando DeepSeek.

    Args:
        topic: Tema del artículo
        source_type: 'test' | 'espejo' | 'tema' | 'keyword'
        source_detail: Detalle de la fuente (opcional)
        save: Si True, guarda en la BD como GeneratedArticle

    Returns:
        GeneratedArticle instance o dict con los datos
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(topic, source_type, source_detail)},
    ]

    logger.info(f"Generando artículo: {topic[:60]}...")
    raw = _call_deepseek(messages)
    data = _parse_response(raw)

    # Asegurar slug único
    slug = data.get('slug', slugify(data['title']))[:200]

    if save:
        article, created = GeneratedArticle.objects.update_or_create(
            slug=slug,
            defaults={
                'title': data['title'][:200],
                'meta_description': data.get('meta_description', '')[:160],
                'keywords': data.get('keywords', '')[:300],
                'intro': data.get('intro', '')[:280],
                'body': data.get('body', ''),
                'cta_text': data.get('cta_text', '')[:80],
                'cta_url': data.get('cta_url', ''),
                'tags': data.get('tags', '')[:300],
                'source_type': source_type,
                'source_detail': source_detail[:200],
                'status': GeneratedArticle.STATUS_DRAFT,
            }
        )
        logger.info(f"Artículo {'creado' if created else 'actualizado'}: {article.title}")
        return article

    return data


def generate_articles_batch(topics, source_type='tema'):
    """
    Genera múltiples artículos en batch.

    Args:
        topics: Lista de strings (temas)
        source_type: Tipo de fuente

    Returns:
        Lista de GeneratedArticle creados
    """
    articles = []
    for topic in topics:
        try:
            article = generate_article(topic, source_type=source_type)
            articles.append(article)
        except Exception as e:
            logger.error(f"Error generando artículo '{topic}': {e}")
    return articles


# ── Temas predefinidos ──────────────────────────────────────────────────────────

BLOG_TOPICS = [
    # Heridas de infancia
    "Herida de abandono: cómo se manifiesta en las relaciones",
    "Herida de rechazo: el miedo a no ser suficiente",
    "Herida de humillación: cuando la vergüenza dirige tu vida",
    "Herida de traición: la dificultad de confiar",
    "Herida de injusticia: el perfeccionismo como escudo",

    # Máscaras
    "La máscara del salvador: ayudar para no ser vulnerable",
    "La máscara del fuerte: cuando pedir ayuda se siente como debilidad",
    "La máscara del complaciente: decir sí cuando quieres decir no",
    "La máscara del distante: protegerte del dolor alejando a los demás",
    "La máscara del perfecto: el agotamiento de tener que demostrar",

    # Patrones
    "Patrones repetitivos en el amor: por qué elijo siempre lo mismo",
    "El autosabotaje: cómo tu propia sombra boicotea tus logros",
    "La procrastinación como mecanismo de defensa",
    "El síndrome del impostor y su origen en la infancia",
    "La dependencia emocional: cuando necesitas que el otro te complete",

    # Crecimiento
    "Qué es el viaje interior y por qué es diferente a la autoayuda",
    "Cómo identificar tu patrón dominante en 3 pasos",
    "La sombra según Jung: integrar lo que rechazas de ti",
    "Heridas de infancia en la pareja: el origen de los conflictos",
    "Del dolor al patrón: cómo usar tu historia como brújula",

    # Tests específicos
    "Eneagrama tipo 2: el ayudante que olvida sus propias necesidades",
    "Eneagrama tipo 4: la búsqueda de autenticidad en la melancolía",
    "Eneagrama tipo 6: la lealtad como respuesta al miedo",
    "Big Five: qué dice tu apertura a la experiencia sobre ti",
    "Apego ansioso en adultos: cuando la incertidumbre se siente como abandono",
]
