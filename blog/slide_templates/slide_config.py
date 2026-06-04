"""
Configuración de templates de slides para carruseles Endonautas.
Cada template define su nombre, archivo HTML base, y campos editables.
"""

SLIDE_TEMPLATES = [
    {
        "id": "portada",
        "label": "Portada",
        "file": "slide-01.html",
        "fields": ["title", "body", "cta"],
    },
    {
        "id": "problema",
        "label": "Problema",
        "file": "slide-02.html",
        "fields": ["tag", "title", "body"],
    },
    {
        "id": "diferenciacion",
        "label": "Diferenciación",
        "file": "slide-03.html",
        "fields": ["tag", "title", "body"],
    },
    {
        "id": "definicion",
        "label": "Definición",
        "file": "slide-04.html",
        "fields": ["tag", "title", "body"],
    },
    {
        "id": "cta",
        "label": "CTA Final",
        "file": "slide-05.html",
        "fields": ["title", "body"],
    },
]


def get_template_by_id(template_id):
    """Devuelve un template por su ID."""
    for t in SLIDE_TEMPLATES:
        if t["id"] == template_id:
            return t
    return SLIDE_TEMPLATES[0]


def get_templates_json():
    """Devuelve los templates como JSON para el frontend."""
    import json
    return json.dumps(SLIDE_TEMPLATES, ensure_ascii=False)
