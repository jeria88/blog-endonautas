from django.core.management.base import BaseCommand
from crm.models import EmailList, EmailTemplate, EmailSequence, SequenceStep

_EMAIL_WRAP_OPEN = '<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#1A1916;"><div style="padding:2rem;">'
_EMAIL_WRAP_CLOSE = "</div></div>"
_SPAM_NOTE = '<p style="color:#9C9589;font-size:0.85rem;margin-top:1.5rem;">⚠️ Si este correo llegó a spam, marca "no spam" para recibir los siguientes.</p>'
_FIRMA = '<p style="margin-top:2rem;">— Franco</p>'
_APP_CTA = """<p style="text-align:center;margin-top:2rem;">
<a href="https://app.endonautas.cl/accounts/registro/" style="background:#C4813A;color:#fff;padding:0.9rem 2rem;border-radius:999px;text-decoration:none;font-weight:600;font-size:0.9rem;">Crear mi cuenta gratuita →</a>
</p>"""


def _email(body: str) -> str:
    return _EMAIL_WRAP_OPEN + body + _FIRMA + _EMAIL_WRAP_CLOSE


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

        # ── MASCARA ─────────────────────────────────────────────────────────
        mascara_templates = [
            {
                "name": "Mascara - Email 1 - Entrega",
                "slug": "mascara-1",
                "subject": "Tu guía está aquí (y una cosa que noté)",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>Te enviamos la guía <strong>"Descubre tu Máscara según tu Herida de Infancia"</strong>.</p>
<p>Algo que noté: la mayoría de las personas que llegan a esta guía llevan años sabiendo que algo se repite en sus vidas. No saben exactamente qué, pero lo sienten.</p>
<p>Esta guía no va a resolver tu vida. Pero va a hacer algo más útil: va a ponerle nombre a lo que ya sabes.</p>
""" + _SPAM_NOTE + """
<p>En el siguiente email te cuento algo sobre por qué la máscara se construye — y por qué no es tu enemiga.</p>
"""),
            },
            {
                "name": "Mascara - Email 2 - Profundización",
                "slug": "mascara-2",
                "subject": "Tu máscara no es tu enemiga",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>La máscara tiene mala fama. Suena a algo malo, algo que hay que quitarse.</p>
<p>Pero piénsalo así: eras un niño. No tenías las herramientas que tienes ahora. Y ante algo que no podías procesar, construiste una forma de sobrevivir.</p>
<p>Esa forma funcionó. El problema es que sigue funcionando décadas después, en situaciones que ya no lo necesitan.</p>
<p>No se trata de destruir la máscara. Se trata de verla. Porque lo que no ves, decide por ti.</p>
<p>En la guía vas a encontrar los 5 tipos. Fíjate cuál resuena — no con lo que "deberías" ser, sino con lo que ya eres sin darte cuenta.</p>
"""),
            },
            {
                "name": "Mascara - Email 3 - Conexión",
                "slug": "mascara-3",
                "subject": "Lo que me enseñó mi propia máscara",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>Durante años pensé que mi dificultad para conectarme con la gente era timidez.</p>
<p>Era mi máscara.</p>
<p>La construí de niño, en un contexto donde mostrarme tal cual era peligroso. Funcionó tan bien que a los 30 años todavía la usaba — y ya no había ningún peligro real.</p>
<p>No fue un momento de iluminación. Fue un proceso. Pero el primer paso fue verla.</p>
<p>Si estás leyendo esto, ya diste ese paso.</p>
"""),
            },
            {
                "name": "Mascara - Email 4 - Invitación app",
                "slug": "mascara-4",
                "subject": "Ahora que la viste, ¿quieres ver más?",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>La guía te mostró tu máscara. El siguiente paso es ver qué hay debajo.</p>
<p>En la app tienes herramientas para eso:</p>
<ul>
<li><strong>Tests psicométricos</strong> que miden exactamente esos patrones</li>
<li><strong>El Espejo de Conflictos</strong>: una IA que te devuelve preguntas (no respuestas)</li>
<li><strong>Tu Mapa Interior</strong>: un registro de tu viaje que se construye solo, con cada test y cada sesión con el Espejo</li>
</ul>
<p>Cuenta gratuita. Sin tarjeta. Empiezas en 2 minutos.</p>
""" + _APP_CTA),
            },
        ]

        # ── HACKS ────────────────────────────────────────────────────────────
        hacks_templates = [
            {
                "name": "Hacks - Email 1 - Entrega",
                "slug": "hacks-1",
                "subject": "Tu guía de 3 Hacks está aquí",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>Te enviamos la guía <strong>"3 Hacks de Endonáutica para tu Viaje Interior"</strong>.</p>
<p>Una sugerencia: no la leas de corrido. Lee un hack, cierra el documento, vuelve al día siguiente con el siguiente. Los tres juntos en una hora no te van a cambiar nada. Uno bien digerido, sí puede.</p>
""" + _SPAM_NOTE + """
<p>En el próximo email te cuento el error que comete casi todo el mundo cuando intenta conocerse a sí mismo.</p>
"""),
            },
            {
                "name": "Hacks - Email 2 - El error más común",
                "slug": "hacks-2",
                "subject": "El error que comete el 90% de la gente que quiere conocerse",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>El error es este: buscar el patrón afuera antes de verlo adentro.</p>
<p>La mayoría lee sobre arquetipos, sombras, heridas de infancia — y los aplica a los demás. "Mi jefe tiene la herida del abandono." "Mi pareja actúa desde su máscara." Todo eso puede ser cierto. El problema es que mientras señalas afuera, el tuyo opera sin que lo veas.</p>
<p>El Hack 1 de la guía va exactamente a eso: cómo leer tu propio origen antes de leer el de nadie más.</p>
<p>Si ya lo leíste, bien. Si no, hoy es buen día para empezar.</p>
"""),
            },
            {
                "name": "Hacks - Email 3 - Invitación app",
                "slug": "hacks-3",
                "subject": "¿Qué sigue después de los 3 hacks?",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>Los hacks son un mapa de lectura. La app es el territorio.</p>
<p>En la app puedes hacer los tests que miden los patrones que describe la guía, conversar con el Espejo de Conflictos cuando algo se repite en tu vida y no entiendes por qué, y construir tu Mapa Interior — un registro vivo de lo que vas descubriendo.</p>
<p>Es gratuita. Sin tarjeta. Sin compromisos.</p>
""" + _APP_CTA),
            },
        ]

        # ── VIAJE ────────────────────────────────────────────────────────────
        viaje_templates = [
            {
                "name": "Viaje - Email 1 - Entrega",
                "slug": "viaje-1",
                "subject": "Tu guía del viaje interior está aquí",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>Te enviamos la guía <strong>"Paso a Paso para Iniciar el Viaje Interior"</strong>.</p>
<p>La guía tiene 8 páginas. Está pensada para leerse con calma — no para terminarla, sino para empezarla. El viaje no tiene deadline, pero hay algo que pasa cuando decides que hoy es el día.</p>
""" + _SPAM_NOTE + """
<p>En el siguiente email te cuento por qué la mayoría de las personas que quieren conocerse terminan dando vueltas en círculo.</p>
"""),
            },
            {
                "name": "Viaje - Email 2 - Por qué la gente da vueltas",
                "slug": "viaje-2",
                "subject": "Por qué das vueltas (y cómo dejar de hacerlo)",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>La razón por la que la mayoría da vueltas es simple: buscan comprensión antes de buscar contacto.</p>
<p>Leen, estudian, acumulan conceptos. "Sé que tengo la herida del rechazo." "Entiendo que actúo desde el miedo." Pero entender no mueve nada. Lo que mueve es el contacto directo con lo que está pasando — sin intermediarios teóricos.</p>
<p>La guía tiene un ejercicio en la página 5 que es exactamente eso: contacto, no análisis. Si no llegaste ahí, vale la pena volver.</p>
"""),
            },
            {
                "name": "Viaje - Email 3 - Invitación app",
                "slug": "viaje-3",
                "subject": "El siguiente paso después de la guía",
                "html_content": _email("""
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>
<p>La guía te da el mapa. La app te da el espacio para caminar.</p>
<p>Tests que revelan los patrones que la guía describe. El Espejo de Conflictos: una IA que no te da respuestas — te hace las preguntas que nadie más te hace. Tu Mapa Interior, que se construye con cada exploración.</p>
<p>Gratuita. Sin tarjeta. Dos minutos para empezar.</p>
""" + _APP_CTA),
            },
        ]

        all_templates = mascara_templates + hacks_templates + viaje_templates

        templates_by_slug = {}
        for tmpl_data in all_templates:
            tmpl, created = EmailTemplate.objects.get_or_create(
                slug=tmpl_data["slug"],
                defaults=tmpl_data
            )
            templates_by_slug[tmpl_data["slug"]] = tmpl
            self.stdout.write(f"  {'Creada' if created else 'Existe'}: {tmpl.name}")

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

        self.stdout.write("\nRegistrando cron jobs vía Railway (ver instrucciones al final)...")

        self.stdout.write(self.style.SUCCESS("\n✅ Flywheel de emails configurado"))
        self.stdout.write(f"  Listas: {', '.join(email_lists.keys())}")
        self.stdout.write(f"  Secuencias: {len(sequences_config)} — {sum(len(s['steps']) for s in sequences_config)} pasos en total")
        self.stdout.write("\n  Cron Jobs Railway requeridos:")
        self.stdout.write("    - python manage.py run_flywheel (cada hora: 0 * * * *)")
        self.stdout.write("    - python manage.py send_queued_mail (cada 5 min: */5 * * * *)")
