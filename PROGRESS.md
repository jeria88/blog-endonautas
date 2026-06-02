# endonautas-platform — Registro de progreso

## 2026-06-02 — CRM flywheel completo + scheduler interno

### ✅ Completado

#### CRM — módulo completo (`crm/`)
- Modelos: `Subscriber`, `EmailList`, `Subscription`, `EmailTemplate`, `EmailSequence`, `SequenceStep`, `SentEmail`
- Email engine: `django-post-office` como backend, despacho a Brevo SMTP en producción
- Lógica pura en `_send_sequence_email` y `_process_sequence_steps` (llamables sin Celery)
- Wrappers Celery como capa opcional, no requerida
- Admin Django completo con todos los modelos registrados

#### Frontend CRM (`/crm/`)
- Dashboard con stats (suscriptores, secuencias, plantillas, enviados, fallidos)
- Cards por lista del flywheel con contador y secuencias activas
- Vista suscriptores con filtro por lista y búsqueda por email
- Vista secuencias como cards con visualización de pasos encadenados
- Vista plantillas con preview en iframe
- Design system CSS consistente (dark, variables `--crm-*`)

#### Flywheel de emails — 3 listas con secuencias completas (`setup_flywheel`)
- **Mascara**: 4 emails (días 0/2/4/6) — entrega, profundización, conexión, CTA app
- **Hacks**: 3 emails (días 0/3/6) — entrega, el error más común, CTA app
- **Viaje**: 3 emails (días 0/3/6) — entrega, por qué se da vueltas, CTA app
- Copy en español neutro (sin argentinismos)
- Comando idempotente (get_or_create en todo)

#### Scheduler interno (`run_scheduler.py`)
- Loop liviano en background dentro del container
- Flywheel: cada 1 hora (`_process_sequence_steps`)
- Despacho SMTP: cada 5 minutos (`send_queued_mail`)
- Arranca automáticamente con el deploy via `scripts/start.sh &`
- No requiere Celery worker, Redis, ni Railway Cron Jobs manuales

#### Infraestructura
- `scripts/start.sh`: extrae startCommand de railway.toml a script legible con `set -e`
- `railway.toml`: `startCommand = "bash scripts/start.sh"` (antes era 1 línea de 400 chars)

#### Bugs corregidos
- `home/views.py`: ImportError `trigger_sequence` → `_send_sequence_email`
- `home/views.py`: `.delay()` sin worker reemplazado por llamada síncrona del paso 0
- `production.py`: `POST_OFFICE CELERY_ENABLED: False` (sin worker real)
- `setup_flywheel`: eliminado `_setup_periodic_tasks` (celery-beat sin worker)

### 🔶 Pendiente

#### Railway env vars — confirmar que existen
- `EMAIL_HOST_USER` — email login SMTP Brevo
- `EMAIL_HOST_PASSWORD` — SMTP key de Brevo

#### CMS — instancias Wagtail por crear en /cms/
- `HacksPage` (slug: `hacks`) como hija de HomePage
- `ViajePage` (slug: `viaje`) como hija de HomePage
- `EquipoPage` (slug: `equipo`) como hija de HomePage

#### Hotmart
- `HOTMART_PACK_200/600/2000` — cuando se creen los packs

---

## 2026-05-29 — Design system P5, nuevas páginas Wagtail, copy finalizado

### ✅ Completado

#### Design system — rework completo
- Tipografía: `EB Garamond + Inter` → `Space Grotesk` (headings/UI) + `Plus Jakarta Sans` (body)
- Paleta: gold `#EAB308` → P5 jade `#7ecfa8` ↔ turquoise `#7ec8cf`
- Animaciones CSS: `@keyframes p5` (color shift), `p5-glow` (text-shadow), `p5-border-left`, `p5-border`, `p5-bg`
- V4 cards: `background: #0b0b14; border-left: 2px solid; animation: p5-border-left 5s`
- Logo en nav con efecto grayscale→color en hover + `.nav-logo-word` con animación P5
- WhatsApp FAB: position fixed bottom-right, P5 glow

