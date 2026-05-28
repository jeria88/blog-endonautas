from datetime import date
from django.core.management.base import BaseCommand
from centro.models import SetupItem, Tarea, PostContenido


SETUP_ITEMS = [
    # Plataforma — Etapa 0 pendientes
    ('plataforma', 1, 'Railway — vars email: EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_USE_TLS', 'Sin esto el cambio de contraseña no funciona en /contacto/'),
    ('plataforma', 2, 'Railway — vars Hotmart: HOTMART_PACK_200, HOTMART_PACK_600, HOTMART_PACK_2000', 'Agregar los offer codes después de crear los productos en Hotmart'),
    ('plataforma', 3, 'Hotmart — crear 3 productos pack en el dashboard (200/600/2000 fractones)', 'Ir a hotmart.com → Productos → Nuevo producto digital'),
    ('plataforma', 4, 'www.endonautas.cl — registrar dominio en Railway → Settings → Domains', 'Actualmente redirige a 404'),
    ('plataforma', 5, 'Wagtail Site config — hostname endonautas.cl, port 443, root page → HomePage', 'En /cms/ → Settings → Sites'),
    ('plataforma', 6, 'Conectar fractones en Espejo de Conflictos — spend() en espejo_send view', 'Archivo: mirrorwork/mirror/views.py'),
    ('plataforma', 7, 'Conectar fractones en AI Insights — spend() antes de DeepSeek en test_result', 'Archivo: mirrorwork/psychometrics/views.py'),
    ('plataforma', 8, 'credit_mission(user, "onboarding") al final de onboarding_viaje', 'Archivo: mirrorwork/accounts/views.py'),
    # Contenido — Setup one-time
    ('contenido', 1, 'PDF a Google Drive — subir y copiar link público compartible', 'PDF: /home/nikka/Proyectos/endonautas/assets/pdfs/descubre-tu-mascara.pdf'),
    ('contenido', 2, 'ManyChat — crear flujo MASCARA (comentario → DM con link PDF)', 'manychat.com → conectar @endonautas → nuevo flujo'),
    ('contenido', 3, 'ManyChat — crear flujo MAPA (comentario → DM con link app test)', ''),
    ('contenido', 4, 'ManyChat — crear flujo ESPEJO (comentario → DM con link sesión gratis)', ''),
    ('contenido', 5, 'Brevo — secuencia 3 emails post-MASCARA (días 1, 3 y 7)', 'brevo.com → Automatizaciones → Nueva automatización'),
]


TAREAS = [
    # Etapa 0 — completadas (estado listo)
    ('0', 'listo', 0, 'Deploy Railway', 'Plataforma live en endonautas.cl'),
    ('0', 'listo', 1, 'DNS Cloudflare → Railway', 'app.endonautas.cl + endonautas.cl funcionando'),
    ('0', 'listo', 2, 'Redesign visual base_editorial.html', 'Estética ebook, constelaciones, gold'),
    ('0', 'listo', 3, 'Blog submission pipeline', 'Modal postular en mirrorwork'),
    ('0', 'listo', 4, 'Renombre MirrorWork → Endonautas (46 archivos)', ''),
    ('0', 'listo', 5, 'Fix aurora background (fondo púrpura)', 'opacity: 0.0 en las 3 auroras'),
    ('0', 'listo', 6, 'Wagtail CMS operativo — HomePage + Blog publicados', 'seed_wagtail recrea HomePage automáticamente en cada deploy limpio'),
    ('0', 'listo', 7, 'GA4 configurado — endonautas.cl + app.endonautas.cl', 'G-MY610BSBE8 en platform, G-5R7E1N116S en mirrorwork'),
    ('0', 'listo', 8, 'Google Search Console + sitemap.xml activo', 'Verificación DNS Cloudflare, sitemap en /sitemap.xml'),
    # Etapa 0 — pendientes
    ('0', 'pendiente', 0, 'Email vars Railway', 'Para contacto y password reset'),
    ('0', 'pendiente', 1, 'Hotmart packs + vars Railway', '3 productos + offer codes'),
    ('0', 'pendiente', 2, 'www.endonautas.cl en Railway Domains', ''),
    ('0', 'pendiente', 3, 'Conectar fractones en features', 'Espejo + AI insights + onboarding mission'),
    # Etapa 1 — pendientes
    ('1', 'pendiente', 0, 'ManyChat 3 flujos activos y probados', 'MASCARA + MAPA + ESPEJO'),
    ('1', 'pendiente', 1, 'Brevo secuencia 3 emails activa', 'Post-MASCARA días 1, 3, 7'),
    ('1', 'pendiente', 2, 'Primera sesión quincenal — sábado 30/05', 'B11 artículo + carrusel + texto'),
    ('1', 'pendiente', 3, 'Banco de posts sembrado en calendario', '12 posts con fechas programadas'),
    # Etapa 2 — backlog
    ('2', 'pendiente', 0, 'Comunidad Valentinas — mentoría grupal 90d', ''),
    ('2', 'pendiente', 1, 'Certificación 6 meses $3.000', ''),
    ('backlog', 'pendiente', 0, 'Conectar ManyChat → Brevo via webhook', 'Cuando haya volumen'),
    ('backlog', 'pendiente', 1, 'Fondos árbol y archipiélago en mirrorwork', 'Después de lanzamiento'),
    ('backlog', 'pendiente', 2, 'Instrumentos a auditar: ECR, SOC-29, MAIA, DERS-16, PSQI', 'Validación científica completa'),
]


