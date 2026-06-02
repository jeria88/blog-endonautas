from django.core.management.base import BaseCommand
from crm.models import EmailList, EmailTemplate, EmailSequence, SequenceStep

# ── Email wrapper ────────────────────────────────────────────────────────────

_EMAIL_OPEN = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400&display=swap');
body{margin:0;padding:0;background-color:#000000;}
p{margin:0 0 16px 0;}
p:last-of-type{margin-bottom:0;}
ul{margin:0 0 16px 0;padding-left:20px;}
li{margin-bottom:8px;}
strong{font-weight:600;}
a{color:#7ecfa8;}
</style>
</head>
<body style="margin:0;padding:0;background-color:#000000;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#000000">
<tr><td align="center" style="padding:48px 16px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#0b0b14;border-radius:10px;overflow:hidden;border-left:4px solid #7ecfa8;">
<!-- brand mark -->
<tr><td style="padding:32px 40px 20px 40px;">
<span style="font-family:'Space Grotesk',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;color:#7ecfa8;text-transform:uppercase;">Endonautas</span>
</td></tr>
<!-- divider -->
<tr><td style="padding:0 40px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-top:1px solid rgba(240,232,220,0.08);font-size:0;line-height:0;">&nbsp;</td></tr></table></td></tr>
<!-- body -->
<tr><td style="padding:32px 40px;font-family:'Plus Jakarta Sans',Georgia,serif;font-size:16px;font-weight:300;line-height:1.8;color:#F0E8DC;">
"""

_FIRMA = """<p style="margin-top:28px;margin-bottom:0;font-family:'Plus Jakarta Sans',Georgia,serif;font-size:15px;font-weight:300;color:#F0E8DC;">— Franco</p>
"""

_EMAIL_CLOSE = """</td></tr>
<!-- footer -->
<tr><td style="padding:20px 40px 28px 40px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-top:1px solid rgba(240,232,220,0.06);padding-top:20px;">
<p style="margin:0;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:11px;line-height:1.7;color:rgba(240,232,220,0.3);">
<a href="https://endonautas.cl" style="color:rgba(240,232,220,0.3);text-decoration:none;">endonautas.cl</a>
&nbsp;&middot;&nbsp;
Recibiste este email porque te suscribiste voluntariamente.
</p>
</td></tr></table>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

_SPAM_NOTE = '<p style="font-size:13px;color:rgba(240,232,220,0.4);margin-top:20px;margin-bottom:0;">Si este correo llegó a spam, márcalo como "no es spam" para recibir los siguientes.</p>'

_APP_CTA = """<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;">
<tr><td align="center">
<a href="https://app.endonautas.cl/accounts/registro/" style="display:inline-block;background-color:#F0E8DC;color:#000000;padding:14px 36px;border-radius:999px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.3px;text-decoration:none;">Crear mi cuenta gratuita →</a>
</td></tr>
</table>"""


def _email(body: str) -> str:
    return _EMAIL_OPEN + body + _FIRMA + _EMAIL_CLOSE


def _greeting() -> str:
    return '<p style="font-size:14px;color:rgba(240,232,220,0.45);margin-bottom:20px;">Hola {{ nombre }},</p>'


# ── Command ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Crea las listas, plantillas y secuencias de email iniciales para el flywheel"

    def handle(self, *args, **options):
        self.stdout.write("Creando listas de email...")

        lists_data = [
            {"name": "Endonautas - Mascara", "slug": "mascara", "description": "Descubre tu Máscara según tu Herida de Infancia"},
            {"name": "Endonautas - Hacks", "slug": "hacks", "description": "3 Hacks de Endonáutica para tu Viaje Interior"},
            {"name": "Endonautas - Viaje", "slug": "viaje", "description": "Guía Paso a Paso para Iniciar el Viaje Interior"},
        ]

        email_lists = {}
        for lst_data in lists_data:
            lst, created = EmailList.objects.get_or_create(slug=lst_data["slug"], defaults=lst_data)
            email_lists[lst_data["slug"]] = lst
            self.stdout.write(f"  {'Creada' if created else 'Existe'}: {lst.name}")

        self.stdout.write("\nCreando plantillas de email...")

        # ── MASCARA ──────────────────────────────────────────────────────────
        mascara_templates = [
            {
                "name": "Mascara - Email 1 - Entrega",
                "slug": "mascara-1",
                "subject": "Tu guía está aquí (y una cosa que noté)",
                "html_content": _email(
                    _greeting() +
                    """<p>Te enviamos la guía <strong>"Descubre tu Máscara según tu Herida de Infancia"</strong>.</p>
<p>Algo que noté: la mayoría de las personas que llegan a esta guía llevan años sabiendo que algo se repite en sus vidas. No saben exactamente qué, pero lo sienten.</p>
<p>Esta guía no va a resolver tu vida. Pero va a hacer algo más útil: va a ponerle nombre a lo que ya sabes.</p>""" +
                    _SPAM_NOTE +
                    """<p style="margin-top:20px;">En el siguiente email te cuento algo sobre por qué la máscara se construye — y por qué no es tu enemiga.</p>"""
                ),
            },
            {
                "name": "Mascara - Email 2 - Profundización",
                "slug": "mascara-2",
                "subject": "Tu máscara no es tu enemiga",
                "html_content": _email(
                    _greeting() +
                    """<p>La máscara tiene mala fama. Suena a algo malo, algo que hay que quitarse.</p>
<p>Pero piénsalo así: eras un niño. No tenías las herramientas que tienes ahora. Y ante algo que no podías procesar, construiste una forma de sobrevivir.</p>
<p>Esa forma funcionó. El problema es que sigue funcionando décadas después, en situaciones que ya no lo necesitan.</p>
<p>No se trata de destruir la máscara. Se trata de verla. Porque lo que no ves, decide por ti.</p>
<p>En la guía vas a encontrar los 5 tipos. Fíjate cuál resuena — no con lo que "deberías" ser, sino con lo que ya eres sin darte cuenta.</p>"""
                ),
            },
            {
                "name": "Mascara - Email 3 - Conexión",
                "slug": "mascara-3",
                "subject": "Lo que me enseñó mi propia máscara",
                "html_content": _email(
                    _greeting() +
                    """<p>Durante años pensé que mi dificultad para conectarme con la gente era timidez.</p>
<p>Era mi máscara.</p>
<p>La construí de niño, en un contexto donde mostrarme tal cual era peligroso. Funcionó tan bien que a los 30 años todavía la usaba — y ya no había ningún peligro real.</p>
<p>No fue un momento de iluminación. Fue un proceso. Pero el primer paso fue verla.</p>
<p>Si estás leyendo esto, ya diste ese paso.</p>"""
                ),
            },
            {
                "name": "Mascara - Email 4 - Invitación app",
                "slug": "mascara-4",
                "subject": "Ahora que la viste, ¿quieres ver más?",
                "html_content": _email(
                    _greeting() +
                    """<p>La guía te mostró tu máscara. El siguiente paso es ver qué hay debajo.</p>
<p>En la app tienes herramientas para eso:</p>
<ul>
<li><strong>Tests psicométricos</strong> que miden exactamente esos patrones</li>
<li><strong>El Espejo de Conflictos</strong>: una IA que te devuelve preguntas, no respuestas</li>
<li><strong>Tu Mapa Interior</strong>: un registro de tu viaje que se construye con cada exploración</li>
</ul>
<p>Cuenta gratuita. Sin tarjeta. Empiezas en 2 minutos.</p>""" +
                    _APP_CTA
                ),
            },
        ]

        # ── HACKS ────────────────────────────────────────────────────────────
        hacks_templates = [
            {
                "name": "Hacks - Email 1 - Entrega",
                "slug": "hacks-1",
                "subject": "Tu guía de 3 Hacks está aquí",
                "html_content": _email(
                    _greeting() +
                    """<p>Te enviamos la guía <strong>"3 Hacks de Endonáutica para tu Viaje Interior"</strong>.</p>
<p>Una sugerencia: no la leas de corrido. Lee un hack, cierra el documento, vuelve al día siguiente con el siguiente. Los tres juntos en una hora no te van a cambiar nada. Uno bien digerido, sí puede.</p>""" +
                    _SPAM_NOTE +
                    """<p style="margin-top:20px;">En el próximo email te cuento el error que comete casi todo el mundo cuando intenta conocerse a sí mismo.</p>"""
                ),
            },
            {
                "name": "Hacks - Email 2 - El error más común",
                "slug": "hacks-2",
                "subject": "El error que comete el 90% de la gente que quiere conocerse",
                "html_content": _email(
                    _greeting() +
                    """<p>El error es este: buscar el patrón afuera antes de verlo adentro.</p>
<p>La mayoría lee sobre arquetipos, sombras, heridas de infancia — y los aplica a los demás. "Mi jefe tiene la herida del abandono." "Mi pareja actúa desde su máscara." Todo eso puede ser cierto. El problema es que mientras señalas afuera, el tuyo opera sin que lo veas.</p>
<p>El Hack 1 de la guía va exactamente a eso: cómo leer tu propio origen antes de leer el de nadie más.</p>
<p>Si ya lo leíste, bien. Si no, hoy es buen día para empezar.</p>"""
                ),
            },
            {
                "name": "Hacks - Email 3 - Invitación app",
                "slug": "hacks-3",
                "subject": "¿Qué sigue después de los 3 hacks?",
                "html_content": _email(
                    _greeting() +
                    """<p>Los hacks son un mapa de lectura. La app es el territorio.</p>
<p>En la app puedes hacer los tests que miden los patrones que describe la guía, conversar con el Espejo de Conflictos cuando algo se repite en tu vida y no entiendes por qué, y construir tu Mapa Interior — un registro vivo de lo que vas descubriendo.</p>
<p>Es gratuita. Sin tarjeta. Sin compromisos.</p>""" +
                    _APP_CTA
                ),
            },
        ]

        # ── VIAJE ────────────────────────────────────────────────────────────
        viaje_templates = [
            {
                "name": "Viaje - Email 1 - Entrega",
                "slug": "viaje-1",
                "subject": "Tu guía del viaje interior está aquí",
                "html_content": _email(
                    _greeting() +
                    """<p>Te enviamos la guía <strong>"Paso a Paso para Iniciar el Viaje Interior"</strong>.</p>
<p>La guía tiene 8 páginas. Está pensada para leerse con calma — no para terminarla, sino para empezarla. El viaje no tiene deadline, pero hay algo que pasa cuando decides que hoy es el día.</p>""" +
                    _SPAM_NOTE +
                    """<p style="margin-top:20px;">En el siguiente email te cuento por qué la mayoría de las personas que quieren conocerse terminan dando vueltas en círculo.</p>"""
                ),
            },
            {
                "name": "Viaje - Email 2 - Por qué la gente da vueltas",
                "slug": "viaje-2",
                "subject": "Por qué das vueltas (y cómo dejar de hacerlo)",
                "html_content": _email(
                    _greeting() +
                    """<p>La razón por la que la mayoría da vueltas es simple: buscan comprensión antes de buscar contacto.</p>
<p>Leen, estudian, acumulan conceptos. "Sé que tengo la herida del rechazo." "Entiendo que actúo desde el miedo." Pero entender no mueve nada. Lo que mueve es el contacto directo con lo que está pasando — sin intermediarios teóricos.</p>
<p>La guía tiene un ejercicio en la página 5 que es exactamente eso: contacto, no análisis. Si no llegaste ahí, vale la pena volver.</p>"""
                ),
            },
            {
                "name": "Viaje - Email 3 - Invitación app",
                "slug": "viaje-3",
                "subject": "El siguiente paso después de la guía",
                "html_content": _email(
                    _greeting() +
                    """<p>La guía te da el mapa. La app te da el espacio para caminar.</p>
<p>Tests que revelan los patrones que la guía describe. El Espejo de Conflictos: una IA que no te da respuestas — te hace las preguntas que nadie más te hace. Tu Mapa Interior, que se construye con cada exploración.</p>
<p>Gratuita. Sin tarjeta. Dos minutos para empezar.</p>""" +
                    _APP_CTA
                ),
            },
        ]

        all_templates = mascara_templates + hacks_templates + viaje_templates

        templates_by_slug = {}
        for tmpl_data in all_templates:
            tmpl, created = EmailTemplate.objects.get_or_create(
                slug=tmpl_data["slug"],
                defaults=tmpl_data
            )
            if not created:
                # Actualizar html_content si el template ya existe
                tmpl.html_content = tmpl_data["html_content"]
                tmpl.subject = tmpl_data["subject"]
                tmpl.save(update_fields=["html_content", "subject"])
            templates_by_slug[tmpl_data["slug"]] = tmpl
            self.stdout.write(f"  {'Creada' if created else 'Actualizada'}: {tmpl.name}")

        self.stdout.write("\nCreando secuencias...")

        sequences_config = [
            {
                "name": "Secuencia Mascara",
                "list_slug": "mascara",
                "steps": [
                    (1, 0, "mascara-1"),
                    (2, 2, "mascara-2"),
                    (3, 4, "mascara-3"),
                    (4, 6, "mascara-4"),
                ],
            },
            {
                "name": "Secuencia Hacks",
                "list_slug": "hacks",
                "steps": [
                    (1, 0, "hacks-1"),
                    (2, 3, "hacks-2"),
                    (3, 6, "hacks-3"),
                ],
            },
            {
                "name": "Secuencia Viaje",
                "list_slug": "viaje",
                "steps": [
                    (1, 0, "viaje-1"),
                    (2, 3, "viaje-2"),
                    (3, 6, "viaje-3"),
                ],
            },
        ]

        for seq_config in sequences_config:
            seq, created = EmailSequence.objects.get_or_create(
                name=seq_config["name"],
                email_list=email_lists[seq_config["list_slug"]],
                defaults={"is_active": True},
            )
            self.stdout.write(f"  {'Creada' if created else 'Existe'}: {seq.name}")

            for step_num, delay, tmpl_slug in seq_config["steps"]:
                step, step_created = SequenceStep.objects.get_or_create(
                    sequence=seq,
                    step_number=step_num,
                    defaults={
                        "template": templates_by_slug[tmpl_slug],
                        "delay_days": delay,
                    },
                )
                self.stdout.write(f"    Paso {step_num} (día {delay}): {'Creado' if step_created else 'Existe'}")

        self.stdout.write(self.style.SUCCESS("\n✅ Flywheel de emails configurado"))
        self.stdout.write(f"  Listas: {', '.join(email_lists.keys())}")
        self.stdout.write(f"  Secuencias: {len(sequences_config)} — {sum(len(s['steps']) for s in sequences_config)} pasos en total")
