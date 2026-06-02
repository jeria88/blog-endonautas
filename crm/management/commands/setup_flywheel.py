from django.core.management.base import BaseCommand
from crm.models import EmailList, EmailTemplate, EmailSequence, SequenceStep


class Command(BaseCommand):
    help = "Crea las listas, plantillas y secuencias de email iniciales para el flywheel"

    def handle(self, *args, **options):
        self.stdout.write("Creando listas de email...")

        # Crear listas
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

        # Plantillas para la secuencia Mascara
        mascara_templates = [
            {
                "name": "Mascara - Email 1 - Entrega",
                "slug": "mascara-1",
                "subject": "Tu guía está acá (y una cosa que noté)",
                "html": """<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#1A1916;">
<div style="padding:2rem;">
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>

<p>Te enviamos la guía <strong>"Descubre tu Máscara según tu Herida de Infancia"</strong>.</p>

<p>Algo que noté: la mayoría de las personas que llegan a esta guía llevan años sabiendo que algo se repite en sus vidas. No saben exactamente qué, pero lo sienten.</p>

<p>Esta guía no va a resolver tu vida. Pero va va a hacer algo más útil: va a ponerle nombre a lo que ya sabes.</p>

<p style="color:#9C9589;font-size:0.85rem;margin-top:1.5rem;">⚠️ Si este correo llegó a spam, marcá "no spam" para recibir los siguientes.</p>

<p>En el siguiente email te cuento algo sobre por qué la máscara se construye — y por qué no es tu enemiga.</p>

<p style="margin-top:2rem;">— Franco</p>
</div>
</div>""",
            },
            {
                "name": "Mascara - Email 2 - Profundización",
                "slug": "mascara-2",
                "subject": "Tu máscara no es tu enemiga",
                "html": """<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#1A1916;">
<div style="padding:2rem;">
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>

<p>La máscara tiene mala fama. Suena a algo malo, algo que hay que quitarse.</p>

<p>Pero pensalo así: eras un niño. No tenías las herramientas que tenés ahora. Y ante algo que no podías procesar, construiste una forma de sobrevivir.</p>

<p>Esa forma funcionó. El problema es que sigue funcionando décadas después, en situaciones que ya no lo necesitan.</p>

<p>No se trata de destruir la máscara. Se trata de verla. Porque lo que no ves, decide por ti.</p>

<p>En la guía vas a encontrar los 5 tipos. Fijate cuál resuena — no con lo que "deberías" ser, sino con lo que ya sos sin darte cuenta.</p>

<p style="margin-top:2rem;">— Franco</p>
</div>
</div>""",
            },
            {
                "name": "Mascara - Email 3 - Conexión",
                "slug": "mascara-3",
                "subject": "Lo que me enseñó mi propia máscara",
                "html": """<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#1A1916;">
<div style="padding:2rem;">
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>

<p>Durante años pensé que mi dificultad para conectarme con la gente era timidez.</p>

<p>Era mi máscara.</p>

<p>La construí cuando era chico, en un contexto donde mostrarme tal cual era peligroso. Funcionó tan bien que a los 30 años todavía la usaba — y ya no había ningún peligro real.</p>

<p>No fue un momento de iluminación. Fue un proceso. Pero el primer paso fue verla.</p>

<p>Si estás leyendo esto, ya diste ese paso.</p>

<p style="margin-top:2rem;">— Franco</p>
</div>
</div>""",
            },
            {
                "name": "Mascara - Email 4 - Invitación app",
                "slug": "mascara-4",
                "subject": "Ahora que la viste, ¿querés ver más?",
                "html": """<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#1A1916;">
<div style="padding:2rem;">
<p style="color:#9C9589;font-size:0.85rem;margin-bottom:1.5rem;">Hola {{ nombre }},</p>

<p>La guía te mostró tu máscara. El siguiente paso es ver qué hay debajo.</p>

<p>En la app tenés herramientas para eso:</p>

<ul>
<li><strong>Tests psicométricos</strong> que miden exactamente esos patrones</li>
<li><strong>El Espejo de Conflictos</strong>: una IA que te devuelve preguntas (no respuestas)</li>
<li><strong>Tu Mapa Interior</strong>: un registro de tu viaje que se arma solo, con cada test y cada sesión con el Espejo</li>
</ul>

<p>Cuenta gratuita. Sin tarjeta. Arrancás en 2 minutos.</p>

<p style="text-align:center;margin-top:2rem;">
<a href="https://app.endonautas.cl/accounts/registro/" style="background:#C4813A;color:#fff;padding:0.9rem 2rem;border-radius:999px;text-decoration:none;font-weight:600;font-size:0.9rem;">Crear mi cuenta gratuita →</a>
</p>

<p style="margin-top:2rem;">— Franco</p>
</div>
</div>""",
            },
        ]

        # Crear todas las plantillas
        all_templates = mascara_templates  # Por ahora solo Mascara, después agregamos Hacks y Viaje

        templates_by_slug = {}
        for tmpl_data in all_templates:
            tmpl, created = EmailTemplate.objects.get_or_create(
                slug=tmpl_data["slug"],
                defaults=tmpl_data
            )
            templates_by_slug[tmpl_data["slug"]] = tmpl
            self.stdout.write(f"  {'Creada' if created else 'Existe'}: {tmpl.name}")

        self.stdout.write("\nCreando secuencias...")

        # Crear secuencia Mascara
        seq, created = EmailSequence.objects.get_or_create(
            name="Secuencia Mascara",
            email_list=email_lists["mascara"],
            defaults={"is_active": True}
        )
        self.stdout.write(f"  {'Creada' if created else 'Existe'}: {seq.name}")

        # Crear pasos de la secuencia
        steps_data = [
            (1, 0, "mascara-1"),   # Email 1, día 0 (inmediato)
            (2, 2, "mascara-2"),   # Email 2, día 2
            (3, 4, "mascara-3"),   # Email 3, día 4
            (4, 6, "mascara-4"),   # Email 4, día 6
        ]

        for step_num, delay, tmpl_slug in steps_data:
            step, created = SequenceStep.objects.get_or_create(
                sequence=seq,
                step_number=step_num,
                defaults={
                    "template": templates_by_slug[tmpl_slug],
                    "delay_days": delay,
                }
            )
            self.stdout.write(f"    Paso {step_num} (día {delay}): {'Creado' if created else 'Existe'}")

        self.stdout.write(self.style.SUCCESS("\n✅ Flywheel de emails configurado"))
        self.stdout.write(f"  Lista Mascara: {email_lists['mascara'].subscribers.count()} suscriptores")
        self.stdout.write(f"  Secuencia: {seq.steps.count()} emails programados")
