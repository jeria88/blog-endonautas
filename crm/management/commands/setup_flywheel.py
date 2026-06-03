from django.core.management.base import BaseCommand
from crm.models import EmailList, EmailTemplate, EmailSequence, SequenceStep

# ── Constantes de diseño ────────────────────────────────────────────────────

LOGO = (
    '<div style="border-radius:50%;width:80px;height:80px;overflow:hidden;display:inline-block;'
    'background-color:#161513;border:2px solid rgba(232,228,220,0.06);">'
    '<img src="https://endonautas.cl/static/img/logo.ffc70eb7b9d7.png" '
    'alt="Endonautas" width="80" height="80" '
    'style="display:block;border:0;outline:none;border-radius:50%;width:80px;height:80px;'
    'object-fit:cover;" />'
    '</div>'
)

_EMAIL_OPEN = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">
{{{{ preview }}}}
</div>
<style>
body{{margin:0;padding:0;background-color:#f5f3ef;}}
p{{margin:0 0 16px 0;}}
p:last-of-type{{margin-bottom:0;}}
ul{{margin:0 0 16px 0;padding-left:20px;}}
li{{margin-bottom:8px;}}
strong{{font-weight:700;color:#f0ece4;}}
a{{color:#7ECCCD;}}
</style>
</head>
<body style="margin:0;padding:0;background-color:#f5f3ef;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f4f4f0">
<tr><td align="center" style="padding:32px 16px 40px 16px;">

<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">
<tr><td align="center" style="padding:0 0 24px 0;">
{LOGO}
</td></tr>
</table>

<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#161513;border-radius:12px;overflow:hidden;">

<tr><td style="padding:0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:#7ECCCD;height:3px;font-size:0;line-height:0;">&nbsp;</td></tr></table></td></tr>

<tr><td style="padding:36px 44px 24px 44px;font-family:Georgia,'Times New Roman',serif;font-size:17px;font-weight:400;line-height:1.75;color:#f0ece4;">
"""

_FIRMA = """
</td></tr>
<tr><td style="padding:0 44px 36px 44px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="border-top:1px solid rgba(240,232,220,0.06);padding-top:24px;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="padding-right:14px;width:48px;">
<img src="https://endonautas.cl/static/img/franco-jeria.29d377e25215.jpeg" alt="Franco" width="48" height="48" style="display:block;border-radius:24px;border:2px solid rgba(126,204,205,0.25);width:48px;height:48px;object-fit:cover;" />
</td>
<td>
<p style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:16px;font-weight:600;color:#f0ece4;">Franco Jeria Castro</p>
<p style="margin:2px 0 0 0;font-family:Arial,sans-serif;font-size:12px;color:rgba(240,236,228,0.4);">Fundador de Endonautas</p>
</td>
</tr>
</table>
</td></tr>
</table>
</td></tr>
"""

_FOOTER = """
<tr><td style="padding:20px 44px 24px 44px;background-color:#161513;border-top:1px solid rgba(240,236,228,0.06);">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="font-family:Arial,sans-serif;font-size:11px;line-height:1.7;color:rgba(240,236,228,0.25);">
<p style="margin:0 0 4px 0;">
<a href="https://endonautas.cl" style="color:rgba(232,228,220,0.25);text-decoration:none;">endonautas.cl</a>
<span style="margin:0 6px;">&#183;</span>
<a href="https://endonautas.cl/contacto/" style="color:rgba(232,228,220,0.25);text-decoration:none;">Contacto</a>
<span style="margin:0 6px;">&#183;</span>
<a href="{{ unsubscribe }}" style="color:rgba(232,228,220,0.25);text-decoration:none;">Cancelar suscripci&oacute;n</a>
</p>
<p style="margin:0;">Recibiste esto porque te suscribiste en endonautas.cl.</p>
</td></tr>
</table>
</td></tr>
</table>

</td></tr>
</table>

</body>
</html>"""

_EMAIL_CLOSE = _FOOTER


def _email(body: str, preview: str = "") -> str:
    """Envuelve el cuerpo del email en la estructura completa."""
    html = _EMAIL_OPEN.replace("{{ preview }}", preview)
    return html + body + _FIRMA + _EMAIL_CLOSE


def _greeting() -> str:
    return '<p style="margin:0 0 24px 0;font-size:16px;color:rgba(240,236,228,0.55);">Hola {{ nombre }},</p>'


def _title(text: str) -> str:
    return f'<p style="font-size:18px;font-weight:600;color:#f0ece4;margin-bottom:24px;">{text}</p>'


def _quote(text: str) -> str:
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">'
        '<tr><td style="padding:20px 24px;background-color:rgba(126,204,205,0.04);'
        'border-left:2px solid rgba(126,204,205,0.25);border-radius:6px;">'
        f'<p style="margin:0;font-family:\'Plus Jakarta Sans\',Georgia,serif;font-size:15px;'
        f'color:rgba(232,228,220,0.55);font-style:italic;line-height:1.7;">"{text}"</p>'
        '</td></tr>'
        '</table>'
    )


def _spam_note() -> str:
    return (
        '<p style="margin-top:24px;font-size:13px;color:rgba(232,228,220,0.3);">'
        'Si este correo llegó a spam, márcalo como "no es spam" para recibir los siguientes.</p>'
    )


def _app_cta(text: str = "Comenzar exploración gratuita →") -> str:
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">'
        '<tr><td align="center">'
        '<a href="https://app.endonautas.cl/accounts/registro/" '
        'style="display:inline-block;background-color:#F0E8DC;color:#000000;padding:14px 36px;'
        'border-radius:999px;font-family:\'Space Grotesk\',Arial,sans-serif;font-size:13px;'
        'font-weight:600;letter-spacing:0.3px;text-decoration:none;">'
        f'{text}</a>'
        '<p style="margin:10px 0 0 0;font-size:12px;color:rgba(232,228,220,0.25);'
        '">Sin tarjeta · 2 minutos · Sin compromiso</p>'
        '</td></tr>'
        '</table>'
    )


def _download_btn(url: str, text: str = "Descargar guía gratuita →") -> str:
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">'
        '<tr><td align="center">'
        f'<a href="{url}" '
        'style="display:inline-block;background-color:#F0E8DC;color:#000000;padding:14px 36px;'
        'border-radius:999px;font-family:\'Space Grotesk\',Arial,sans-serif;font-size:14px;'
        'font-weight:600;letter-spacing:0.3px;text-decoration:none;">'
        f'{text}</a>'
        '<p style="margin:10px 0 0 0;font-size:12px;color:rgba(232,228,220,0.25);'
        '">PDF · Sin registro · Descarga inmediata</p>'
        '</td></tr>'
        '</table>'
    )


# ── Templates de cada secuencia ─────────────────────────────────────────────

MASCARA_TEMPLATES = [
    {
        "name": "Mascara - Email 1 - Entrega",
        "slug": "mascara-1",
        "subject": "Tu guía está aquí (y una cosa que noté)",
        "html_content": _email(
            _greeting()
            + _title("Tu guía está aquí")
            + """<p>Te enviamos la guía de <strong>"Descubre tu Máscara según tu Herida de Infancia"</strong>.</p>
<p>Algo que noté: la mayoría de las personas que llegan a esta guía llevan años sabiendo que algo se repite en sus vidas. No saben exactamente qué, pero lo sienten.</p>
<p>Esta guía no va a resolver tu vida. Pero va a hacer algo más útil: va a ponerle nombre a lo que ya sabes.</p>"""
            + _download_btn("https://endonautas.cl/static/pdfs/descubre-tu-mascara.pdf", "Descargar guía de la Máscara →")
            + _quote("La máscara no se lleva para ocultar quienes somos. Se lleva para sobrevivir hasta que estemos listos para mirar.")
            + _spam_note()
            + '<p style="margin-top:24px;">En el próximo email te cuento algo sobre por qué la máscara se construye — y por qué no es tu enemiga.</p>',
            preview="Tu guía para descubrir la máscara que construiste para sobrevivir — y por qué hoy puedes mirarla de frente."
        ),
    },
    {
        "name": "Mascara - Email 2 - Profundización",
        "slug": "mascara-2",
        "subject": "Tu máscara no es tu enemiga",
        "html_content": _email(
            _greeting()
            + _title("Tu máscara no es tu enemiga")
            + """<p>La máscara tiene mala fama. Suena a algo malo, algo que hay que quitarse.</p>
<p>Pero piénsalo así: eras un niño. No tenías las herramientas que tienes ahora. Y ante algo que no podías procesar, construiste una forma de sobrevivir.</p>
<p>Esa forma funcionó. El problema es que sigue funcionando décadas después, en situaciones que ya no lo necesitan.</p>
<p>No se trata de destruir la máscara. Se trata de verla. Porque lo que no ves, decide por ti.</p>"""
            + _quote("El problema no es que tengas una máscara. Todos tenemos una. El problema es que no sabes que la tienes puesta.")
            + '<p>En la guía vas a encontrar los 5 tipos. Fíjate cuál resuena — no con lo que "deberías" ser, sino con lo que ya eres sin darte cuenta.</p>'
            + _app_cta("Tu herida no es tu identidad. Es tu origen →"),
            preview="Tu máscara no es tu enemiga. Es una herramienta que ya no necesitas usar todo el tiempo."
        ),
    },
    {
        "name": "Mascara - Email 3 - Conexión",
        "slug": "mascara-3",
        "subject": "Lo que me enseñó mi propia máscara",
        "html_content": _email(
            _greeting()
            + _title("Lo que me enseñó mi propia máscara")
            + """<p>Durante años pensé que mi dificultad para conectarme con la gente era timidez.</p>
<p>Era mi máscara.</p>
<p>La construí de niño, en un contexto donde mostrarme tal cual era peligroso. Funcionó tan bien que a los 30 años todavía la usaba — y ya no había ningún peligro real.</p>
<p>No fue un momento de iluminación. Fue un proceso. Pero el primer paso fue verla.</p>
<p>Si estás leyendo esto, ya diste ese paso.</p>"""
            + _quote("No vemos las cosas como son. Las vemos como somos. La máscara no es una excepción.")
            + _app_cta("No te da respuestas. Te hace las preguntas que importan →"),
            preview="Lo que aprendí al verme la mía — y cómo ese primer paso cambió todo."
        ),
    },
    {
        "name": "Mascara - Email 4 - Invitación app",
        "slug": "mascara-4",
        "subject": "Ahora que la viste, ¿quieres ver más?",
        "html_content": _email(
            _greeting()
            + _title("¿Qué hay debajo de tu máscara?")
            + """<p>La guía te mostró qué máscara usas. El siguiente paso es ver qué hay debajo.</p>
<p>En la app de Endonautas tienes herramientas para eso:</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0;">
<tr><td style="padding-bottom:16px;vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">01</td>
<td style="padding-bottom:16px;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>Tests psicométricos</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Miden exactamente esos patrones que reconociste en la guía.</span></td></tr>
<tr><td style="padding-bottom:16px;vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">02</td>
<td style="padding-bottom:16px;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>El Espejo de Conflictos</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Una IA que no te da respuestas — te hace las preguntas que importan.</span></td></tr>
<tr><td style="vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">03</td>
<td style="font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>Tu Mapa Interior</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Un registro de tu viaje que se construye con cada exploración.</span></td></tr>
</table>"""
            + _app_cta(),
            preview="La guía te mostró la máscara. En la app hay tests, un espejo IA y un mapa que se construye solo."
        ),
    },
]

HACKS_TEMPLATES = [
    {
        "name": "Hacks - Email 1 - Entrega",
        "slug": "hacks-1",
        "subject": "Tu guía de 3 Hacks está aquí",
        "html_content": _email(
            _greeting()
            + _title("Tu guía de 3 Hacks está aquí")
            + """<p>Te enviamos la guía <strong>"3 Hacks de Endonáutica para tu Viaje Interior"</strong>.</p>
<p>Una sugerencia: no la leas de corrido. Lee un hack, cierra el documento, vuelve al día siguiente con el siguiente. Los tres juntos en una hora no te van a cambiar nada. Uno bien digerido, sí puede.</p>"""
            + _download_btn("https://endonautas.cl/static/pdfs/3-hacks-endonautica.pdf", "Descargar guía de los 3 Hacks →")
            + _quote("Un hack no es un truco. Es un atajo consciente hacia algo que siempre estuvo ahí pero no veías.")
            + _spam_note()
            + '<p style="margin-top:24px;">En el próximo email te cuento el error que comete casi todo el mundo cuando intenta conocerse a sí mismo.</p>',
            preview="Tres hacks de endonáutica. La recomendación: uno a la vez, con calma."
        ),
    },
    {
        "name": "Hacks - Email 2 - El error más común",
        "slug": "hacks-2",
        "subject": "El error que comete el 90% de la gente que quiere conocerse",
        "html_content": _email(
            _greeting()
            + _title("El error que comete el 90% de la gente que quiere conocerse")
            + """<p>El error es este: buscar el patrón afuera antes de verlo adentro.</p>
<p>La mayoría lee sobre arquetipos, sombras, heridas de infancia — y los aplica a los demás. "Mi jefe tiene la herida del abandono." "Mi pareja actúa desde su máscara." Todo eso puede ser cierto. El problema es que mientras señalas afuera, el tuyo opera sin que lo veas.</p>
<p>El Hack 1 de la guía va exactamente a eso: cómo leer tu propio origen antes de leer el de nadie más.</p>
<p>Si ya lo leíste, bien. Si no, hoy es buen día para empezar.</p>"""
            + _quote("Señalar afuera es cómodo. Mirarse adentro es incómodo. Pero lo incómodo es lo que transforma.")
            + _app_cta("Lo que no quieres ver de ti también es parte del mapa →"),
            preview="El error más común cuando empezamos a explorarnos: aplicar todo a los demás antes de mirarnos a nosotros."
        ),
    },
    {
        "name": "Hacks - Email 3 - Invitación app",
        "slug": "hacks-3",
        "subject": "¿Qué sigue después de los 3 hacks?",
        "html_content": _email(
            _greeting()
            + _title("¿Qué sigue después de los 3 hacks?")
            + """<p>Los hacks son un mapa de lectura. La app es el territorio.</p>
<p>En la app puedes hacer los tests que miden los patrones que describe la guía, conversar con el Espejo de Conflictos cuando algo se repite en tu vida y no entiendes por qué, y construir tu Mapa Interior — un registro vivo de lo que vas descubriendo.</p>
<p>Es gratuita. Sin tarjeta. Sin compromisos.</p>"""
            + _app_cta("Un hack no es un truco. Es un atajo consciente →"),
            preview="Los hacks son el mapa. La app es el territorio donde aplicarlos."
        ),
    },
]

VIAJE_TEMPLATES = [
    {
        "name": "Viaje - Email 1 - Entrega",
        "slug": "viaje-1",
        "subject": "Tu guía del viaje interior está aquí",
        "html_content": _email(
            _greeting()
            + _title("Tu guía del viaje interior está aquí")
            + """<p>Te enviamos la guía <strong>"Paso a Paso para Iniciar el Viaje Interior"</strong>.</p>
<p>La guía tiene 8 páginas. Está pensada para leerse con calma — no para terminarla, sino para empezarla. El viaje no tiene deadline, pero hay algo que pasa cuando decides que hoy es el día.</p>"""
            + _download_btn("https://endonautas.cl/static/pdfs/guia-viaje-interior.pdf", "Descargar guía del Viaje Interior →")
            + _quote("El viaje interior no es un destino. Es una dirección. Y la dirección importa más que la velocidad.")
            + _spam_note()
            + '<p style="margin-top:24px;">En el siguiente email te cuento por qué la mayoría de las personas que quieren conocerse terminan dando vueltas en círculo.</p>',
            preview="La guía paso a paso para el viaje interior. Ocho páginas para leer sin apuro."
        ),
    },
    {
        "name": "Viaje - Email 2 - Por qué la gente da vueltas",
        "slug": "viaje-2",
        "subject": "Por qué das vueltas (y cómo dejar de hacerlo)",
        "html_content": _email(
            _greeting()
            + _title("Por qué das vueltas (y cómo dejar de hacerlo)")
            + """<p>La razón por la que la mayoría da vueltas es simple: buscan comprensión antes de buscar contacto.</p>
<p>Leen, estudian, acumulan conceptos. "Sé que tengo la herida del rechazo." "Entiendo que actúo desde el miedo." Pero entender no mueve nada. Lo que mueve es el contacto directo con lo que está pasando — sin intermediarios teóricos.</p>
<p>La guía tiene un ejercicio en la página 5 que es exactamente eso: contacto, no análisis. Si no llegaste ahí, vale la pena volver.</p>"""
            + _quote("Entender es cómodo. Sentir es donde ocurre el cambio. No confundas una con la otra.")
            + _app_cta("No te da respuestas. Te hace las preguntas que importan →"),
            preview="El motivo real por el que muchos se quedan en el mismo lugar — y cómo salir de ahí."
        ),
    },
    {
        "name": "Viaje - Email 3 - Invitación app",
        "slug": "viaje-3",
        "subject": "El siguiente paso después de la guía",
        "html_content": _email(
            _greeting()
            + _title("El siguiente paso después de la guía")
            + """<p>La guía te da el mapa. La app te da el espacio para caminar.</p>
<p>Tests que revelan los patrones que la guía describe. El Espejo de Conflictos: una IA que no te da respuestas — te hace las preguntas que nadie más te hace. Tu Mapa Interior, que se construye con cada exploración.</p>
<p>Gratuita. Sin tarjeta. Dos minutos para empezar.</p>"""
            + _app_cta("El viaje interior no es un destino. Es una dirección →"),
            preview="La guía te da el mapa. La app te da el espacio para caminar."
        ),
    },
]


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

        all_templates = MASCARA_TEMPLATES + HACKS_TEMPLATES + VIAJE_TEMPLATES

        templates_by_slug = {}
        for tmpl_data in all_templates:
            tmpl, created = EmailTemplate.objects.get_or_create(
                slug=tmpl_data["slug"],
                defaults=tmpl_data
            )
            if not created:
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
