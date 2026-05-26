# endonautas-platform — Registro de progreso

## 2026-05-26 — Fix CMS login, DNS, brand audit

### ✅ Completado

#### CMS — Wagtail admin funcional
- `seed_admin` management command: crea superuser con email como USERNAME_FIELD, soporta `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars
- Fix `balance.permanent` (no `balance.balance` — es @property sin setter)
- Fix `accounts/signals.py`: `monthly_tokens` → `.get('monthly_fractones', 100)` (KeyError en signup)
- `wagtail.contrib.settings` añadido a INSTALLED_APPS (requerido por wagtailseo — sin él, `/cms/` daba NoReverseMatch 500)
- CMS accesible y funcional en `/cms/`

#### Deploy — Nixpacks restaurado
- Dockerfile y .dockerignore añadidos a `.gitignore` (evitar que Railway cambie de builder)
- `railway.toml` restaurado con `builder = "NIXPACKS"`
- startCommand: `migrate → seed_admin → collectstatic → gunicorn`

#### DNS / Dominio
- `endonautas.cl` → live via Cloudflare CNAME → Railway
- Error 1000 Cloudflare resuelto: eliminados A/AAAA records con IPs de Cloudflare para `www`
- `www` CNAME configurado en Cloudflare, falta registrar en Railway service

#### Brand audit — editorial
- `comunidad.html`: teal → gold en CTA (gradient + color `em` + clase btn)
- `home_page.html`: features reescritas con voz personal del libro, sección autor con foto de Franco, corrección gradient CTA band (`#d4a853` → `rgba(234,179,8,0.04)`)
- `mision.html`: foto circular de Franco en firma

### 🔶 Pendiente

#### www.endonautas.cl
- Registrar `www.endonautas.cl` como custom domain en Railway service Settings → Domains

#### CMS — configuración inicial
- En `/cms/` → Settings → Sites → hostname `endonautas.cl`, puerto 443, root page → HomePage
- Primer post del blog

#### Nav y cross-site
- Nav cross-site: actualizar para ser consistente (Contacto, Comunidad)
- Barra "← volver a endonautas.cl" en mirrorwork para no autenticados

#### Features app
- `sensorial` app: URLs no están wired en `config/urls.py`
- Email vars en Railway para /contacto/: `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`
- Configurar Wagtail Site en CMS post-deploy

---

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

### ✅ Resuelto en 2026-05-26
- DNS Cloudflare configurado → endonautas.cl live
- Superuser creado vía seed_admin (automatizado en startCommand)
- CMS accesible en /cms/