#### Nuevas páginas Wagtail — `home/models.py`
- `EndonauticaPage`: headline, intro, hotmart_url, hotmart_cta, features (StreamField), excerpt
- `MascaraPage`: headline, subheadline, description, brevo_list_id, hotmart_url, thank_you_text
- `EquipoPage`: intro, bio, photo_url
- Migración `0002_endonauticapage_equipopage_mascarapage` aplicada

#### Templates nuevos
- `endonautica_page.html`: redesign completo — H1 "Endonautica.", img-wrap grayscale→color, quote, tres territorios, "el endonauta se reconoce", CTA
- `equipo_page.html`: hero, misión (quote grande), visión (3 cards V4), Franco portrait, paradox note, comunidad con CTAs
- `mascara_page.html`: lead magnet con form AJAX → Brevo API v3

#### Nav y rutas
- Nav actualizado: Blog · Endonautica · Equipo · Empezar → (eliminados MÁSCARA y Misión)
- Eliminadas rutas `/mision/` y `/comunidad/` de `config/urls.py` — contenido integrado en `/equipo/`
- Brevo subscribe endpoint: `POST /suscribir/` — `@csrf_exempt @require_POST`, JSON `{ok: true/false}`
- `settings/production.py`: `BREVO_API_KEY`, `BREVO_DEFAULT_LIST_ID`

#### Auditoría de links y copy
- Audit completo: todos los `ebook.endonautas.cl` → `endonautas.cl/endonautica/` (platform + mirrorwork)
- Copy finalizado en todas las páginas: home, endonautica, equipo, blog
- H1 home: "El mundo interior tiene estructura", eyebrow "Método endonauta"
- Blog: H1 "Blog", sub con voz propia, empty state con links contextuales

### 🔶 Pendiente

#### CMS — instancias a crear
- `EquipoPage` (slug: `equipo`) como hija de HomePage
- `MascaraPage` (slug: `mascara`) como hija de HomePage
- EndonauticaPage `hotmart_url` → vacío hasta crear productos en Hotmart

#### Railway env vars
- `BREVO_API_KEY` — requerido por `/suscribir/`
- `HOTMART_PACK_200/600/2000` — cuando se creen los packs en Hotmart

#### Dominio
- Registrar `www.endonautas.cl` como custom domain en Railway service Settings → Domains

---

## 2026-05-28 — Deploy estable, Wagtail operativo, GA4 + Search Console

### ✅ Completado

#### Deploy Railway — fix BD rota
- `wsgi.py`: cambiado setdefault a `config.settings.production` (era dev/SQLite → 500 en todo)
- `prepare_db`: DROP SCHEMA CASCADE cuando `auth_user` ausente → migrate limpio sin estados parciales
- `seed_superuser`: crea superusuario desde env vars `DJANGO_SUPERUSER_*` (idempotente)
- `seed_wagtail`: recrea HomePage y Wagtail Site automáticamente en cada deploy limpio
- `railway.toml` startCommand actualizado con el orden correcto: prepare_db → migrate → seed_superuser → seed_wagtail → seed_centro → collectstatic → gunicorn

#### Wagtail — CMS operativo
- Homepage publicada en endonautas.cl (seed_wagtail la recrea si BD es reseteada)
- Blog `/blog/` activo con `BlogIndexPage` publicada en CMS
- Sitemap Wagtail registrado en urls.py → `endonautas.cl/sitemap.xml` funcional

#### Analytics y SEO
- GA4 configurado: `G-MY610BSBE8` en `base_editorial.html` (endonautas.cl)
- GA4 configurado: `G-5R7E1N116S` en mirrorwork `base.html` (app.endonautas.cl)
- Google Search Console: verificado via DNS Cloudflare, sitemap enviado
- GEO: `llms.txt` + `robots.txt` con allowlist AI bots ya estaban activos

### 🔶 Pendiente

#### www.endonautas.cl
- Registrar `www.endonautas.cl` como custom domain en Railway service Settings → Domains

#### Features app
- Email vars Railway: `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`
- Hotmart packs: 3 productos + vars `HOTMART_PACK_200/600/2000` en Railway
- Conectar fractones en features: Espejo (spend), AI Insights (spend), onboarding (credit_mission)

---

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
