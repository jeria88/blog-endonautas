"""
Servicio de generación de contenido para Endonautas.

Incluye:
1. Generación de artículos de blog con DeepSeek
2. Generación de copy RRSS (carrusel + reel) a partir de artículos

Uso:
    from blog.services import generate_article, generate_social_posts
    article = generate_article("Tema del artículo")
    posts = generate_social_posts(article, plataformas=['instagram'], formatos=['carrusel', 'reel'])
"""
import json
import logging
import re

import requests
from django.conf import settings
from django.utils.text import slugify

from blog.models import GeneratedArticle, SocialPost

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = getattr(settings, 'DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')


# ════════════════════════════════════════════════════════════════════════════
# Generación de artículos de blog
# ════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_ARTICLE = """Eres el escritor del blog de Endonautas, una plataforma de exploración del mundo interior.

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
- Usa vocabulario endonáutico: patrón, origen, integrar, mapa, navegar, sombra, máscara
- Evita: transformar, despertar, vibración, manifestar, empoderar
- Extensión: 800-1200 palabras
- Formato HTML (h2, h3, p, ul, li, blockquote)
- Incluye meta description (máx 160 chars)
- Incluye 3-5 keywords SEO separadas por coma"""


def _call_deepseek_article(messages, max_tokens=4000):
    """Llama a la API de DeepSeek para artículos."""
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


def generate_article(topic, source_type='tema', source_detail='', save=True):
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
    source_context = ""
    if source_type == 'test':
        source_context = f"\n\nEste artículo está inspirado en el siguiente test/resultado: {source_detail}"
    elif source_type == 'espejo':
        source_context = f"\n\nEste artículo está inspirado en una sesión del Espejo: {source_detail}"
    elif source_type == 'keyword':
        source_context = f"\n\nEste artículo debe optimizarse para la keyword SEO: {topic}"

    prompt = f"""Genera un artículo de blog sobre: "{topic}"{source_context}

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

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_ARTICLE},
        {"role": "user", "content": prompt},
    ]

    logger.info(f"Generando artículo: {topic[:60]}...")
    raw = _call_deepseek_article(messages)
    data = json.loads(raw)

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


# ════════════════════════════════════════════════════════════════════════════
# Generación de copy RRSS
# ════════════════════════════════════════════════════════════════════════════

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

El carrusel debe tener esta estructura:
1. GANCHO (portada): Frase que detiene el scroll, máximo 150 chars. Debe ser impactante, pregunta provocadora o afirmación contraintuitiva.
2. CUERPO (3-5 slides): Cada slide desarrolla UNA idea clave del artículo. Máximo 200 chars por slide. Texto claro y directo.
3. CTA (slide cierre): Llamada a la acción que invita a ir a endonautas.cl. Máximo 150 chars.