POSTS = [
    # sesión 1 semana 02/06
    ('B11', 'Sanar vs integrar', 'carrusel', 'generado', date(2026, 6, 3), 'A+C'),
    ('B01', 'Para quienes ya leyeron', 'texto', 'generado', date(2026, 6, 5), 'D+C'),
    # sesión 1 semana 09/06
    ('B07', 'Lo que te molesta', 'texto', 'generado', date(2026, 6, 10), 'C'),
    ('B10', 'Síntoma vs mapa', 'carrusel', 'programado', date(2026, 6, 12), 'A+C'),
    # sesión 2 semana 16/06
    ('B17', 'El patrón es la solución', 'texto', 'generado', date(2026, 6, 17), 'A+B'),
    ('B05', 'No analices todavía', 'texto', 'generado', date(2026, 6, 19), 'C'),
    # sesión 2 semana 23/06
    ('B02', 'Solos en su proceso', 'texto', 'generado', date(2026, 6, 24), 'C+D'),
    ('B09', 'Sentir vs estar en', 'carrusel', 'generado', date(2026, 6, 26), 'A+C'),
    # sesión 3 semana 30/06
    ('B14', 'Entender no es suficiente', 'texto', 'generado', date(2026, 7, 1), 'B'),
    ('B20', 'Lo que la autoayuda no dice', 'texto', 'generado', date(2026, 7, 3), 'D+B'),
    # sesión 3 semana 07/07
    ('B04', 'Años en terapia', 'texto', 'generado', date(2026, 7, 8), 'B+E'),
    ('NUEVO', 'Presentación app', 'carrusel', 'generado', date(2026, 7, 10), 'E'),
]


class Command(BaseCommand):
    help = 'Siembra datos iniciales de Centro de Operaciones (idempotente)'

    def handle(self, *args, **options):
        created = 0

        for cat, orden, texto, desc in SETUP_ITEMS:
            _, c = SetupItem.objects.get_or_create(
                texto=texto,
                defaults={'categoria': cat, 'orden': orden, 'descripcion': desc},
            )
            if c:
                created += 1

        for etapa, estado, orden, titulo, desc in TAREAS:
            _, c = Tarea.objects.get_or_create(
                titulo=titulo,
                defaults={'etapa': etapa, 'estado': estado, 'orden': orden, 'descripcion': desc},
            )
            if c:
                created += 1

        for codigo, titulo, tipo, estado, fecha, cta in POSTS:
            _, c = PostContenido.objects.get_or_create(
                codigo=codigo,
                titulo=titulo,
                defaults={'tipo': tipo, 'estado': estado, 'fecha_programada': fecha, 'cta_tipo': cta},
            )
            if c:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'seed_centro: {created} objetos creados'))
