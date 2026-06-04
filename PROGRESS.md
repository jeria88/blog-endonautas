# endonautas-platform — Registro de progreso

## 2026-06-03 — CGM completo: artículos IA + RRSS + carruseles profesionales

### ✅ Completado

#### CGM — Content Generation Management (`/cgm/`)
- Panel web para generación de contenido (no solo management command)
- Dashboard con stats de artículos y posts RRSS
- Generador paso a paso: artículo → copy RRSS → carrusel PNG → reel video
- API AJAX: generate-article, generate-rrss, generate-carrusel, generate-reel
- Descarga de assets: ZIP con PNGs del carrusel, MP4 del reel

#### Generación de artículos con IA
- Modelo `GeneratedArticle` con estados: draft → review → approved → published
- Servicio `blog/services.py`: `generate_article()` con DeepSeek
- 22 temas SEO/GEO de 3 capas (autoconocimiento, viaje interior, nivel de conciencia)
- Cada tema incluye: título, capa, keywords, CTA sugerida
- Management command: `generate_articles` (batch, single, approve, status)
- Método `publish_to_blog()` → crea BlogPost en Wagtail

#### SocialPost — Modelo RRSS completo
- Campos por formato: gancho, cuerpo, CTA, hashtags (carrusel/reel/post)
- Campos por red social: copy_instagram, copy_tiktok, copy_linkedin
- Método `build_formatted_copy()` → construye texto completo automáticamente
- Admin CRUD con botones "Copiar IG/TT/LI" en la lista
- Acción "Construir copy formateado" para generar textos

#### Carruseles profesionales
- Integración con plantilla `generate_v4.py` (estilos A/B/C probados)
- Fondos de Pexels (dark-galaxy, nebula-space)
- Chrome headless → PNG 1080x1080
- Reel: HTML 1080x1920 → PNG → ffmpeg → MP4 15s

#### Blog services.py
- `generate_article()`: genera artículos con DeepSeek
- `generate_carrusel_copy()`: slides + descripción + hashtags
- `generate_reel_copy()`: texto pantalla + descripción loop + hashtags
- `generate_social_posts()`: crea SocialPost a partir de artículo
- `BLOG_TOPICS`: 22 temas con mapeo SEO/GEO de 3 capas

### 🔶 Pendiente
- Migración de SocialPost (nuevos campos) — requiere makemigrations
- Verificar que `generate_v4.py` existe en Railway (path `/brand/social/plantilla/`)
- Instalar Chrome headless en Railway para renderizado PNG

---

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

#### Tracking de aperturas/clicks (Capa 2)
- Modelo `EmailEvent` para guardar eventos de Brevo
- `fetch_brevo_events` command: polling API Brevo cada 15 min
- `brevo_api.py` devuelve 3 valores (ok, error, message_id)
- Dashboard con métricas: open rate, click rate, bounces, unsubscribes

#### Infraestructura
- `scripts/start.sh`: extrae startCommand de railway.toml a script legible con `set -e`
- `railway.toml`: `startCommand = "bash scripts/start.sh"` (antes era 1 línea de 400 chars)

#### Bugs corregidos
- `home/views.py`: ImportError `trigger_sequence` → `_send_sequence_email`
- `home/views.py`: `.delay()` sin worker reemplazado por llamada síncrona del paso 0
- `production.py`: `POST_OFFICE CELERY_ENABLED: False` (sin worker real)
- `setup_flywheel`: eliminado `_setup_periodic_tasks` (celery-beat sin worker)
- Nav links rotos en templates CRM (malformed `{% url %}` tags)

### 🔶 Pendiente
- Railway env vars: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (SMTP Brevo)
- CMS: instancias Wagtail por crear en `/cms/`
- Hotmart: `HOTMART_PACK_200/600/2000` cuando se creen los packs

---

## 2026-05-29 — Design system P5, nuevas páginas Wagtail, copy finalizado
[Ver PROGRESS.md completo para detalles anteriores]