Devuelve JSON exactamente así:
{{
    "gancho": "Texto del gancho/portada (máx 150 chars)",
    "cuerpo": [
        "Slide 2: idea 1 (máx 200 chars)",
        "Slide 3: idea 2 (máx 200 chars)",
        "Slide 4: idea 3 (máx 200 chars)"
    ],
    "cta": "Texto CTA cierre (máx 150 chars, incluye mención a endonautas.cl)",
    "descripcion": "Descripción completa para Instagram (máx 2200 chars, incluye pregunta final y CTA)",
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


# ════════════════════════════════════════════════════════════════════════════
# Temas SEO/GEO de 3 capas para generación de artículos
# ════════════════════════════════════════════════════════════════════════════

# Cada tema tiene: (título, capa SEO, keywords sugeridos, CTA sugerido)
BLOG_TOPICS = [
    # ── Capa 1: Autoconocimiento (volumen, búsqueda activa) ──
    ("Cómo conocerse a sí mismo: guía práctica para empezar",
     "capa1", "autoconocimiento, conocerse a uno mismo, psicología personal", "/mascara/"),
    ("Qué es el autoconocimiento y por qué importa",
     "capa1", "autoconocimiento, desarrollo personal, crecimiento interior", "/mascara/"),
    ("Señales de que necesitas conocerte mejor",
     "capa1", "autoconocimiento, señales, desarrollo personal", "/hacks/"),
    ("Los 5 tipos de personalidad según la psicología",
     "capa1", "tipos de personalidad, psicología, autoconocimiento", "/mascara/"),
    ("Cómo identificar tus patrones repetitivos",
     "capa1", "patrones repetitivos, autoconocimiento, psicología", "/hacks/"),

    # ── Capa 2: Viaje interior (intención, personas en proceso) ──
    ("Qué es el viaje interior y en qué se diferencia de la autoayuda",
     "capa2", "viaje interior, trabajo interior, mundo interior", "/viaje/"),
    ("Heridas de infancia: cómo se manifiestan en la vida adulta",
     "capa2", "heridas de infancia, infancia, relaciones, psicología", "/mascara/"),
    ("La máscara que usas para sobrevivir (y cómo reconocerla)",
     "capa2", "máscara, personalidad, autoconocimiento, sombra", "/mascara/"),
    ("Patrones repetitivos en el amor: por qué eliges siempre lo mismo",
     "capa2", "patrones en el amor, relaciones, apego, psicología", "/viaje/"),
    ("El autosabotaje: cómo tu propia sombra boicotea tus logros",
     "capa2", "autosabotaje, sombra, jung, psicología", "/hacks/"),
    ("Herida de abandono: cómo se manifiesta en las relaciones",
     "capa2", "herida de abandono, relaciones, apego, psicología", "/mascara/"),
    ("Herida de rechazo: el miedo a no ser suficiente",
     "capa2", "herida de rechazo, autoestima, psicología", "/mascara/"),
    ("La máscara del salvador: ayudar para no ser vulnerable",
     "capa2", "máscara del salvador, relaciones, límites", "/mascara/"),
    ("Del dolor al patrón: cómo usar tu historia como brújula",
     "capa2", "dolor, patrón, historia personal, crecimiento", "/viaje/"),

    # ── Capa 3: Nivel de conciencia (brand, retención, conversión) ──
    ("Qué es la endonáutica: el mapa del mundo interior",
     "capa3", "endonáutica, cartografía interior, mapa interior", "/viaje/"),
    ("Cómo aumentar tu nivel de conciencia en 30 días",
     "capa3", "nivel de conciencia, expansión de conciencia, crecimiento", "/viaje/"),
    ("La sombra según Jung: integrar lo que rechazas de ti",
     "capa3", "sombra, jung, integración, psicología analítica", "/hacks/"),
    ("Eneagrama tipo 2: el ayudante que olvida sus propias necesidades",
     "capa3", "eneagrama tipo 2, eneagrama, personalidad", "/mascara/"),
    ("Eneagrama tipo 4: la búsqueda de autenticidad en la melancolía",
     "capa3", "eneagrama tipo 4, eneagrama, autenticidad", "/mascara/"),
    ("Apego ansioso en adultos: cuando la incertidumbre se siente como abandono",
     "capa3", "apego ansioso, apego, relaciones, psicología", "/viaje/"),
    ("Big Five: qué dice tu apertura a la experiencia sobre ti",
     "capa3", "big five, personalidad, psicología, test de personalidad", "/mascara/"),
    ("Heridas de infancia en la pareja: el origen de los conflictos",
     "capa3", "heridas de infancia, pareja, conflictos, relaciones", "/mascara/"),
]

# Helper functions
def get_topic_title(topic_tuple):
    return topic_tuple[0]

def get_topic_capa(topic_tuple):
    return topic_tuple[1]

def get_topic_keywords(topic_tuple):
    return topic_tuple[2]

def get_topic_cta(topic_tuple):
    return topic_tuple[3]

BLOG_TOPIC_TITLES = [t[0] for t in BLOG_TOPICS]


# ════════════════════════════════════════════════════════════════════════════
# Búsqueda de imágenes en Pexels
# ════════════════════════════════════════════════════════════════════════════

PEXELS_API_KEY = getattr(settings, 'PEXELS_API_KEY', '')

def search_pexels_images(query, count=6):
    """
    Busca imágenes en Pexels relacionadas con un tema.
    
    Args:
        query: Término de búsqueda en inglés
        count: Cantidad de imágenes (default: 6, max: 80)
    
    Returns:
        Lista de dicts con: id, url_landscape, url_portrait, photographer, photographer_url
    """
    if not PEXELS_API_KEY:
        return []

    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": min(count, 80), "orientation": "landscape"}
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            images = []
            for photo in data.get("photos", []):
                images.append({
                    "id": photo["id"],
                    "url": photo["src"]["landscape"],
                    "url_small": photo["src"]["medium"],
                    "photographer": photo["photographer"],
                    "photographer_url": photo["photographer_url"],
                })
            return images
    except Exception as e:
        logger.error(f"Error buscando imágenes Pexels: {e}")
    return []
