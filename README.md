# endonautas-platform

Proyecto unificado de Endonautas. Incluye el sitio editorial (home + blog con Wagtail CMS) y todos los módulos de la app MirrorWork (psicometría, Espejo de Conflictos, lecturas de nacimiento, comunidad, tokens).

**Producción:** https://endonautas.cl (DNS Cloudflare pendiente de configurar)

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
--dim: #52525b         --gold: #d4a853         --teal: #4ecdc4
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
python3 manage.py createsuperuser --settings=config.settings.dev
python3 manage.py runserver --settings=config.settings.dev
```

### Variables de entorno requeridas en Railway

```env
SECRET_KEY=
DATABASE_URL=          # inyectado por Railway Postgres
DJANGO_SETTINGS_MODULE=config.settings.production
DEEPSEEK_API_KEY=
```

---

## Deploy (Railway)

El `Procfile` ejecuta en orden: `migrate → seed_tests → seed_missions → seed_mirror_kb → collectstatic → gunicorn`

### Pasos pendientes post-deploy
1. `python manage.py createsuperuser --settings=config.settings.production`
2. En `/cms/` → Settings → Sites → configurar hostname `endonautas.cl` y apuntar a `HomePage`
3. Cloudflare DNS: `endonautas.cl` → Railway service URL (CNAME)

---

## CMS — gestión editorial

- `/cms/` — Wagtail admin (crear/editar páginas, posts, imágenes)
- `/django-admin/` — Django admin (usuarios, tokens, postulaciones al blog)

Para crear un post del blog: `/cms/` → Pages → Blog → Add child page → BlogPost
