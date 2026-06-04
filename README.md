# endonautas-platform

Proyecto unificado de Endonautas. Incluye el sitio editorial (home + blog con Wagtail CMS), CRM de email marketing, y CGM (Content Generation Management) para generación de contenido con IA.

**Producción:** https://endonautas.cl — live ✅

---

## Arquitectura

| Capa | Tecnología |
|---|---|
| Backend | Django 6 + Wagtail 7.4 |
| Base de datos | SQLite (dev) · PostgreSQL via `dj-database-url` (prod) |
| IA | DeepSeek API (`deepseek-chat`) |
| Email | Brevo API v3 + SMTP |
| Static files | WhiteNoise + CompressedManifestStaticFilesStorage |
| Deploy | Railway (Nixpacks) |

---

## Apps

### Editorial (Wagtail)
| App | Descripción |
|---|---|
| `home` | HomePage, EndonauticaPage, EquipoPage, MascaraPage. Gestionable desde `/cms/` |
| `blog` | BlogIndexPage + BlogPost (StreamField). Sistema de postulaciones de usuarios. Generación de artículos con IA. |
| `search` | Búsqueda Wagtail |

### CRM + CGM
| App | URL | Descripción |
|---|---|---|
| `crm` | `/crm/` | CRM de email marketing: suscriptores, secuencias, templates, broadcasts, pipeline, tags, segmentos |
| `blog` (CGM) | `/cgm/` | Content Generation Management: artículos IA, copy RRSS, carruseles, reels |

---

## CGM — Content Generation Management

Panel de generación de contenido con IA para las redes sociales de Endonautas.

### URLs
| URL | Descripción |
|---|---|
| `/cgm/` | Dashboard con stats |
| `/cgm/generate/` | Generador paso a paso |
| `/cgm/article/{id}/` | Detalle de artículo |
| `/cgm/social/{id}/` | Detalle de post RRSS |
| `/cgm/download/carrusel/{id}/` | Descargar carrusel (ZIP) |
| `/cgm/download/reel/{id}/` | Descargar reel (MP4) |

### Flujo de generación
1. **Artículo**: Elegí un tema (o escribilo) → DeepSeek genera artículo SEO
2. **Copy RRSS**: Se genera gancho + cuerpo + CTA + hashtags para carrusel y reel
3. **Carrusel PNG**: Usa plantilla profesional (estilos A/B/C) con fondos de Pexels
4. **Reel MP4**: HTML → PNG → ffmpeg → video 15s
5. **Copiar**: Botones "Copiar IG/TT/LI" con texto formateado listo para pegar

### Modelos
- `GeneratedArticle`: artículos generados por IA con estados (draft → review → approved → published)
- `SocialPost`: copy RRSS con campos gancho/cuerpo/CTA/hashtags por formato y por red social

### Management commands
```bash
python manage.py generate_articles --count 3          # Generar 3 artículos
python manage.py generate_articles --topic "Tema"     # Generar sobre tema específico
python manage.py create_content --topic "Tema" --all  # Pipeline completo
python manage.py fetch_brevo_events                   # Traer eventos de Brevo
```

---

## CRM — Email Marketing

### Flywheel de emails
- **Mascara**: 4 emails (días 0/2/4/6)
- **Hacks**: 3 emails (días 0/3/6)
- **Viaje**: 3 emails (días 0/3/6)

### Modelos principales
- `Subscriber`, `EmailList`, `Subscription`
- `EmailTemplate`, `EmailSequence`, `SequenceStep`
- `SentEmail`, `EmailEvent` (tracking de aperturas/clicks)
- `Tag`, `ContactTag`, `Broadcast`
- `PipelineStage`, `PipelineLog`, `ContactNote`, `Segment`

### Tracking de aperturas
- `fetch_brevo_events` command: polling API Brevo cada 15 min
- Dashboard con métricas: open rate, click rate, bounces, unsubscribes

---

## Blog — sistema de postulaciones

Los usuarios de la app pueden postular contenido al blog desde cualquier sesión del Espejo, resultado de test o lectura de nacimiento.

**Flujo:**
1. Usuario hace clic en "Postular al blog" (modal inline en la app)
2. El contenido se pre-rellena desde la fuente — editable antes de enviar
3. La postulación queda en estado `submitted` y espera revisión
4. En `/django-admin/blog/blogsubmission/` → acción "Aprobar" → crea `BlogPost` borrador
5. En `/cms/` → revisar y publicar

---

## Design system — editorial

Paleta P5 (Space Grotesk + Plus Jakarta Sans):
```css
--bg: #000000          --text: #F0E8DC         --muted: #888899
--dim: #555566         --accent: #7ecfa8       --accent2: #7ec8cf
--glass-bg: rgba(255,255,255,0.03)
--font-heading: 'Space Grotesk', sans-serif
--font-serif: 'EB Garamond', Georgia, serif   /* solo títulos editoriales */
--font-ui: 'Plus Jakarta Sans', sans-serif
```

---

## Instalación local

```bash
git clone <repo>
cd endonautas-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 manage.py migrate --settings=config.settings.dev
python3 manage.py seed_admin --settings=config.settings.dev
python3 manage.py runserver --settings=config.settings.dev
```

### Variables de entorno requeridas

```env
SECRET_KEY=
DATABASE_URL=          # inyectado por Railway Postgres
DJANGO_SETTINGS_MODULE=config.settings.production
DEEPSEEK_API_KEY=
BREVO_API_KEY=
BREVO_DEFAULT_LIST_ID=
EMAIL_HOST_USER=       # SMTP Brevo
EMAIL_HOST_PASSWORD=   # SMTP Brevo
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

---

## Deploy (Railway)

El `railway.toml` startCommand ejecuta en orden: `migrate → seed_admin → collectstatic → gunicorn`

**Builder:** Nixpacks. No incluir `Dockerfile` en el repo.

### Estado actual (2026-06-03)
- ✅ endonautas.cl — live
- ✅ CRM completo con tracking de aperturas
- ✅ CGM: generación de artículos, copy RRSS, carruseles, reels
- ✅ Flywheel de emails con 3 listas y secuencias
- ✅ Blog Wagtail con sistema de postulaciones
- ✅ Design system P5 activo
- ⚠️ Chrome headless para renderizado PNG (verificar en Railway)
- ⚠️ `generate_v4.py` path en Railway (para carruseles profesionales)

---

## CMS — gestión editorial

- `/cms/` — Wagtail admin (crear/editar páginas, posts, imágenes)
- `/django-admin/` — Django admin (CRM, CGM, usuarios, tokens)
- `/crm/` — CRM de email marketing
- `/cgm/` — Content Generation Management
