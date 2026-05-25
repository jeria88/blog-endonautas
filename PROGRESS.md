# endonautas-platform — Registro de progreso

## 2026-05-25 — Deploy inicial + blog submission pipeline

### ✅ Completado

#### Deploy en Railway
- Configuración de `config.settings.production` con `dj_database_url`
- `django.contrib.postgres` en INSTALLED_APPS (requerido por Wagtail SearchVectorField)
- `STATICFILES_DIRS` condicional (evita error si `/static` no existe en Railway)
- Procfile con orden correcto: migrate → seeds → collectstatic → gunicorn
- Deploy exitoso, sitio live en Railway

#### Editorial — Wagtail
- `HomePage` con campos: tagline, intro, cta_app_text/url, cta_ebook_text/url
- `BlogIndexPage` + `BlogPost` (StreamField richtext + imagen, tags, author_name, is_community)
- Template `home_page.html` — hero serif grande, glass-cards features, aurora aesthetic
- Template `blog_index_page.html` — grid de tarjetas con date, tags, community badge
- Template `blog_post.html` — artículo completo con JSON-LD Article schema
- `base_editorial.html` — sistema de diseño completo: EB Garamond + aurora + gold + glass-card

#### Blog — sistema de postulaciones de usuarios
- `BlogSubmission` model: source_type (espejo/test/birth/free), status machine (draft→submitted→approved/rejected), FK a ConflictSession / TestResult / BirthReport
- Vistas: picker, create (pre-fill desde fuente), edit, list, delete
- Endpoint AJAX: `GET /blog/postular/prefill/<type>/<id>/` → JSON con title + body
- `submission_create` responde JSON cuando `X-Requested-With: XMLHttpRequest`
- Django admin con acciones "Aprobar" (crea BlogPost borrador en Wagtail) y "Rechazar"
- Wagtail snippet: "Postulaciones" visible en `/cms/` sidebar

#### SEO / GEO
- `robots.txt` con allowlist de AI bots (GPTBot, ClaudeBot, Googlebot-Extended, etc.)
- `llms.txt` con descripción del proyecto para modelos de lenguaje
- JSON-LD WebSite schema en homepage, Article schema en BlogPost

### 🔶 Pendiente

#### DNS / Dominio
- Configurar Cloudflare: `endonautas.cl` → Railway service URL
- Crear superuser en Railway: `python manage.py createsuperuser --settings=config.settings.production`
- En `/cms/` → Sites → hostname `endonautas.cl`, apuntar a HomePage

#### Nav unificado cross-site
- Añadir Contacto y Comunidad (RRSS) al nav de `base_editorial.html`
- Actualizar nav de endonautica-landing para ser consistente
- Barra "← volver a endonautas.cl" en mirrorwork para usuarios no autenticados

#### Templates de la app
- Los templates de mirrorwork no están en este repo — están en `/home/nikka/Proyectos/mirrorwork/templates/`
- Para el deploy unificado: añadir ese path a `TEMPLATES[0]['DIRS']` en settings, o copiar templates

#### Features pendientes
- `sensorial` app: URLs no están wired en `config/urls.py`
- Configurar superuser y primera HomePage en Wagtail CMS (post-deploy)
- Primer post del blog (editorial o desde una postulación)
