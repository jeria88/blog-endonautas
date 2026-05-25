from django.core.management.base import BaseCommand
from django.utils.text import slugify
from psychometrics.models import Test, Question


class Command(BaseCommand):
    help = 'Carga los tests psicométricos con lógica sombra/luz endonauta (idempotente)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Elimina todos los tests existentes y los recrea desde cero.',
        )

    def handle(self, *args, **options):
        if options['force']:
            self.stdout.write('⚠️  --force: eliminando tests y preguntas existentes...')
            Question.objects.all().delete()
            Test.objects.all().delete()
            self.stdout.write('   Limpieza completa.\n')
        self.stdout.write('🌱 Sembrando tests psicométricos...\n')
        self.seed_all()
        self.stdout.write(self.style.SUCCESS('\n✨ Tests listos.'))

    # ─────────────────────────────────────────────
    # HELPER
    # ─────────────────────────────────────────────

    def _seed(self, name, dimension, description, estimated_minutes, questions_data,
              order=0, default_scale='likert5', instrument_type='custom'):
        slug = slugify(name)
        test, created = Test.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'dimension': dimension,
                'description': description,
                'estimated_minutes': estimated_minutes,
                'order': order,
                'active': True,
                'instrument_type': instrument_type,
            }
        )
        if not created:
            self.stdout.write(f'  ⏭  {name} ya existe.')
            return

        for i, q in enumerate(questions_data):
            Question.objects.create(
                test=test,
                text=q['t'],
                dimension_key=q.get('d', ''),
                scale=q.get('scale', default_scale),
                reverse_scored=q.get('r', False),
                order=i,
            )

        self.stdout.write(self.style.SUCCESS(f'  ✅ {name} — {len(questions_data)} preguntas'))

    # ─────────────────────────────────────────────
    # DIMENSIÓN: IDENTIDAD Y PERSONALIDAD
    # ─────────────────────────────────────────────

    def seed_all(self):
        self._seed(
            name='Big Five — Inventario de Personalidad',
            dimension='identidad',
            description='Mide los 5 grandes rasgos de personalidad: Extraversión, Amabilidad, Responsabilidad, Neuroticismo y Apertura. Cada rasgo tiene su polo sombra y su polo luz — ninguno es "bueno" o "malo" en sí mismo.',
            estimated_minutes=8,
            order=1,
            default_scale='likert5a',
            instrument_type='clinical',
            questions_data=[
                {'t': 'Es hablador/a', 'd': 'Extraversión'},
                {'t': 'Tiende a encontrar defectos en los demás', 'd': 'Amabilidad', 'r': True},
                {'t': 'Hace un trabajo minucioso', 'd': 'Responsabilidad'},
                {'t': 'Es deprimido/a, melancólico/a', 'd': 'Neuroticismo'},
                {'t': 'Es original, se le ocurren ideas nuevas', 'd': 'Apertura'},
                {'t': 'Es reservado/a', 'd': 'Extraversión', 'r': True},
                {'t': 'Es servicial y no egoísta con los demás', 'd': 'Amabilidad'},
                {'t': 'Puede ser algo descuidado/a', 'd': 'Responsabilidad', 'r': True},
                {'t': 'Es relajado/a, maneja bien el estrés', 'd': 'Neuroticismo', 'r': True},
                {'t': 'Tiene curiosidad por muchas cosas diferentes', 'd': 'Apertura'},
                {'t': 'Está lleno/a de energía', 'd': 'Extraversión'},
                {'t': 'Inicia peleas con los demás', 'd': 'Amabilidad', 'r': True},
                {'t': 'Es un/a trabajador/a confiable', 'd': 'Responsabilidad'},
                {'t': 'Puede estar tenso/a', 'd': 'Neuroticismo'},
                {'t': 'Es ingenioso/a, un/a pensador/a profundo', 'd': 'Apertura'},
                {'t': 'Genera mucho entusiasmo', 'd': 'Extraversión'},
                {'t': 'Tiene una naturaleza perdonadora', 'd': 'Amabilidad'},
                {'t': 'Tiende a ser desorganizado/a', 'd': 'Responsabilidad', 'r': True},
                {'t': 'Se preocupa mucho', 'd': 'Neuroticismo'},
                {'t': 'Tiene una imaginación activa', 'd': 'Apertura'},
                {'t': 'Tiende a ser callado/a', 'd': 'Extraversión', 'r': True},
                {'t': 'Generalmente es confiado/a', 'd': 'Amabilidad'},
                {'t': 'Tiende a ser perezoso/a', 'd': 'Responsabilidad', 'r': True},
                {'t': 'Es emocionalmente estable, no se altera fácilmente', 'd': 'Neuroticismo', 'r': True},
                {'t': 'Es inventivo/a', 'd': 'Apertura'},
                {'t': 'Tiene una personalidad asertiva', 'd': 'Extraversión'},
                {'t': 'Puede ser frío/a y distante', 'd': 'Amabilidad', 'r': True},
                {'t': 'Persevera hasta terminar la tarea', 'd': 'Responsabilidad'},
                {'t': 'Puede ser temperamental', 'd': 'Neuroticismo'},
                {'t': 'Valora las experiencias artísticas y estéticas', 'd': 'Apertura'},
                {'t': 'Es a veces tímido/a, inhibido/a', 'd': 'Extraversión', 'r': True},
                {'t': 'Es considerado/a y amable con casi todos', 'd': 'Amabilidad'},
                {'t': 'Hace las cosas de manera eficiente', 'd': 'Responsabilidad'},
                {'t': 'Permanece tranquilo/a en situaciones tensas', 'd': 'Neuroticismo', 'r': True},
                {'t': 'Prefiere el trabajo rutinario', 'd': 'Apertura', 'r': True},
                {'t': 'Es extrovertido/a, sociable', 'd': 'Extraversión'},
                {'t': 'A veces es grosero/a con los demás', 'd': 'Amabilidad', 'r': True},
                {'t': 'Hace planes y los sigue', 'd': 'Responsabilidad'},
                {'t': 'Se pone nervioso/a fácilmente', 'd': 'Neuroticismo'},
                {'t': 'Le gusta reflexionar, jugar con ideas', 'd': 'Apertura'},
                {'t': 'Tiene pocos intereses artísticos', 'd': 'Apertura', 'r': True},
                {'t': 'Le gusta cooperar con los demás', 'd': 'Amabilidad'},
                {'t': 'Se distrae fácilmente', 'd': 'Responsabilidad', 'r': True},
                {'t': 'Es sofisticado/a en arte, música o literatura', 'd': 'Apertura'},
            ]
        )

        self._seed(
            name='Tipología de Jung',
            dimension='identidad',
            description='Explora las cuatro funciones psicológicas junguianas: Introversión/Extraversión, Sensación/Intuición, Pensamiento/Sentimiento, Juicio/Percepción. La sombra es la función inferior — lo que más rechazas en ti es lo que más te controla.',
            estimated_minutes=6,
            order=2,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Prefiero pasar tiempo solo/a para recargar energías antes que socializar.', 'd': 'Introversión'},
                {'t': 'Me centro en los datos concretos y verificables más que en teorías abstractas.', 'd': 'Sensación'},
                {'t': 'Tomo decisiones basándome principalmente en la lógica y el análisis.', 'd': 'Pensamiento'},
                {'t': 'Prefiero tener las cosas planificadas y estructuradas antes de actuar.', 'd': 'Juicio'},
                {'t': 'Me energizo más en grupos y situaciones sociales que en soledad.', 'd': 'Extraversión'},
                {'t': 'Confío más en mi intuición y las posibilidades futuras que en los hechos presentes.', 'd': 'Intuición'},
                {'t': 'Las relaciones y los valores humanos pesan más que la lógica en mis decisiones.', 'd': 'Sentimiento'},
                {'t': 'Prefiero mantener mis opciones abiertas y adaptarme sobre la marcha.', 'd': 'Percepción'},
                {'t': 'Me siento más cómodo/a observando que siendo el centro de atención.', 'd': 'Introversión'},
                {'t': 'Noto los detalles sensoriales del mundo antes que los patrones abstractos.', 'd': 'Sensación'},
                {'t': 'Valoro más la justicia y la coherencia que la compasión al resolver conflictos.', 'd': 'Pensamiento'},
                {'t': 'Me incomoda dejar asuntos sin resolver o sin una conclusión clara.', 'd': 'Juicio'},
            ]
        )

        self._seed(
            name='Eneagrama — Tipología de carácter',
            dimension='identidad',
            description='Mapea los 9 eneatipos como estrategias egoicas de supervivencia. Cada tipo tiene una virtud (luz) y una pasión (sombra). Reconocer tu eneatipo no es para etiquetarte — es para ver el patrón que opera cuando estás en automático.',
            estimated_minutes=10,
            order=3,
            questions_data=[
                {'t': 'Siento que debo esforzarme constantemente por ser perfecto/a y corregir lo que está mal.', 'd': 'Tipo 1 — Reformador'},
                {'t': 'Mi mayor satisfacción viene de sentirme necesario/a y de ayudar a los demás.', 'd': 'Tipo 2 — Ayudador'},
                {'t': 'Me esfuerzo mucho por tener éxito y ser reconocido/a por mis logros.', 'd': 'Tipo 3 — Triunfador'},
                {'t': 'Siento con frecuencia que algo me falta o que soy fundamentalmente diferente a los demás.', 'd': 'Tipo 4 — Individualista'},
                {'t': 'Necesito mucho tiempo y espacio a solas para observar y procesar el mundo.', 'd': 'Tipo 5 — Investigador'},
                {'t': 'Me preocupo mucho por la seguridad y desconfío fácilmente de las intenciones ajenas.', 'd': 'Tipo 6 — Leal'},
                {'t': 'Busco constantemente nuevas experiencias, ideas y proyectos emocionantes.', 'd': 'Tipo 7 — Entusiasta'},
                {'t': 'Siento que debo ser fuerte y controlar mi entorno para protegerme.', 'd': 'Tipo 8 — Desafiador'},
                {'t': 'Tiendo a evitar conflictos y prefiero mantener la paz y la armonía a toda costa.', 'd': 'Tipo 9 — Pacificador'},
            ]
        )

        # ─── EMOCIONES Y REGULACIÓN ───

        self._seed(
            name='GAD-7 — Ansiedad Generalizada',
            dimension='emociones',
            description='Detecta la presencia y severidad de ansiedad clínica. La ansiedad no es un error del sistema — es una señal. La sombra es la ansiedad como modo de vida; la luz es la ansiedad como detector de lo que importa.',
            estimated_minutes=3,
            order=10,
            instrument_type='clinical',
            questions_data=[
                {'t': 'Sentirse nervioso/a, ansioso/a o con los nervios de punta.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'No poder dejar de preocuparse o no poder controlar la preocupación.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'Preocuparse demasiado por diferentes cosas.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'Dificultad para relajarse.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'Estar tan inquieto/a que es difícil permanecer sentado/a.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'Molestarse o irritarse fácilmente.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
                {'t': 'Sentir miedo como si algo terrible pudiera pasar.', 'd': 'Nivel de Ansiedad (GAD-7)', 'scale': 'likert3'},
            ]
        )

        self._seed(
            name='PHQ-9 — Cuestionario de Salud del Paciente',
            dimension='emociones',
            description='Instrumento validado para detectar y graduar la severidad de la depresión. 9 ítems basados en los criterios diagnósticos del DSM. Desde la perspectiva endonauta, la depresión suele ser una llamada del alma a retirar energía del mundo exterior para reparar el mundo interior.',
            estimated_minutes=4,
            order=11,
            instrument_type='clinical',
            questions_data=[
                {'t': 'Poco interés o placer en hacer cosas.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Sentirse decaído/a, deprimido/a o sin esperanzas.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Dificultad para quedarse o permanecer dormido/a, o dormir demasiado.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Sentirse cansado/a o con poca energía.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Tener poco apetito o comer en exceso.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Sentirse mal consigo mismo/a — o sentir que es un fracaso o que ha decepcionado a su familia o a sí mismo/a.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Dificultad para concentrarse en cosas, como leer o ver televisión.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Moverse o hablar tan lento que otras personas podrían haberlo notado; o al contrario, estar tan agitado/a e inquieto/a que se ha estado moviendo mucho más de lo usual.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
                {'t': 'Pensamientos de que estaría mejor muerto/a, o de hacerse daño de alguna manera.', 'd': 'Indicadores Depresivos (PHQ-9)', 'scale': 'likert3'},
            ]
        )

        self._seed(
            name='DERS — Dificultades en Regulación Emocional',
            dimension='emociones',
            description='Evalúa seis dimensiones de regulación emocional: claridad, atención, aceptación, impulsividad, acceso a estrategias e interferencia. La luz es surfear la ola emocional; la sombra es ser arrastrado por ella o suprimirla.',
            estimated_minutes=5,
            order=12,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Tengo claro lo que siento.', 'd': 'Claridad', 'r': True},
                {'t': 'Presto atención a lo que siento.', 'd': 'Atención', 'r': True},
                {'t': 'Cuando estoy mal, me avergüenzo de mis sentimientos.', 'd': 'No-aceptación'},
                {'t': 'Cuando estoy mal, me cuesta concentrarme en otra cosa.', 'd': 'Interferencia'},
                {'t': 'Cuando estoy mal, pierdo el control sobre mi comportamiento.', 'd': 'Impulsividad'},
                {'t': 'Cuando estoy mal, creo que no hay nada que pueda hacer para sentirme mejor.', 'd': 'Estrategias'},
                {'t': 'Cuando estoy mal, me siento fuera de control.', 'd': 'Impulsividad'},
                {'t': 'Cuando estoy mal, me quedo atrapado/a en mis emociones.', 'd': 'Estrategias'},
            ]
        )

        self._seed(
            name='TAS-20 — Alexitimia (Escala Toronto)',
            dimension='emociones',
            description='La alexitimia es la dificultad para identificar y describir emociones propias. No es falta de emociones — es un muro entre el sentimiento y el lenguaje. La sombra es vivir desconectado del cuerpo emocional; la luz es habitar las emociones con vocabulario y conciencia.',
            estimated_minutes=7,
            order=13,
            default_scale='likert5a',
            instrument_type='clinical',
            questions_data=[
                # DIF — Dificultad para Identificar Sentimientos (7 ítems)
                {'t': 'A menudo estoy confundido/a sobre qué emoción estoy sintiendo.', 'd': 'Identificación'},
                {'t': 'Me es difícil encontrar las palabras adecuadas para mis sentimientos.', 'd': 'Descripción'},
                {'t': 'Tengo sensaciones físicas que ni los médicos entienden.', 'd': 'Identificación'},
                {'t': 'Soy capaz de describir mis sentimientos fácilmente.', 'd': 'Descripción', 'r': True},
                {'t': 'Prefiero analizar los problemas en lugar de simplemente describirlos.', 'd': 'Pensamiento Externo', 'r': True},
                {'t': 'Cuando estoy nervioso/a no sé si estoy triste, asustado/a o enfadado/a.', 'd': 'Identificación'},
                {'t': 'A menudo me desconciertan las sensaciones de mi cuerpo.', 'd': 'Identificación'},
                {'t': 'Prefiero que las cosas simplemente ocurran, en lugar de entender por qué han sucedido así.', 'd': 'Pensamiento Externo'},
                {'t': 'Tengo sentimientos que no puedo identificar con claridad.', 'd': 'Identificación'},
                {'t': 'Estar en contacto con las emociones es esencial.', 'd': 'Pensamiento Externo', 'r': True},
                {'t': 'Me resulta difícil describir cómo me siento con las personas.', 'd': 'Descripción'},
                {'t': 'La gente me dice que describa más mis sentimientos.', 'd': 'Descripción'},
                {'t': 'No sé lo que pasa dentro de mí.', 'd': 'Identificación'},
                {'t': 'Frecuentemente no sé por qué estoy enfadado/a.', 'd': 'Identificación'},
                {'t': 'Prefiero hablar con las personas sobre sus actividades diarias más que sobre sus sentimientos.', 'd': 'Pensamiento Externo'},
                {'t': 'Prefiero ver espectáculos de entretenimiento ligero más que dramas psicológicos.', 'd': 'Pensamiento Externo'},
                {'t': 'Me resulta difícil revelar mis sentimientos más íntimos incluso con los amigos más íntimos.', 'd': 'Descripción'},
                {'t': 'Puedo sentirme cercano/a a alguien, incluso en momentos de silencio.', 'd': 'Pensamiento Externo', 'r': True},
                {'t': 'Encuentro útil examinar mis sentimientos para resolver problemas personales.', 'd': 'Pensamiento Externo', 'r': True},
                {'t': 'Buscar significados ocultos en películas o novelas me resta el disfrute que producen.', 'd': 'Pensamiento Externo'},
            ]
        )

        self._seed(
            name='PSS-10 — Estrés Percibido',
            dimension='emociones',
            description='Mide el grado en que las situaciones de la vida se perciben como incontrolables o abrumadoras. No mide el estrés objetivo — mide tu relación subjetiva con él. La luz es el estrés como señal; la sombra es el estrés como identidad.',
            estimated_minutes=4,
            order=14,
            instrument_type='clinical',
            questions_data=[
                {'t': 'En el último mes, ¿con qué frecuencia te has sentido afectado/a por algo inesperado?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4'},
                {'t': 'En el último mes, ¿con qué frecuencia sentiste que no podías controlar cosas importantes?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4'},
                {'t': 'En el último mes, ¿con qué frecuencia te sentiste nervioso/a o estresado/a?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4'},
                {'t': 'En el último mes, ¿con qué frecuencia manejaste con éxito los problemas irritantes?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4', 'r': True},
                {'t': 'En el último mes, ¿con qué frecuencia afrontaste efectivamente los cambios importantes?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4', 'r': True},
                {'t': 'En el último mes, ¿con qué frecuencia confiaste en tu capacidad para manejar problemas personales?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4', 'r': True},
                {'t': 'En el último mes, ¿con qué frecuencia sentiste que las cosas iban bien?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4', 'r': True},
                {'t': 'En el último mes, ¿con qué frecuencia sentiste que no podías afrontar todo lo que debías hacer?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4'},
                {'t': 'En el último mes, ¿con qué frecuencia pudiste controlar las dificultades de tu vida?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4', 'r': True},
                {'t': 'En el último mes, ¿con qué frecuencia sentiste que las dificultades se acumulaban tanto que no podías superarlas?', 'd': 'Estrés Percibido (PSS-10)', 'scale': 'likert4'},
            ]
        )

        # ─── CUERPO Y SENSORIALIDAD ───

        self._seed(
            name='MAIA — Consciencia Interoceptiva',
            dimension='cuerpo',
            description='Evalúa tu capacidad de habitar el cuerpo: notar sensaciones, no distorsionarlas, regularlas. El cuerpo es el primer espejo. La sombra es la desconexión somática; la luz es el cuerpo como guía.',
            estimated_minutes=6,
            order=20,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Cuando estoy tenso/a, me doy cuenta de dónde tengo la tensión en mi cuerpo.', 'd': 'Notar'},
                {'t': 'Noto cambios en mi respiración, como si se acelera o se vuelve superficial.', 'd': 'Notar'},
                {'t': 'Noto cómo mi cuerpo cambia cuando me siento feliz.', 'd': 'Notar'},
                {'t': 'Tiendo a ignorar el dolor o el malestar físico hasta que se vuelve insoportable.', 'd': 'No-Distracción', 'r': True},
                {'t': 'Me distraigo para no sentir dolor o malestar en mi cuerpo.', 'd': 'No-Distracción', 'r': True},
                {'t': 'No me presto atención a sensaciones físicas de dolor o malestar.', 'd': 'No-Distracción', 'r': True},
                {'t': 'Cuando siento dolor en mi cuerpo, me preocupo mucho por lo que pueda significar.', 'd': 'No-Preocupación', 'r': True},
                {'t': 'Me asusto cuando siento dolor o malestar en mi cuerpo.', 'd': 'No-Preocupación', 'r': True},
                {'t': 'Puedo concentrarme en todo mi cuerpo incluso cuando hay muchas cosas sucediendo.', 'd': 'Atención'},
                {'t': 'Puedo prestar atención a mis sensaciones físicas cuando lo decido.', 'd': 'Atención'},
                {'t': 'Puedo recuperar mi enfoque en mi cuerpo cuando mi mente divaga.', 'd': 'Atención'},
                {'t': 'Noto que mi respiración cambia cuando siento emociones fuertes.', 'd': 'Consciencia Emocional'},
                {'t': 'Cuando algo está mal en mi vida, lo siento en mi cuerpo.', 'd': 'Consciencia Emocional'},
                {'t': 'Puedo percibir mis emociones al sentir cómo reacciona mi cuerpo.', 'd': 'Consciencia Emocional'},
                {'t': 'Cuando me siento abrumado/a, puedo encontrar un lugar de calma dentro de mi cuerpo.', 'd': 'Auto-regulación'},
                {'t': 'Puedo calmar mi mente prestando atención a cómo se siente mi cuerpo.', 'd': 'Auto-regulación'},
                {'t': 'Uso mi respiración para calmarme.', 'd': 'Auto-regulación'},
                {'t': 'Escucho a mi cuerpo para que me informe qué hacer.', 'd': 'Escucha Corporal'},
                {'t': 'Mi cuerpo me dice cuándo necesito descansar.', 'd': 'Escucha Corporal'},
                {'t': 'Siento que mi cuerpo es un lugar seguro.', 'd': 'Confianza'},
                {'t': 'Confío en las señales de mi cuerpo.', 'd': 'Confianza'},
            ]
        )

        self._seed(
            name='PSQI — Calidad del Sueño de Pittsburgh',
            dimension='cuerpo',
            description='Evalúa 7 dimensiones del sueño. La noche es el espejo del día. La calidad del sueño revela la calidad de tu relación con el descanso, el soltar el control y la confianza en el cuerpo.',
            estimated_minutes=7,
            order=21,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Durante el último mes, ¿cómo calificarías en general la calidad de tu sueño?', 'd': 'Calidad Subjetiva', 'scale': 'likert3'},
                {'t': '¿Cuánto tiempo (minutos) te toma generalmente quedarte dormido/a?', 'd': 'Latencia', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia no pudiste conciliar el sueño en los primeros 30 minutos?', 'd': 'Latencia', 'scale': 'likert3'},
                {'t': '¿Cuántas horas dormiste por noche en el último mes?', 'd': 'Duración', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia te despertaste a media noche o muy temprano?', 'd': 'Perturbaciones', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia tuviste dificultad para respirar cómodamente al dormir?', 'd': 'Perturbaciones', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia tomaste medicamentos para dormir?', 'd': 'Medicación', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia tuviste dificultad para mantenerte despierto/a durante el día?', 'd': 'Disfunción diurna', 'scale': 'likert3'},
                {'t': '¿Con qué frecuencia te resultó difícil mantener el entusiasmo para realizar tus actividades?', 'd': 'Disfunción diurna', 'scale': 'likert3'},
            ]
        )

        self._seed(
            name='Perfil Neurosensorial',
            dimension='cuerpo',
            description='Evalúa tu sistema de procesamiento sensorial: bajo registro, búsqueda sensorial, sensibilidad y evitación. Tu sistema nervioso no es tu enemigo — es tu hardware original. Conocerlo es el mapa técnico para diseñar una vida donde puedas prosperar.',
            estimated_minutes=5,
            order=22,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Necesito estímulos intensos (música fuerte, sabores fuertes) para notar las cosas.', 'd': 'Bajo Registro'},
                {'t': 'A menudo no me doy cuenta del calor, el frío o el dolor hasta que son extremos.', 'd': 'Bajo Registro'},
                {'t': 'Busco activamente sensaciones intensas: velocidad, ruido, movimiento.', 'd': 'Búsqueda Sensorial'},
                {'t': 'Me aburro rápido en ambientes tranquilos y necesito estimulación constante.', 'd': 'Búsqueda Sensorial'},
                {'t': 'Me molestan mucho las texturas, sonidos o luces que otros apenas notan.', 'd': 'Sensibilidad Sensorial'},
                {'t': 'Entornos con mucha actividad (centros comerciales, fiestas) me agotan rápido.', 'd': 'Sensibilidad Sensorial'},
                {'t': 'Evito activamente lugares o situaciones con mucho ruido, olor o movimiento.', 'd': 'Evitación Sensorial'},
                {'t': 'Necesito mucho orden y rutina en mi entorno para sentirme bien.', 'd': 'Evitación Sensorial'},
            ]
        )

        self._seed(
            name='Vitalidad Subjetiva (SVI)',
            dimension='cuerpo',
            description='Mide la sensación de estar vivo/a y con energía disponible. No es energía física — es la energía de la alineación interna. Cuando fluyes sin resistencias internas, te sientes vital independientemente del cansancio.',
            estimated_minutes=3,
            order=23,
            instrument_type='clinical',
            questions_data=[
                {'t': 'Me siento vivo/a y vital.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
                {'t': 'A veces me siento tan vivo/a que parece que voy a estallar.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
                {'t': 'Tengo energía y espíritu.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
                {'t': 'Espero con ganas cada nuevo día.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
                {'t': 'Casi siempre me siento alerta y despierto/a.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
                {'t': 'Me siento lleno/a de energía.', 'd': 'Vitalidad Subjetiva', 'scale': 'likert7'},
            ]
        )

        # ─── VÍNCULOS Y APEGO ───

        self._seed(
            name='ECR — Estilos de Apego en Relaciones',
            dimension='vinculos',
            description='Evalúa dos dimensiones del apego adulto: ansiedad de apego (miedo al abandono) y evitación de apego (miedo a la intimidad). El estilo de apego no es un rasgo permanente — es la estrategia que aprendiste de niño/a para sobrevivir la relación con tus cuidadores.',
            estimated_minutes=5,
            order=30,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Me preocupa mucho que mis parejas dejen de quererme.', 'd': 'Ansiedad de Apego', 'scale': 'likert7'},
                {'t': 'Rara vez me preocupa que mi pareja me abandone.', 'd': 'Ansiedad de Apego', 'scale': 'likert7', 'r': True},
                {'t': 'Necesito demasiada confirmación de que soy amado/a.', 'd': 'Ansiedad de Apego', 'scale': 'likert7'},
                {'t': 'A veces siento que presiono a mis parejas para que muestren más sentimiento.', 'd': 'Ansiedad de Apego', 'scale': 'likert7'},
                {'t': 'Me enojo cuando mi pareja no pasa suficiente tiempo conmigo.', 'd': 'Ansiedad de Apego', 'scale': 'likert7'},
                {'t': 'Me pone nervioso/a cuando una pareja se acerca demasiado a mí.', 'd': 'Evitación de Apego', 'scale': 'likert7'},
                {'t': 'Me resulta fácil depender de mis parejas sentimentales.', 'd': 'Evitación de Apego', 'scale': 'likert7', 'r': True},
                {'t': 'No me siento cómodo/a abriéndome a mis parejas.', 'd': 'Evitación de Apego', 'scale': 'likert7'},
                {'t': 'Prefiero no mostrar a mi pareja cómo me siento en el fondo.', 'd': 'Evitación de Apego', 'scale': 'likert7'},
                {'t': 'Me siento incómodo/a cuando mi pareja quiere mucha cercanía.', 'd': 'Evitación de Apego', 'scale': 'likert7'},
            ]
        )

        # ─── SOMBRA Y PATRONES ───

        self._seed(
            name='Heridas de la Infancia — Lise Bourbeau',
            dimension='sombra',
            description='Las 5 heridas nucleares que en la infancia generaron máscaras de defensa — Abandono, Rechazo, Humillación, Injusticia y Traición. Cada herida activa también un patrón en el cuerpo. Identificar la tuya no es culpar el pasado: es reconocer la máscara que hoy usas de forma automática para dejar de sentir el dolor original.',
            estimated_minutes=6,
            order=40,
            default_scale='binary',
            questions_data=[
                # ── ABANDONO ──
                {'t': '¿La soledad te aterra y sueles aguantar relaciones por no estar solo/a?', 'd': 'Abandono'},
                {'t': '¿Sientes incapacidad para poner límites y decir claramente lo que necesitas?', 'd': 'Abandono'},
                {'t': '¿Sueles hacerte dependiente de las personas?', 'd': 'Abandono'},
                {'t': '¿Muchas veces descalificas o sobredimensionas las circunstancias?', 'd': 'Abandono'},
                {'t': '¿Terminas sintiendo que las personas no te quieren y no te valoran?', 'd': 'Abandono'},
                # ── RECHAZO ──
                {'t': '¿De niño/a tenías problemas en las vías respiratorias (asma, rinitis) o en la piel con frecuencia?', 'd': 'Rechazo'},
                {'t': '¿Fuiste un niño/a solitario/a, callado/a, que sentía no ser parte de su familia o del mundo?', 'd': 'Rechazo'},
                {'t': '¿Frecuentemente dudas de tu capacidad o sientes miedo a ser rechazado/a?', 'd': 'Rechazo'},
                {'t': '¿Tienes o tuviste una relación de enojo muy fuerte con el progenitor de tu mismo sexo?', 'd': 'Rechazo'},
                {'t': '¿Lo intelectual, la música, los videojuegos y las actividades en solitario te atraen especialmente?', 'd': 'Rechazo'},
                # ── HUMILLACIÓN ──
                {'t': '¿Te das cuenta de que eres súper complaciente e incondicional con los demás?', 'd': 'Humillación'},
                {'t': '¿Tu infancia, tu cuerpo o tu sexualidad te generan vergüenza?', 'd': 'Humillación'},
                {'t': '¿Te cuesta ver y satisfacer tus propias necesidades?', 'd': 'Humillación'},
                {'t': '¿Tienes sobrepeso o tendencia a acumular peso como protección?', 'd': 'Humillación'},
                {'t': '¿Sueles ser la ambulancia, el paño de lágrimas o el/la rescatador/a de los demás?', 'd': 'Humillación'},
                # ── INJUSTICIA ──
                {'t': '¿Eres perfeccionista, estricto/a, rígido/a, parecido/a a tu mamá o papá en eso?', 'd': 'Injusticia'},
                {'t': '¿No sabes pedir ayuda?', 'd': 'Injusticia'},
                {'t': '¿Te cuesta ser espontáneo/a y hacer cosas simplemente por diversión?', 'd': 'Injusticia'},
                {'t': '¿El orden, la estructura y la disciplina son lo tuyo?', 'd': 'Injusticia'},
                {'t': '¿Eres muy sensible pero no te permites mostrar tus emociones?', 'd': 'Injusticia'},
                # ── TRAICIÓN ──
                {'t': '¿Te cuesta confiar aunque la confianza esté probada?', 'd': 'Traición'},
                {'t': '¿Tienes siempre altas expectativas de todo y de todos?', 'd': 'Traición'},
                {'t': '¿Eres organizador/a de vidas, vas de prisa y haces varias cosas a la vez?', 'd': 'Traición'},
                {'t': '¿Sueles sentir que siempre tienes la razón?', 'd': 'Traición'},
                {'t': '¿Eres muy mental/intuitivo/a y odias la mentira?', 'd': 'Traición'},
            ]
        )

        self._seed(
            name='IBI — Creencias Irracionales',
            dimension='sombra',
            description='Basado en la Terapia Racional-Emotiva de Ellis. Las creencias irracionales son "debos" y "tengos" que le exigimos a la realidad. La sombra es vivir gobernado por estas reglas; la luz es la flexibilidad radical.',
            estimated_minutes=5,
            order=41,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Es absolutamente necesario que todos me aprueben y me quieran.', 'd': 'Necesidad de Aprobación'},
                {'t': 'Si alguien no me aprueba, significa que hay algo mal en mí.', 'd': 'Necesidad de Aprobación'},
                {'t': 'Debo ser completamente competente y exitoso en todo lo que hago.', 'd': 'Perfeccionismo'},
                {'t': 'Cometer un error es terrible y catastrófico.', 'd': 'Perfeccionismo'},
                {'t': 'Las personas que hacen cosas malas deben ser severamente castigadas.', 'd': 'Culpa y Condena'},
                {'t': 'Si las cosas no salen como yo quiero, es una catástrofe.', 'd': 'Intolerancia a la Frustración'},
                {'t': 'No puedo soportar cuando la vida es injusta o difícil.', 'd': 'Intolerancia a la Frustración'},
                {'t': 'La felicidad es algo que me pasa; yo tengo poco control sobre ella.', 'd': 'Irresponsabilidad Emocional'},
                {'t': 'Si algo parece peligroso o temible, debo preocuparme constantemente por ello.', 'd': 'Ansiedad Ansiosa'},
                {'t': 'Es más fácil evitar los problemas y responsabilidades que enfrentarlos.', 'd': 'Evitación'},
            ]
        )

        self._seed(
            name='Autosabotaje',
            dimension='sombra',
            description='Evalúa 4 patrones de autosabotaje: procrastinación, perfeccionismo paralizante, miedo al éxito y síndrome del impostor. El autosabotaje no es falta de disciplina — es tu sistema psíquico protegiéndote de un dolor percibido mayor.',
            estimated_minutes=5,
            order=42,
            questions_data=[
                {'t': 'Dejo las tareas importantes para el último minuto.', 'd': 'Procrastinación'},
                {'t': 'Empiezo proyectos con entusiasmo pero nunca los termino.', 'd': 'Procrastinación'},
                {'t': 'Me distraigo con cosas triviales cuando tengo trabajo importante que hacer.', 'd': 'Procrastinación'},
                {'t': 'Si no puedo hacer algo perfecto, prefiero no hacerlo.', 'd': 'Perfeccionismo Paralizante'},
                {'t': 'Dedico demasiado tiempo a los detalles, retrasando el avance general.', 'd': 'Perfeccionismo Paralizante'},
                {'t': 'Cuando estoy cerca de lograr un objetivo, algo sucede y me desvío o fracaso.', 'd': 'Miedo al Éxito'},
                {'t': 'Siento ansiedad cuando las cosas me empiezan a ir demasiado bien.', 'd': 'Miedo al Éxito'},
                {'t': 'Dudo de mis capacidades incluso cuando tengo pruebas de mi competencia.', 'd': 'Síndrome del Impostor'},
                {'t': 'Atribuyo mis éxitos a la suerte en lugar de a mi esfuerzo.', 'd': 'Síndrome del Impostor'},
            ]
        )

        self._seed(
            name='Dirty Dozen — Tríada Oscura',
            dimension='sombra',
            description='Evalúa Maquiavelismo, Narcisismo y Psicopatía subclínicos con el instrumento validado Dirty Dozen (Jonason & Webster, 2010). La verdadera bondad es un logro consciente — reconocer los dientes que tienes y decidir conscientemente no usarlos. Este test no es para juzgarte sino para ver tu sombra con claridad.',
            estimated_minutes=5,
            order=43,
            default_scale='likert5a',
            instrument_type='clinical',
            questions_data=[
                {'t': 'Tiendo a manipular a otros para conseguir lo que quiero.', 'd': 'Maquiavelismo'},
                {'t': 'He usado el engaño o la mentira para conseguir lo que quiero.', 'd': 'Maquiavelismo'},
                {'t': 'He usado la adulación para conseguir lo que quiero.', 'd': 'Maquiavelismo'},
                {'t': 'Tiendo a explotar a otros en mi propio beneficio.', 'd': 'Maquiavelismo'},
                {'t': 'Tiendo a querer que otros me admiren.', 'd': 'Narcisismo'},
                {'t': 'Tiendo a querer que otros me presten atención.', 'd': 'Narcisismo'},
                {'t': 'Tiendo a buscar prestigio o estatus.', 'd': 'Narcisismo'},
                {'t': 'Tiendo a esperar favores especiales de otros.', 'd': 'Narcisismo'},
                {'t': 'Tiendo a carecer de remordimientos.', 'd': 'Psicopatía'},
                {'t': 'Tiendo a no preocuparme por la moralidad de mis acciones.', 'd': 'Psicopatía'},
                {'t': 'Tiendo a ser insensible o indiferente.', 'd': 'Psicopatía'},
                {'t': 'Tiendo a ser cínico/a.', 'd': 'Psicopatía'},
            ]
        )

        # ─── ESPIRITUALIDAD Y SENTIDO ───

        self._seed(
            name='Logo-Test — Sentido de Vida',
            dimension='espiritualidad',
            description='Basado en la logoterapia de Viktor Frankl. La voluntad de sentido es la motivación primaria del ser humano. La sombra es el vacío existencial; la luz es vivir desde un "para qué" que trasciende el ego.',
            estimated_minutes=4,
            order=50,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Siento que mi vida tiene sentido y dirección.', 'd': 'Sentido'},
                {'t': 'Me siento aburrido/a o vacío/a a menudo.', 'd': 'Vacío Existencial', 'r': True},
                {'t': 'Tengo metas claras por las que vale la pena luchar.', 'd': 'Sentido'},
                {'t': 'Siento que mi existencia es puramente accidental.', 'd': 'Vacío Existencial', 'r': True},
                {'t': 'Incluso en el sufrimiento, puedo encontrar una razón para seguir.', 'd': 'Resiliencia de Sentido'},
            ]
        )

        self._seed(
            name='Bienestar Espiritual (SWB)',
            dimension='espiritualidad',
            description='Evalúa dos dimensiones: bienestar existencial (propósito y satisfacción vital) y bienestar religioso/trascendente (conexión con algo mayor). No requiere creencia religiosa — requiere sentido.',
            estimated_minutes=4,
            order=51,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Siento que mi vida tiene un propósito profundo.', 'd': 'Bienestar Existencial'},
                {'t': 'Tengo una relación personal con algo superior o trascendente.', 'd': 'Bienestar Religioso'},
                {'t': 'Me siento muy realizado/a con lo que estoy haciendo con mi vida.', 'd': 'Bienestar Existencial'},
                {'t': 'Mi relación con lo divino me da una sensación de paz.', 'd': 'Bienestar Religioso'},
                {'t': 'No sé quién soy, de dónde vengo o hacia dónde voy.', 'd': 'Bienestar Existencial', 'r': True},
                {'t': 'Siento que lo trascendente se preocupa por mí.', 'd': 'Bienestar Religioso'},
                {'t': 'Disfruto mucho de la vida.', 'd': 'Bienestar Existencial'},
                {'t': 'Creo que hay un plan para mi vida.', 'd': 'Bienestar Religioso'},
            ]
        )

        self._seed(
            name='Trascendencia de Cloninger',
            dimension='espiritualidad',
            description='Evalúa la capacidad de disolver las fronteras del ego y sentirse parte de una totalidad mayor. La sombra es el ego como única realidad; la luz es el yo como parte de algo más vasto.',
            estimated_minutes=4,
            order=52,
            instrument_type='adapted',
            questions_data=[
                {'t': 'A veces me siento tan absorto/a en lo que estoy haciendo que pierdo la noción del tiempo.', 'd': 'Absorción Transpersonal'},
                {'t': 'A menudo me siento conectado/a con la naturaleza y todo lo que me rodea.', 'd': 'Identificación Mística'},
                {'t': 'Creo que los milagros y las cosas inexplicables ocurren a menudo.', 'd': 'Aceptación Espiritual'},
                {'t': 'He tenido momentos de alegría intensa en los que me sentí uno/a con el universo.', 'd': 'Identificación Mística'},
                {'t': 'A veces me siento como si estuviera fuera de mi cuerpo.', 'd': 'Absorción Transpersonal'},
            ]
        )

        self._seed(
            name='Perfil de Chakras',
            dimension='espiritualidad',
            description='Los 7 centros de energía como mapa de la conciencia encarnada. Un chakra "bloqueado" es una parte de tu experiencia vital que no está recibiendo atención. La luz es el flujo; la sombra es el estancamiento o el exceso.',
            estimated_minutes=6,
            order=53,
            questions_data=[
                {'t': 'Me siento seguro/a y con derecho a estar aquí en la Tierra.', 'd': 'Muladhara (Raíz)'},
                {'t': 'Tengo buena conexión con mis necesidades físicas (comida, refugio, salud).', 'd': 'Muladhara (Raíz)'},
                {'t': 'Me permito sentir placer y disfrutar de mis sentidos sin culpa.', 'd': 'Svadhisthana (Sacro)'},
                {'t': 'Tengo una sexualidad sana y fluida.', 'd': 'Svadhisthana (Sacro)'},
                {'t': 'Confío en mi poder personal y capacidad de manifestar lo que deseo.', 'd': 'Manipura (Plexo Solar)'},
                {'t': 'Tengo buena digestión y niveles de energía constantes.', 'd': 'Manipura (Plexo Solar)'},
                {'t': 'Siento amor y compasión hacia mí mismo/a y hacia los demás.', 'd': 'Anahata (Corazón)'},
                {'t': 'Tengo relaciones sanas basadas en la apertura del corazón.', 'd': 'Anahata (Corazón)'},
                {'t': 'Expreso mi verdad con claridad y honestidad.', 'd': 'Vishuddha (Garganta)'},
                {'t': 'Soy capaz de escuchar profundamente a los demás.', 'd': 'Vishuddha (Garganta)'},
                {'t': 'Confío en mi intuición y tengo una visión clara de mi vida.', 'd': 'Ajna (Tercer Ojo)'},
                {'t': 'Tengo sueños vívidos o momentos de "saber" sin razonar.', 'd': 'Ajna (Tercer Ojo)'},
                {'t': 'Siento una conexión con algo más grande que yo.', 'd': 'Sahasrara (Corona)'},
                {'t': 'Experimento momentos de paz profunda y unidad.', 'd': 'Sahasrara (Corona)'},
            ]
        )

        # ─── SUEÑOS Y CONCIENCIA ───

        self._seed(
            name='Índice de Recuerdo Onírico (DRI)',
            dimension='suenos',
            description='Mide la frecuencia y calidad del recuerdo de sueños. Tu relación con los sueños es un puente hacia tu inconsciente. Aumentar el recuerdo es el primer paso para integrar el material onírico en tu proceso de individuación.',
            estimated_minutes=4,
            order=60,
            questions_data=[
                {'t': '¿Con qué frecuencia recuerdas tus sueños al despertar?', 'd': 'Recuerdo'},
                {'t': '¿Qué tan vívidos o intensos son tus sueños?', 'd': 'Nitidez'},
                {'t': '¿Recuerdas fragmentos o historias completas?', 'd': 'Complejidad'},
                {'t': '¿Con qué frecuencia tienes sueños recurrentes (mismos temas o lugares)?', 'd': 'Recurrencia'},
                {'t': '¿Sientes que tus sueños influyen en tu estado de ánimo al despertar?', 'd': 'Impacto'},
            ]
        )

        self._seed(
            name='Escala de Lucidez en Sueños (DLQ)',
            dimension='suenos',
            description='Evalúa la capacidad de despertar conscientemente dentro del sueño. La lucidez onírica expande la conciencia y permite usar la noche como campo de entrenamiento para la vigilia plena.',
            estimated_minutes=3,
            order=61,
            questions_data=[
                {'t': '¿Te das cuenta de que estás soñando mientras el sueño ocurre?', 'd': 'Conciencia'},
                {'t': '¿Puedes controlar o cambiar el curso de tus sueños?', 'd': 'Control'},
                {'t': '¿Has intentado técnicas para tener sueños lúcidos (WBTB, MILD, WILD)?', 'd': 'Práctica'},
            ]
        )

        # ─── PROPÓSITO Y TRABAJO ───

        self._seed(
            name='VIA — Fortalezas de Carácter',
            dimension='proposito',
            description='Identifica tus fortalezas núcleo de carácter: sabiduría, valor, humanidad, justicia, templanza y trascendencia. Las fortalezas que no se eligen pueden volverse automáticas y rígidas. La maestría es saber cuándo y cómo aplicarlas.',
            estimated_minutes=8,
            order=70,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Siempre encuentro formas creativas de resolver problemas.', 'd': 'Sabiduría'},
                {'t': 'Me gusta aprender cosas nuevas, incluso si no son útiles de inmediato.', 'd': 'Sabiduría'},
                {'t': 'Tengo una mente abierta y considero todos los puntos de vista.', 'd': 'Sabiduría'},
                {'t': 'Tengo la valentía de defender lo que creo que es correcto.', 'd': 'Valor'},
                {'t': 'Termino todo lo que empiezo, a pesar de los obstáculos.', 'd': 'Valor'},
                {'t': 'Soy muy cariñoso/a y afectuoso/a con las personas que me importan.', 'd': 'Humanidad'},
                {'t': 'Siempre estoy dispuesto/a a ayudar a los demás.', 'd': 'Humanidad'},
                {'t': 'Trato a todos con igualdad y justicia.', 'd': 'Justicia'},
                {'t': 'Trabajo muy bien en equipo.', 'd': 'Justicia'},
                {'t': 'Siempre pienso antes de actuar.', 'd': 'Templanza'},
                {'t': 'Soy capaz de perdonar a personas que me han tratado mal.', 'd': 'Templanza'},
                {'t': 'Siento que mi vida tiene un propósito y un significado más profundo.', 'd': 'Trascendencia'},
                {'t': 'Siempre veo el lado positivo de las cosas.', 'd': 'Trascendencia'},
            ]
        )

        self._seed(
            name='RIASEC — Perfil Vocacional de Holland',
            dimension='proposito',
            description='Los 6 tipos de personalidad vocacional: Realista, Investigador, Artístico, Social, Emprendedor, Convencional. Prosperamos en entornos que coinciden con nuestra personalidad. Tu código RIASEC es el mapa de dónde te sentirás más natural y efectivo.',
            estimated_minutes=6,
            order=71,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Disfruto trabajar con herramientas, máquinas o animales.', 'd': 'Realista'},
                {'t': 'Me gusta construir o reparar cosas con mis manos.', 'd': 'Realista'},
                {'t': 'Disfruto resolver problemas complejos y analizar datos.', 'd': 'Investigador'},
                {'t': 'Me apasiona la ciencia y el conocimiento profundo.', 'd': 'Investigador'},
                {'t': 'Disfruto expresarme a través del arte, la música o la escritura.', 'd': 'Artístico'},
                {'t': 'Me gustan las actividades que requieren creatividad e imaginación.', 'd': 'Artístico'},
                {'t': 'Disfruto enseñar, orientar o ayudar a otras personas.', 'd': 'Social'},
                {'t': 'Me importa mucho el bienestar de los demás.', 'd': 'Social'},
                {'t': 'Me gusta liderar grupos y tomar decisiones.', 'd': 'Emprendedor'},
                {'t': 'Disfruto persuadir a otros y vender ideas o productos.', 'd': 'Emprendedor'},
                {'t': 'Disfruto trabajar con datos, registros y sistemas organizados.', 'd': 'Convencional'},
                {'t': 'Prefiero tareas con instrucciones claras y procedimientos definidos.', 'd': 'Convencional'},
            ]
        )

        self._seed(
            name='MWQ — Sentido del Trabajo',
            dimension='proposito',
            description='Mide el grado de significado y propósito en tu labor profesional. El trabajo deja de ser una carga cuando se convierte en una vía de expresión de tus valores. Si el puntaje es bajo, no significa renunciar — sino encontrar cómo inyectar sentido en tus tareas actuales.',
            estimated_minutes=4,
            order=72,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Mi trabajo contribuye significativamente al bienestar de los demás.', 'd': 'Sentido del Trabajo'},
                {'t': 'Siento que lo que hago en el trabajo tiene un propósito importante.', 'd': 'Sentido del Trabajo'},
                {'t': 'Mi trabajo me da la oportunidad de expresar mis valores más importantes.', 'd': 'Sentido del Trabajo'},
                {'t': 'Cuando termina la jornada, siento que he hecho algo que vale la pena.', 'd': 'Sentido del Trabajo'},
            ]
        )

        # ─── COMUNIDAD Y RELACIONES ───

        self._seed(
            name='MOS-SSS — Apoyo Social Percibido',
            dimension='comunidad',
            description='Evalúa la calidad percibida de tu red de apoyo social: emocional, informacional, instrumental y de compañía. Somos seres tribales. Tu salud biológica y mental está íntimamente ligada a la calidad de tu red social.',
            estimated_minutes=5,
            order=80,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Hay alguien disponible cuando necesito ayuda si estoy enfermo/a o incapacitado/a.', 'd': 'Apoyo Instrumental'},
                {'t': 'Hay alguien con quien puedo contar para escucharme cuando necesito hablar.', 'd': 'Apoyo Emocional'},
                {'t': 'Hay alguien que me da información para ayudarme a entender una situación.', 'd': 'Apoyo Informacional'},
                {'t': 'Hay alguien con quien hacer cosas agradables.', 'd': 'Apoyo de Compañía'},
                {'t': 'Hay alguien que me quiere y me hace sentir querido/a.', 'd': 'Apoyo Emocional'},
                {'t': 'Hay alguien que me aconseja en momentos de crisis.', 'd': 'Apoyo Informacional'},
                {'t': 'Hay alguien que entiende mis problemas.', 'd': 'Apoyo Emocional'},
                {'t': 'Hay alguien a quien puedo recurrir cuando necesito ayuda práctica.', 'd': 'Apoyo Instrumental'},
            ]
        )

        self._seed(
            name='Fortalezas Prosociales y Comunicación',
            dimension='comunidad',
            description='Evalúa tu estilo de comunicación y tus fortalezas en la relación con otros. La asertividad es la capacidad de honrar tu verdad sin deshonrar la del otro. La sombra es la comunicación reactiva; la luz es la comunicación consciente.',
            estimated_minutes=5,
            order=81,
            questions_data=[
                {'t': 'Puedo expresar mis opiniones con claridad sin agredir a los demás.', 'd': 'Asertividad'},
                {'t': 'Escucho activamente a los demás antes de responder.', 'd': 'Escucha Activa'},
                {'t': 'Busco entender el punto de vista del otro antes de defender el mío.', 'd': 'Empatía'},
                {'t': 'Cuando hay un conflicto, busco soluciones que satisfagan a ambas partes.', 'd': 'Resolución Colaborativa'},
                {'t': 'Me cuesta decir "no" aunque quiera hacerlo.', 'd': 'Asertividad', 'r': True},
                {'t': 'Expreso mis emociones de forma clara y apropiada.', 'd': 'Expresión Emocional'},
            ]
        )

        # ─── ABUNDANCIA Y FINANZAS ───

        self._seed(
            name='MAQ — Actitudes hacia el Dinero',
            dimension='abundancia',
            description='Tu relación con el dinero es un espejo de tu relación con la energía y la vida. La abundancia no es acumulación — es flujo. Identificar tus arquetipos financieros te permite dejar de usar el dinero como mecanismo de defensa.',
            estimated_minutes=5,
            order=90,
            questions_data=[
                {'t': 'El dinero es sucio o corrupto en su naturaleza.', 'd': 'Creencias Limitantes'},
                {'t': 'Las personas ricas son generalmente codiciosas o deshonestas.', 'd': 'Creencias Limitantes'},
                {'t': 'Me siento cómodo/a recibiendo dinero y reconocimiento por mi trabajo.', 'd': 'Merecimiento'},
                {'t': 'Tengo claro cuánto dinero necesito y cuánto quiero ganar.', 'd': 'Claridad Financiera'},
                {'t': 'El dinero que gano fluye hacia cosas que importan para mí.', 'd': 'Flujo'},
                {'t': 'El miedo a quedarme sin dinero toma muchas de mis decisiones.', 'd': 'Mentalidad de Escasez'},
            ]
        )

        self._seed(
            name='FSS — Estrés Financiero',
            dimension='abundancia',
            description='Mide el impacto del estrés financiero en tu bienestar. Las finanzas estresadas revelan la relación con la abundancia, el merecimiento y el control. La luz es la conciencia financiera; la sombra es el piloto automático económico.',
            estimated_minutes=4,
            order=91,
            questions_data=[
                {'t': 'Me preocupo frecuentemente por si tendré suficiente dinero para cubrir mis gastos.', 'd': 'Estrés Financiero'},
                {'t': 'Las preocupaciones financieras afectan mi sueño o mi concentración.', 'd': 'Estrés Financiero'},
                {'t': 'Siento que tengo el control de mi situación financiera.', 'd': 'Control Percibido', 'r': True},
                {'t': 'Me resulta difícil ahorrar aunque quiera hacerlo.', 'd': 'Conducta Financiera'},
                {'t': 'Gasto impulsivamente para sentirme mejor emocionalmente.', 'd': 'Conducta Financiera'},
            ]
        )

        # ─── CREATIVIDAD E INTEGRACIÓN ───

        self._seed(
            name='Identidad Creativa (CIQ)',
            dimension='creatividad',
            description='Evalúa cómo te identificas con tu propia creatividad. La creatividad no es una habilidad — es una forma de ver. La sombra creativa es creer que no eres creativo/a; la luz es reconocerte como co-creador/a de tu realidad.',
            estimated_minutes=5,
            order=100,
            questions_data=[
                {'t': 'Me considero una persona creativa.', 'd': 'Identidad Creativa'},
                {'t': 'Encuentro formas originales de abordar los problemas cotidianos.', 'd': 'Creatividad Aplicada'},
                {'t': 'Me resulta natural generar nuevas ideas cuando me enfrento a un desafío.', 'd': 'Creatividad Aplicada'},
                {'t': 'Siento que mi vida misma es una expresión creativa.', 'd': 'Identidad Creativa'},
                {'t': 'Me bloqueo fácilmente cuando intento crear algo nuevo.', 'd': 'Bloqueo Creativo', 'r': True},
                {'t': 'Tengo miedo de que mis ideas sean juzgadas negativamente.', 'd': 'Bloqueo Creativo', 'r': True},
            ]
        )

        self._seed(
            name='Rueda de la Vida — Integración',
            dimension='creatividad',
            description='Evalúa el grado de satisfacción y equilibrio en las áreas fundamentales de tu vida. La integración no es perfección en todas las áreas — es la capacidad de moverte conscientemente entre ellas según lo que necesitas en cada momento.',
            estimated_minutes=6,
            order=101,
            questions_data=[
                {'t': '¿Qué tan satisfecho/a estás con tu salud y bienestar físico?', 'd': 'Salud'},
                {'t': '¿Qué tan satisfecho/a estás con tus relaciones íntimas y de pareja?', 'd': 'Relaciones'},
                {'t': '¿Qué tan satisfecho/a estás con tus relaciones familiares?', 'd': 'Familia'},
                {'t': '¿Qué tan satisfecho/a estás con tus amistades y vida social?', 'd': 'Amistades'},
                {'t': '¿Qué tan satisfecho/a estás con tu trabajo o carrera profesional?', 'd': 'Trabajo'},
                {'t': '¿Qué tan satisfecho/a estás con tu situación económica?', 'd': 'Finanzas'},
                {'t': '¿Qué tan satisfecho/a estás con tu crecimiento personal y aprendizaje?', 'd': 'Desarrollo Personal'},
                {'t': '¿Qué tan satisfecho/a estás con tu vida espiritual o sentido de propósito?', 'd': 'Espiritualidad'},
            ]
        )

        self._seed(
            name='SOC-29 — Sentido de Coherencia',
            dimension='creatividad',
            description='El Sentido de Coherencia de Antonovsky mide la capacidad de ver la vida como comprensible, manejable y significativa. Es lo que permite navegar el caos sin perder el centro. La sombra es el sin-sentido; la luz es la coherencia interna.',
            estimated_minutes=6,
            order=102,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Cuando algo inesperado ocurre, generalmente creo que encontraré la manera de manejarlo.', 'd': 'Manejabilidad', 'scale': 'likert7'},
                {'t': 'La vida tiene muy poco sentido para mí.', 'd': 'Significatividad', 'scale': 'likert7', 'r': True},
                {'t': 'Entiendo lo que me pasa en la vida.', 'd': 'Comprensibilidad', 'scale': 'likert7'},
                {'t': 'Tengo la sensación de que la vida es injusta.', 'd': 'Significatividad', 'scale': 'likert7', 'r': True},
                {'t': 'Tengo los recursos para manejar lo que la vida me exige.', 'd': 'Manejabilidad', 'scale': 'likert7'},
                {'t': 'Siento que lo que hago en la vida tiene sentido.', 'd': 'Significatividad', 'scale': 'likert7'},
                {'t': 'Las cosas que me pasan tienen una causa comprensible.', 'd': 'Comprensibilidad', 'scale': 'likert7'},
            ]
        )

        # ─── MENTE Y APRENDIZAJE ───

        self._seed(
            name='Kolb — Estilos de Aprendizaje',
            dimension='mente',
            description='Los 4 estilos de aprendizaje experiencial: Acomodador, Divergente, Asimilador, Convergente. Aprender a aprender es la habilidad maestra. Tu estilo te dice cómo procesas mejor la realidad — úsalo como fortaleza y entrena los otros.',
            estimated_minutes=5,
            order=110,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Aprendo mejor cuando puedo intentar las cosas directamente y experimentar.', 'd': 'Experiencia Concreta'},
                {'t': 'Me gusta reflexionar y observar desde distintos ángulos antes de actuar.', 'd': 'Observación Reflexiva'},
                {'t': 'Aprendo mejor cuando puedo crear modelos o teorías que expliquen los datos.', 'd': 'Conceptualización Abstracta'},
                {'t': 'Aprendo mejor cuando puedo aplicar lo aprendido a problemas prácticos.', 'd': 'Experimentación Activa'},
                {'t': 'Prefiero la acción a la reflexión cuando enfrento situaciones nuevas.', 'd': 'Experiencia Concreta'},
                {'t': 'Me gusta observar las reacciones de los demás antes de tomar decisiones.', 'd': 'Observación Reflexiva'},
            ]
        )

        self._seed(
            name='CEQ — Curiosidad Epistémica',
            dimension='mente',
            description='Mide el deseo de exploración intelectual y la tolerancia a la ambigüedad. La curiosidad es el motor de la expansión. La sombra es la certeza prematura; la luz es la capacidad de habitar la pregunta sin apuro de respuesta.',
            estimated_minutes=4,
            order=111,
            instrument_type='adapted',
            questions_data=[
                {'t': 'Disfruto aprendiendo cosas nuevas incluso cuando no tienen aplicación práctica inmediata.', 'd': 'Curiosidad Epistémica'},
                {'t': 'Me fascina explorar ideas que desafían mi forma de pensar actual.', 'd': 'Curiosidad Epistémica'},
                {'t': 'Me siento incómodo/a con las preguntas que no tienen respuesta clara.', 'd': 'Tolerancia a la Ambigüedad', 'r': True},
                {'t': 'Busco activamente información que contradiga mis creencias para ponerlas a prueba.', 'd': 'Pensamiento Crítico'},
                {'t': 'Disfruto de las conversaciones filosóficas y abstractas.', 'd': 'Curiosidad Epistémica'},
            ]
        )

        self.stdout.write(f'\n  Total: {Test.objects.count()} tests cargados.')
