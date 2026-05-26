# endonautas-platform

Proyecto unificado de Endonautas. Incluye el sitio editorial (home + blog con Wagtail CMS) y todos los módulos de la app MirrorWork (psicometría, Espejo de Conflictos, lecturas de nacimiento, comunidad, tokens).

**Producción:** https://endonautas.cl — live ✅

---

## Arquitectura

| Capa | Tecnología |
|---|---|
| Backend | Django 6 + Wagtail 7.4 |
| Base de datos | SQLite (dev) · PostgreSQL via `dj-database-url` (prod) |
| IA | DeepSeek API (`deepseek-chat`) |
| Static files | WhiteNoise + CompressedManifestStaticFilesStorage |
| Deploy | Railway (Nixpacks) |

---

## Apps

### Editorial (Wagtail)
| App | Descripción |
|---|---|
| `home` | HomePage con hero, features, CTAs. Gestionable desde `/cms/` |
| `blog` | BlogIndexPage + BlogPost (StreamField). Sistema de postulaciones de usuarios |
| `search` | Búsqueda Wagtail |

### App MirrorWork
| App | URL | Descripción |
|---|---|---|
| `accounts` | `/` | Usuario custom (email como USERNAME_FIELD), login/register, dashboard, mapa interior, perfil, onboarding |
| `mirror` | `/espejo/` | Espejo de Conflictos — KB con RAG (40 docs, 97 chunks), chat AJAX con DeepSeek |
| `psychometrics` | `/psicometria/` | 35 tests validados/adaptados/endonautas, evaluador, lecturas de IA |
| `birth` | `/nacimiento/` | Lecturas de Carta Astral, Human Design y Saju |
| `community` | `/comunidad/` | Feed, SharedInsights, reacciones, comentarios, follows |
| `tokens` | `/tokens/` | Fractones — balance, misiones, webhook Hotmart |
| `background` | `/fondos/` | Generador de fondos visuales (cosmos, mandala, psicodélico) |
| `practitioners` | `/practitioners/` | Perfiles temporales de clientes para facilitadores |
| `reports` | `/reportes/` | Dashboard de progreso por dimensión |
| `sensorial` | `/sensorial/` | Ejercicios sensoriales (respiración, etc.) |

---

## Blog — sistema de postulaciones

Los usuarios de la app pueden postular contenido al blog desde cualquier sesión del Espejo, resultado de test o lectura de nacimiento.

**Flujo:**
1. Usuario hace clic en "Postular al blog" (modal inline en la app)
2. El contenido se pre-rellena desde la fuente — editable antes de enviar
3. La postulación queda en estado `submitted` y espera revisión
4. En `/django-admin/blog/blogsubmission/` → acción "Aprobar" → crea `BlogPost` borrador
5. En `/cms/` → revisar y publicar

**URLs de gestión:**
- `/blog/postular/` — picker con todo el contenido del usuario
- `/blog/postulaciones/` — lista de postulaciones del usuario
- `/django-admin/blog/blogsubmission/` — revisión de admin

---

## Los 35 tests

**Clínicos (7):** BFI-44, GAD-7, PHQ-9, PSS-10, TAS-20, Dirty Dozen, SVI

**Adaptados (17):** Jung, DERS-16, MAIA, PSQI, ECR, IBI, Logo-Test, SWB, Cloninger, VIA, RIASEC, MWQ, MOS-SSS, Kolb, CEQ, SOC-29, Neurosensorial

**Endonautas (11):** Eneagrama, Heridas Bourbeau, Autosabotaje, Chakras, DRI, DLQ, CIQ, Rueda de la Vida, MAQ, FSS, Fortalezas Prosociales

---

## Design system — editorial

Paleta EB Garamond + aurora + gold:
```css
--bg: #000000          --text: #ffffff         --muted: #a1a1aa
--dim: #52525b         --gold: #EAB308         --teal: #4ecdc4
--glass-bg: rgba(255,255,255,0.03)
--font-serif: 'EB Garamond', Georgia, serif
--font-ui: 'Inter', system-ui, sans-serif
```

Fondo: 3 blobs aurora (purple `#3b0764`, deep blue `#172554`, dark `#0f2027`) + canvas de 160 estrellas animadas.

---

## Instalación local

```bash
git clone <repo>
cd endonautas-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 manage.py migrate --settings=config.settings.dev
python3 manage.py seed_tests --force --settings=config.settings.dev
python3 manage.py seed_missions --settings=config.settings.dev
python3 manage.py seed_mirror_kb --settings=config.settings.dev
python3 manage.py seed_admin --settings=config.settings.dev    # crea superuser admin con env vars
python3 manage.py runserver --settings=config.settings.dev
```

### Variables de entorno requeridas en Railway

```env
SECRET_KEY=
DATABASE_URL=          # inyectado por Railway Postgres
DJANGO_SETTINGS_MODULE=config.settings.production
DEEPSEEK_API_KEY=
ADMIN_EMAIL=           # email del superuser (default: fjeriacastro@gmail.com)
ADMIN_PASSWORD=        # contraseña del superuser (sin ! — Railway lo interpreta como history expansion)
```

---

## Deploy (Railway)

El `railway.toml` startCommand ejecuta en orden: `migrate → seed_admin → collectstatic → gunicorn`

**Builder:** Nixpacks. No incluir `Dockerfile` en el repo — Railway lo detecta y cambia de builder, rompiendo el deploy.

### Post-deploy (primera vez)
1. Env vars en Railway: `SECRET_KEY`, `DJANGO_SETTINGS_MODULE`, `DEEPSEEK_API_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`
2. `seed_admin` corre automáticamente en cada deploy y crea/actualiza el superuser
3. En `/cms/` → Settings → Sites → hostname `endonautas.cl`, puerto 443, apuntar a `HomePage`

### Estado actual (2026-05-26)
- ✅ endonautas.cl — live, Wagtail CMS accesible en `/cms/`
- ✅ DNS Cloudflare configurado (CNAME → Railway)
- ✅ Superuser creado vía `seed_admin`
- ⚠️ www.endonautas.cl → 404 (CNAME configurado en Cloudflare, falta registrar dominio en Railway service)
- ⚠️ `wagtail.contrib.settings` debe estar en INSTALLED_APPS (requerido por wagtailseo — sin él, login CMS da 500)

---

## CMS — gestión editorial

- `/cms/` — Wagtail admin (crear/editar páginas, posts, imágenes)
- `/django-admin/` — Django admin (usuarios, tokens, postulaciones al blog)

Para crear un post del blog: `/cms/` → Pages → Blog → Add child page → BlogPost
