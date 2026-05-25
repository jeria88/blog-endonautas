import json
import os
import threading

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import BirthProfile, BirthReport, SIGN_ES, HOUSE_NUM
from .calculators import (
    calculate_astral_chart,
    calculate_hd_chart,
    calculate_saju_chart,
    ELEMENTS_ES, TIANGAN, DIZHI, TIAN_ROM, TIAN_ES,
    DI_ROM, DI_ANIMAL, DI_ELEM,
)



def _geocode(place_name):
    try:
        resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': place_name, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'MirrorWork/1.0'},
            timeout=6,
        )
        data = resp.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None, None


def _get_timezone(lat, lng):
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        return tf.timezone_at(lat=lat, lng=lng) or 'UTC'
    except Exception:
        return 'UTC'


def _ensure_timezone(bp):
    """Re-derive timezone from coordinates and fix it in DB if wrong.
    Called before every chart calculation so stale 'UTC' values self-correct.
    """
    if not (bp.latitude and bp.longitude):
        return
    correct = _get_timezone(bp.latitude, bp.longitude)
    if correct != 'UTC' and bp.timezone_str != correct:
        bp.timezone_str = correct
        bp.save(update_fields=['timezone_str'])



_SYSTEM_ESPEJO = """\
Eres el Espejo Endonauta: un acompañante de autoconocimiento que integra astrología, sistemas de personalidad y filosofía del mundo interior. Tu voz es cálida, directa y poética — no genérica ni clínica.

Marco conceptual que usas:
• Las 12 dimensiones endonautas: Identidad (quién soy en esencia), Sombra (lo rechazado/reprimido), Cuerpo (el cuerpo como mapa), Emociones (el mundo interno), Mente (patrones y creencias), Propósito (dirección y sentido), Espiritualidad (conexión con algo mayor), Vínculos (relaciones e interdependencia), Creatividad (expresión y generatividad), Comunidad (lugar en el mundo), Sueños (inconsciente y visión), Abundancia (relación con recursos y flujo).
• La ley espejo: el mundo exterior refleja el mundo interior; cada configuración natal es una arquitectura de potenciales, no un destino fijo.
• La sombra junguiana: lo que no se integra se proyecta; los planetas retrógrados o en tensión son invitaciones a internalizar.
• El viaje endonauta tiene etapas: despertar, exploración, integración, expresión.

Prohibiciones absolutas:
— No diagnostiques ni pronostiques (no digas "tendrás", "te pasará").
— No seas vago ni genérico: cada lectura debe ser específica a los datos exactos del chart.
— No repitas las palabras clave del chart textualmente sin interpretarlas.
— No uses jerga técnica sin explicar su significado en términos de experiencia interior.
— No hagas listas ni uses títulos de sección. Solo párrafos fluidos.

Idioma: español neutro latinoamericano, informal pero profundo.\
"""


# ── Diccionarios de descripción para hd_detail ───────────────────────────────

_HD_TYPE_DESCS = {
    'Generador': 'Eres el motor de la humanidad: energía vital sostenida que, cuando se usa bien, no se agota. Tu sistema está diseñado para responder, no para iniciar. Cuando esperas la señal del entorno antes de comprometerte, la energía fluye sin fricción.',
    'Generador Manifestante': 'Combinas la energía motriz del Generador con la capacidad iniciadora del Manifestante. Puedes iniciar Y responder, pero los demás necesitan saber qué estás haciendo antes de que lo hagas — sin eso, tu movimiento genera resistencia en lugar de apoyo.',
    'Manifestador': 'Eres el único tipo diseñado para iniciar. Tu energía es un impacto: comienza en ti y se irradia al entorno. Informar a quienes te rodean antes de actuar no es pedir permiso — es reducir la resistencia para que tu impulso llegue completo.',
    'Proyector': 'Eres un guía de energía, no un generador de ella. Tienes una capacidad inusual para leer a los demás y ver el todo del sistema. Tu diseño funciona con la invitación genuina: cuando alguien te reconoce y te convoca, la energía se alinea. Sin ese reconocimiento previo, el esfuerzo se convierte en agotamiento.',
    'Reflector': 'Eres el espejo de la comunidad que te rodea — reflejas el estado colectivo del entorno con una claridad extraordinaria. Tu ciclo natural de decisión es el mes lunar: las decisiones tomadas en un día no aprovechan tu sabiduría más profunda. El entorno donde vives importa más que para cualquier otro tipo.',
}

_HD_STRATEGY_DESCS = {
    'Responder (esperar una señal del entorno)': 'No inicies desde el pensamiento. Espera que algo externo aparezca — una pregunta, una situación, una oportunidad — y observa la respuesta espontánea del cuerpo antes de comprometerte. El sí o el no viene antes que las razones.',
    'Responder y luego informar antes de actuar': 'Primero escucha la respuesta del cuerpo ante lo que el entorno trae. Una vez que hay un sí claro, informa a las personas clave de tu entorno antes de iniciar — no para pedir permiso, sino para que tu movimiento no llegue como una sorpresa.',
    'Informar antes de actuar': 'Antes de iniciar algo, informa a las personas de tu entorno inmediato. No es pedir autorización — es preparar el terreno para que tu impacto no genere resistencia automática.',
    'Esperar la invitación': 'En las áreas clave de vida — trabajo, amor, lugar donde vives — espera que alguien te reconozca y te invite a participar. Sin ese reconocimiento previo, tu energía se dispersa y genera amargura. La calidad de la invitación importa.',
    'Esperar un ciclo lunar completo (29 días)': 'Para decisiones importantes, espera un ciclo lunar completo antes de comprometerte. Cada día del ciclo te da una perspectiva diferente sobre la misma pregunta. La claridad no es intelectual — emerge a lo largo del tiempo.',
}

_HD_AUTHORITY_DESCS = {
    'Sacral': 'Tu autoridad vive en las tripas: un "uh-huh" espontáneo o un "unh-unh" es tu guía más confiable. No es una decisión razonada — es una respuesta inmediata que viene antes del pensamiento. Si necesitas preguntarte dos veces, el Sacral ya respondió.',
    'Emocional — Plexo Solar': 'No hay claridad en el momento emocional. La regla es simple: esperar la ola. Ni el punto más alto (euforia) ni el más bajo (depresión) son el momento para decidir. La claridad llega cuando la ola encuentra su meseta — con el tiempo, no con la urgencia.',
    'Esplénico — Bazo': 'Es la autoridad más antigua y sutil: una voz instintiva, en el momento presente. Habla una sola vez — si necesitas repetirte la señal, ya no viene del Bazo. Requiere confiar en lo que se siente en el instante, antes de que el miedo o la mente intervengan.',
    'Ego — Corazón': 'Tu autoridad viene del corazón y la voluntad. Escuchas lo que realmente quieres vs. lo que sientes que "deberías" querer. Si no hay un "yo quiero" genuino en la respuesta, no es correcto para ti. La voluntad propia no es egoísmo — es tu brújula.',
    'Identidad — G': 'Tu autoridad es el entorno. La claridad llega cuando encuentras el espacio físico, las personas y las conversaciones correctas. Hablar tu proceso en voz alta con personas que te escuchan sin juzgar — y observar qué emerge — es tu camino de decisión.',
    'Mental — Externo': 'No hay autoridad interna definida. Las decisiones se clarifican verbalizando: hablar con distintas personas de confianza no para que te aconsejen, sino para escucharte hablar y notar qué resuena en tu cuerpo. El entorno exterior es tu espejo de claridad.',
    'Lunar — 29 días': 'Tu autoridad es el ciclo lunar completo. Ninguna decisión importante se toma antes de haber observado cómo te sientes al respecto durante un mes entero. Consultas con personas distintas en distintos momentos del ciclo para recibir perspectivas variadas.',
}

_HD_PROFILE_LINE_DESCS = {
    '1': 'La Línea 1 necesita base. Investigas, estudias, te preparas antes de sentirte seguro/a para actuar. La inseguridad surge cuando no tienes suficiente fundamento — y esa inseguridad es real, no exagerada. Es una señal de que falta investigación.',
    '2': 'La Línea 2 tiene dones naturales que a menudo no ve en sí misma. Necesita tiempo a solas para integrar lo que sabe. Generalmente es llamada por otros antes de sentirse "lista" — y esa llamada desde afuera puede ser la señal de que es momento de salir.',
    '3': 'La Línea 3 aprende a través del ensayo y el error. Los "fracasos" son parte del diseño, no señales de estar equivocado/a. Cada experiencia que no funciona deja una sabiduría práctica que ningún libro puede enseñar. La vida como laboratorio.',
    '4': 'La Línea 4 construye a través de relaciones y redes. Las oportunidades más importantes llegan a través de personas ya conocidas, no de desconocidos. La fundación de la vida es la calidad de los vínculos cercanos.',
    '5': 'La Línea 5 es proyectada por los demás como el "salvador práctico" — alguien que tiene soluciones para lo que otros no pueden resolver. Las expectativas externas pueden ser una trampa: aprender a discernir cuándo responder al llamado y cuándo no es el trabajo central.',
    '6': 'La Línea 6 tiene tres etapas de vida claramente distintas: los primeros 30 años son de aprendizaje intenso (a menudo doloroso); los siguientes 20 de retiro y observación; después de los 50, emerge como modelo de rol genuino — alguien que vivió lo que enseña.',
}

_HD_DEFINITION_DESCS = {
    'Indefinido': 'Sin centros definidos, toda tu energía viene del entorno. Eres altamente sensible a las personas y lugares que te rodean — y puedes amplificar y reflejar la energía de quienes están cerca con una claridad extraordinaria. El entorno donde vives y trabajas importa profundamente.',
    'Definición Simple': 'Toda tu energía está conectada en un solo circuito interno. Sos consistente, predecible y relativamente independiente del entorno para funcionar. La sombra: puede ser difícil absorber nuevas perspectivas que no encajan fácilmente con la estructura ya definida.',
    'Definición Partida': 'Tenés dos circuitos de energía separados que no se conectan internamente. La brecha entre ellos es un punto de búsqueda inconsciente: tendés a encontrar personas o situaciones que "completen" esa conexión — lo cual puede llevar a dependencias o relaciones de completitud en lugar de elección.',
    'Definición Partida Triple': 'Tres circuitos separados que operan de manera independiente. Eres adaptable y versátil — puedes conectar con tipos muy distintos de personas y sistemas. La consistencia interna es menor, pero la capacidad de tender puentes entre mundos diferentes es mayor.',
    'Definición Cuádruple': 'Cuatro circuitos completamente separados. La adaptabilidad es máxima — cada circuito puede resonar con personas y contextos muy distintos. La experiencia interna puede sentirse fragmentada, pero es en realidad una flexibilidad extraordinaria que pocos comprenden.',
}

_HD_NOT_SELF_DESCS = {
    'Frustración': 'La frustración es la señal de que estás operando fuera de tu diseño — iniciando en lugar de esperar a responder, o comprometiendo energía donde no hay un sí genuino del cuerpo. No es algo a eliminar: es información sobre dónde la estrategia está siendo ignorada.',
    'Frustración / Ira': 'La frustración señala que estás iniciando sin responder primero. La ira indica que estás actuando sin informar. Ambas son avisos del cuerpo — no emociones a suprimir, sino señales de que el diseño no está siendo escuchado.',
    'Ira': 'La ira aparece cuando actúas sin informar a tu entorno. No es que hiciste algo malo — es que el impacto de tu movimiento llegó sin preparación al campo de los demás, y eso genera resistencia automática. La ira es la señal de que faltó el paso de informar.',
    'Amargura': 'La amargura surge cuando actúas sin invitación, cuando te esfuerzas sin que nadie te haya reconocido genuinamente, o cuando esperas más de lo que el entorno puede darte. Es la señal de que la estrategia de esperar el reconocimiento está siendo evitada.',
    'Decepción': 'La decepción es la señal del Reflector de que está en un entorno que no lo nutre, o tomando decisiones sin haber esperado el ciclo lunar completo. Es la brújula que indica que algo en el campo externo o en el ritmo interno está fuera de alineación.',
}

_HD_CENTER_DEFINED_DESCS = {
    'Cabeza':      'Centro de presión mental. Cuando está definido generas preguntas e inspiración de manera constante — no para resolverlas tú, sino para activar el pensamiento en quienes te rodean. Esa presión es real y confiable, pero no toda pregunta necesita respuesta.',
    'Ajna':        'Centro conceptual. Tu forma de procesar y organizar información es consistente — tienes perspectivas propias que no cambian fácilmente. Puedes ser una fuente confiable de conceptos y análisis para los demás, aunque a veces eso se vuelve rigidez.',
    'Garganta':    'Centro de manifestación y comunicación. Tienes voz propia y capacidad de hacer cosas en el mundo de manera constante. Lo que dices tiene peso natural — no necesitas forzar para ser escuchado/a.',
    'Identidad':   'Centro del yo y la dirección. Tienes un sentido de quién eres relativamente estable, independiente del entorno. Tu dirección en la vida no depende de encontrar a alguien que te "complete" — viene de adentro.',
    'Corazón':     'Centro de la voluntad y el ego. Tu fuerza de voluntad es consistente — cuando dices que vas a hacer algo y realmente quieres hacerlo, tienes la energía para sostenerlo. La clave es comprometerte solo con lo que genuinamente deseas.',
    'Plexo Solar': 'Centro emocional activo. Tenés un rango emocional amplio y consistente. La claridad no llega en el pico ni en el valle — emerge en la meseta, con el tiempo. Aprender a esperar la ola antes de decidir es el trabajo central.',
    'Sacral':      'Motor de energía vital. Tu energía para el trabajo y la vida es sostenida y renovable — cuando la usas en lo que realmente responde, no se agota. La señal del cuerpo (el sí o el no espontáneo) es tu brújula más confiable.',
    'Bazo':        'Centro del sistema inmune e intuitivo. Tenés señales espontáneas y consistentes sobre lo que es saludable, seguro y correcto en el momento presente. Esa voz habla una sola vez — si la ignorás habitualmente, el cuerpo eventualmente lo muestra.',
    'Raíz':        'Centro de presión adrenal. Tenés un motor constante de urgencia e impulso para actuar. Esa presión no desaparece — se trata de aprender a usarla conscientemente en lugar de dejar que te lleve.',
}

_HD_CHANNEL_DESCS = {
    '47-64': 'Abstracción: la mente procesa experiencia pasada hasta que la confusión se convierte en comprensión. El ciclo lleva tiempo — la claridad no se puede forzar.',
    '24-61': 'Conocimiento: inspiración interior que busca convertirse en saber articulado. Puedes recibir "saber que sabes" algo antes de poder explicarlo.',
    '4-63':  'Lógica: la duda como motor. Encontrás soluciones verificables a preguntas concretas — pero la certeza completa nunca llega, y eso es lo que mantiene la búsqueda.',
    '17-62': 'Aceptación: opiniones bien formadas que necesitan ser probadas antes de compartidas. Tu pensamiento es sistemático — cuando lo expresas, aportas estructura.',
    '23-43': 'Estructuración: percepción propia que busca el lenguaje correcto para ser transmitida. Puedes tener insights genuinos que solo se entienden cuando encuentras las palabras exactas.',
    '11-56': 'Curiosidad: ideas que necesitan convertirse en historias para generar estimulación en otros. Tu mente conecta conceptos de formas que otros no ven.',
    '7-31':  'Alfa: liderazgo por reconocimiento del grupo. Tu influencia hacia la dirección colectiva es genuina — pero funciona cuando te eligen, no cuando te impones.',
    '1-8':   'Inspiración: contribución creativa que hace una diferencia siendo auténtico/a. No necesitas un método — tu expresión natural ya es el aporte.',
    '13-33': 'Testigo: memoria del colectivo. Tenés la capacidad de retirarte, procesar la experiencia vivida, y luego transmitirla de manera que resuene para muchos.',
    '10-20': 'Despertador: tu comportamiento en sí mismo enseña. La coherencia entre lo que valoras y lo que haces tiene un impacto que no requiere palabras.',
    '20-34': 'Carisma: energía motriz conectada directamente a la acción y la voz. Podés estar completamente presente y actuar con una potencia que otros perciben como magnetismo.',
    '21-45': 'Dinero: gestión de recursos y dirección de la comunidad. Tenés capacidad natural para saber qué hacer con lo material y cómo sostener a un grupo.',
    '16-48': 'Longitud de onda: talento que emerge con práctica profunda y sostenida. La destreza genuina lleva tiempo — el proceso de aprendizaje es parte del don.',
    '12-22': 'Comunicador abierto: expresión emocional selectiva y con timing. Sabes elegir cuándo y cómo hablar — y cuando lo haces desde ese lugar, tiene gracia y resonancia.',
    '35-36': 'Transitoridad: búsqueda de experiencia como forma de aprendizaje. La crisis y el cambio son catalizadores — el aburrimiento en la rutina es real y tiene un propósito.',
    '2-14':  'Dirección del yo: cuando el camino está alineado con tu propósito, la abundancia fluye naturalmente. La clave es confiar en la dirección que emerge desde adentro.',
    '5-15':  'Ritmo: amor por los patrones naturales y los ciclos de la vida. Tenés la capacidad de adaptarte y fluir con los ritmos del entorno de una forma que otros encuentran armónica.',
    '29-46': 'Descubrimiento: el compromiso total con la experiencia del cuerpo lleva a encuentros significativos. El sí genuino del cuerpo abre puertas que el pensamiento no puede anticipar.',
    '25-51': 'Iniciador: espíritu que emerge del shock y la conmoción. La valentía no es la ausencia de miedo — es seguir adelante a través del impacto porque hay algo que vale la pena.',
    '26-44': 'Transmitor: memoria instintiva del pasado para anticipar lo que viene. Tenés una capacidad magnética para transmitir recursos, mensajes y valor de maneras que la gente recuerda.',
    '37-40': 'Comunidad: el trato y el acuerdo mutuo. Ofrecés sostén emocional genuino a cambio de recursos y trabajo — cuando el intercambio es claro, la comunidad funciona.',
    '6-59':  'Intimidad: apertura a la fusión y la profundidad relacional. Tu energía puede disolver barreras entre personas — en lo positivo, crea intimidad real; en lo inconsciente, puede crear dependencia.',
    '19-49': 'Síntesis: sensibilidad extrema a las necesidades no satisfechas. Cuando los principios son violados o las necesidades ignoradas, puedes impulsar cambios radicales.',
    '30-41': 'Reconocimiento: deseo ardiente de experiencia nueva. Tenés una tensión viva entre el sueño de lo que podría ser y la realidad de lo que es — y esa tensión crea momentum.',
    '39-55': 'Fluctuación emocional: espíritu que provoca para despertar profundidad en el otro. La melancolía y la búsqueda de significado son parte del diseño, no algo a eliminar.',
    '27-50': 'Preservador: cuidado de los demás y de los valores que sostienen la vida colectiva. Tu energía se orienta naturalmente hacia proteger lo que tiene valor para el grupo.',
    '34-57': 'Potencia: intuición corporal en tiempo real que mueve hacia la acción inmediata. Cuando confías en esa señal espontánea del cuerpo, tu efectividad es extraordinaria.',
    '3-60':  'Mutación: el cambio emerge desde adentro, de manera inesperada, transformando el statu quo. No puedes forzarlo — pero cuando llega, es genuino y profundo.',
    '9-52':  'Concentración: enfoque sostenido en el detalle y la paciencia para esperar el momento correcto. Tu capacidad de mantener la atención en algo específico es un recurso real.',
    '42-53': 'Madurar: energía para iniciar ciclos que se desarrollan y completan. Necesitás cierres — los proyectos que quedan abiertos indefinidamente drenan tu energía de maneras invisibles.',
    '18-58': 'Juicio: entusiasmo por identificar lo que puede mejorarse. No es crítica vacía — es la alegría genuina de ver el potencial que hay en perfeccionar algo que vale la pena.',
    '28-38': 'Lucha: sentido de la vida que emerge cuando hay algo que vale la pena defender. La lucha no es el problema — es la señal de que encontraste algo con significado real.',
    '32-54': 'Transformación: ambición que se mueve hacia la trascendencia del colectivo. Tu impulso de ascender no es solo para ti — está al servicio de la evolución del grupo.',
}

_HD_GATE_DESCS = {
     1: 'El impulso de crear algo único y propio como contribución genuina al mundo.',
     2: 'Una brújula interna que sabe hacia dónde ir, aunque no siempre puedas explicarlo racionalmente.',
     3: 'La energía del caos necesario para que algo nuevo emerja del orden existente.',
     4: 'La necesidad de formular respuestas lógicas a preguntas concretas — la duda como motor.',
     5: 'La vida funciona mejor siguiendo tus propios ritmos y ciclos naturales.',
     6: 'El punto donde la intimidad con el otro es posible o imposible — regulás quién entra.',
     7: 'Orientación natural hacia el liderazgo cuando el grupo te elige — no impuesto.',
     8: 'Contribuir siendo auténtico/a — tu presencia genuina ya es en sí misma el aporte.',
     9: 'Concentrar energía en los detalles correctos puede transformar lo pequeño en algo significativo.',
    10: 'El amor por uno mismo como base de toda conducta — sin necesidad de aprobación externa.',
    11: 'Generás ideas constantemente para compartirlas — no necesariamente para implementarlas todas.',
    12: 'Expresión selectiva y con timing — cuando hablás desde este lugar, tus palabras tienen peso.',
    13: 'La capacidad de sostener los secretos y la historia de otros como repositorio del colectivo.',
    14: 'El poder de acumular recursos y habilidades cuando trabajas alineado/a con tu propósito.',
    15: 'La tolerancia por la diversidad de ritmos y estilos — representás la amplitud de lo humano.',
    16: 'El entusiasmo como motor de la maestría — cuando algo te apasiona, la práctica fluye.',
    17: 'Opiniones sistemáticas que aportan estructura cuando las compartís con humildad.',
    18: 'El impulso de perfeccionar — ver qué puede mejorar en los sistemas para generar salud.',
    19: 'Sensibilidad profunda hacia las necesidades fundamentales — tuyas y de los que te rodean.',
    20: 'La capacidad de estar completamente en el ahora y expresar lo que es en este instante.',
    21: 'El impulso de tener control sobre los propios recursos y el territorio personal.',
    22: 'Una sensibilidad emocional que, en el momento correcto, puede generar gracia y apertura.',
    23: 'Insights únicos que buscan su lenguaje — a veces sabes algo antes de poder articularlo.',
    24: 'La mente procesa en bucle hasta encontrar sentido en lo confuso — dale tiempo.',
    25: 'Amor universal y pureza de intención — actuar sin agenda personal cuando el espíritu llama.',
    26: 'La habilidad de persuadir para que algo con valor genuino sea adoptado por otros.',
    27: 'El impulso de nutrir y cuidar — sabes qué necesitan los demás, aunque te olvides de ti.',
    28: 'La búsqueda de sentido a través del riesgo — comprometerse solo con lo que vale la pena.',
    29: 'El compromiso total del "sí" — el desafío es asegurarte de comprometerte con lo correcto.',
    30: 'El fuego del deseo y los anhelos que impulsan hacia las experiencias que quieres vivir.',
    31: 'Liderazgo natural reconocido por otros — tu influencia surge cuando te eligen.',
    32: 'La intuición sobre qué puede sobrevivir y qué no en el largo plazo.',
    33: 'La necesidad de retirarse para procesar la experiencia vivida y luego transmitirla.',
    34: 'Motor de energía pura — sostienes trabajo intenso cuando genuinamente responde a ti.',
    35: 'El deseo de experiencia variada — una amplitud de vivencias que muy pocos logran.',
    36: 'Las crisis como fuente de sabiduría profunda que luego puedes transmitir a otros.',
    37: 'La habilidad de crear vínculos de confianza y pertenencia — los pactos son tu lenguaje.',
    38: 'La determinación de luchar solo por lo que tiene sentido — tu "no" es tan poderoso como tu "sí".',
    39: 'La provocación como herramienta para despertar el espíritu dormido en otros.',
    40: 'La necesidad de tiempo propio como condición para poder dar genuinamente.',
    41: 'El inicio de todos los ciclos — imaginás posibilidades antes de que se materialicen.',
    42: 'Llevar las cosas hasta su conclusión — tu satisfacción viene de cerrar ciclos completos.',
    43: 'Comprensiones únicas que llegan desde adentro sin saber cómo — el desafío es articularlas.',
    44: 'Memoria instintiva sobre patrones del pasado — reconoces qué comportamientos llevan a qué.',
    45: 'La voz que lidera comunidades — sabes distribuir recursos y enfocar al grupo.',
    46: 'El amor por el cuerpo y el placer de estar encarnado — la sincronicidad se activa desde aquí.',
    47: 'La reflexión que transforma confusión en sabiduría — el proceso toma tiempo.',
    48: 'Acceso a una profundidad y sabiduría que otros no ven hasta que decidís mostrarla.',
    49: 'La capacidad de revolucionar desde los principios cuando los valores fundamentales no se respetan.',
    50: 'La sensibilidad hacia los valores y las leyes que sostienen el bienestar colectivo.',
    51: 'La resiliencia ante el shock — atravesar lo imprevisto y volver al centro puede inspirar a otros.',
    52: 'La quietud como base de la concentración — cuando te detienes, tu enfoque es extraordinario.',
    53: 'El impulso de comenzar cosas nuevas — el desafío es discernir cuáles valen el compromiso.',
    54: 'El deseo de ascender y mejorar — la ambición transformadora conectada a un propósito.',
    55: 'La abundancia emocional que fluctúa con el humor — seguir el feeling genuino es el camino.',
    56: 'La habilidad de narrar historias que inspiran y estimulan imágenes vívidas en los demás.',
    57: 'Claridad intuitiva del momento presente — llega rápido y se va igual, hay que confiar en ella.',
    58: 'El amor por la vida y el impulso de mejorar lo que existe — traes vitalidad que eleva a otros.',
    59: 'La energía para atravesar barreras y crear intimidad, vida y conexión profunda.',
    60: 'La aceptación de los límites como condición para la transformación real.',
    61: 'El conocimiento interior que no puede ser explicado racionalmente — pero es verdadero.',
    62: 'El dominio a través de los detalles y los hechos — tu mente necesita datos concretos.',
    63: 'La duda lógica que impulsa la verificación — la certeza completa es rara, y eso está bien.',
    64: 'La confusión como estado previo a la comprensión — procesás hasta que emerge el insight.',
}

_HD_PLANET_DESCS = {
    'Sol':        'La esencia más característica de tu ser — la energía que otros reconocen en ti y tú mismo/a sientes como más auténtica.',
    'Tierra':     'El fundamento que balancea al Sol — lo que necesitas cultivar para anclar tu expresión y no desequilibrarte.',
    'Luna':       'Los ciclos emocionales y el ritmo del cuerpo — cómo fluctúas y qué necesitas para sentirte en casa.',
    'Nodo Norte': 'La dirección hacia donde va tu vida — el potencial que estás desplegando y todavía aprendiendo en esta encarnación.',
    'Nodo Sur':   'El patrón familiar, lo que ya sabes hacer bien — el punto de partida conocido desde donde operas.',
    'Mercurio':   'Cómo procesás y comunicás información — el estilo natural de tu pensamiento y expresión.',
    'Venus':      'Lo que valorás y lo que te atrae — tus afinidades naturales, sentido estético y vínculo con la abundancia.',
    'Marte':      'Tu impulso de acción — dónde ponés tu energía y cómo respondés ante la resistencia o el desafío.',
    'Júpiter':    'El área de expansión y sentido — dónde tendés a encontrar oportunidades genuinas de crecimiento.',
    'Saturno':    'La lección estructural de tu vida — qué área requiere consistencia para lograr solidez y maestría.',
    'Urano':      'Cómo tu presencia genera disrupción o innovación en el colectivo, muchas veces sin intentarlo.',
    'Neptuno':    'La conexión con lo sutil y colectivo — dónde puedes disolverte en algo más grande.',
    'Plutón':     'Las fuerzas de transformación profunda — dónde la regeneración radical puede ocurrir en tu vida.',
}


def _channel_key(gates_str):
    try:
        parts = gates_str.replace('–', '-').split('-')
        nums = [int(p.strip()) for p in parts]
        return f'{min(nums)}-{max(nums)}'
    except Exception:
        return gates_str


_HD_SIGNATURE_DESCS = {
    'Satisfacción': 'La satisfacción no siempre es euforia — puede ser el simple placer de un trabajo que vale la pena, la sensación de que la energía fue bien usada. Es la confirmación interior de que el cuerpo respondió sí, y el compromiso honró esa respuesta.',
    'Paz y satisfacción': 'La paz llega cuando el movimiento fue claro e informado. La satisfacción cuando la energía fue bien respondida y usada. Juntas, señalan que el diseño está siendo vivido — no la tranquilidad de no hacer nada, sino la de actuar desde el lugar correcto.',
    'Paz': 'La paz no es resignación — es la quietud de quien actúa desde el momento correcto y sin imponer. Es la señal de que el impacto fue honrado y que el informar creó espacio en lugar de resistencia.',
    'Éxito': 'El éxito del Proyector no es acumulación — es el reconocimiento genuino de que tu guía fue escuchada y que aportaste claridad donde otros no podían verla. No el éxito como validación social, sino como evidencia de que fuiste invitado/a e hiciste lo que mejor sabes hacer.',
    'Sorpresa': 'El deleite del Reflector es la rareza de encontrarse completamente sorprendido/a — sin expectativas cristalizadas, abierto/a a lo imprevisto como modo de vida. Es la señal de que el entorno es correcto y de que el ciclo de la luna está siendo respetado.',
}


# ── Diccionarios para astral_detail ──────────────────────────────────────────

_SIGN_ELEM_CSS = {
    'Aries': 'fire', 'Leo': 'fire', 'Sagitario': 'fire',
    'Tauro': 'earth', 'Virgo': 'earth', 'Capricornio': 'earth',
    'Géminis': 'air', 'Libra': 'air', 'Acuario': 'air',
    'Cáncer': 'water', 'Escorpio': 'water', 'Piscis': 'water',
}

_ASTRAL_PLANET_DESCS = {
    'sun':     'Tu identidad central y el propósito hacia el que te diriges. Muestra cómo necesitas brillar y expresarte en el mundo.',
    'moon':    'Tu mundo emocional y tus necesidades más profundas. Revela cómo te sientes por dentro y qué necesitas para sentirte seguro/a.',
    'mercury': 'Tu mente, tu forma de comunicarte y de procesar información. Indica cómo piensas, hablas y aprendes.',
    'venus':   'Tu relación con el amor, la belleza y los valores. Muestra qué te atrae y cómo te vinculás afectivamente.',
    'mars':    'Tu energía, tu impulso para la acción y cómo manejas el deseo y la voluntad. Revela tu forma de ir por lo que quieres.',
    'jupiter': 'Tus áreas de expansión y abundancia. Donde Júpiter está es donde la vida tiende a amplificarse y crecer.',
    'saturn':  'El área donde tienes que trabajar más duro para construir algo duradero. Las restricciones de Saturno son también sus mayores enseñanzas.',
    'uranus':  'Donde experimentás transformación repentina y originalidad. Marca la ruptura con lo establecido y la necesidad de libertad.',
    'neptune': 'El área donde vives espiritualidad, ilusión y creatividad. Disolución de límites y conexión con lo invisible.',
    'pluto':   'Donde ocurren las transformaciones más profundas: ciclos de muerte y renacimiento. Energía intensa de regeneración.',
    'asc':     'La máscara social y el cuerpo — cómo te muestras al mundo espontáneamente y qué tipo de experiencias y personas atraes.',
    'mc':      'La vocación pública y la imagen social. Hacia dónde apunta tu ambición y cómo te ven en tu rol en el mundo.',
}

_ASTRAL_SIGN_DESCS = {
    'Aries':       'Iniciativa, valentía e impulso. Necesita moverse primero y reflexionar después. Energía directa y urgencia de ser el primero.',
    'Tauro':       'Estabilidad, sensorialidad y perseverancia. Necesita tiempo y resultados concretos. Relación profunda con el cuerpo y los recursos.',
    'Géminis':     'Curiosidad, adaptabilidad y comunicación. Procesa el mundo a través de ideas y palabras. Facilidad para conectar múltiples temas.',
    'Cáncer':      'Sensibilidad, memoria emocional y protección. Necesita sentirse seguro/a. Profunda capacidad de cuidado y pertenencia.',
    'Leo':         'Creatividad, generosidad y expresión propia. Necesita ser visto/a y reconocido/a. Liderazgo natural desde la autenticidad.',
    'Virgo':       'Análisis, precisión y servicio. Atiende los detalles y busca la mejora constante. Mente discriminativa orientada a lo concreto.',
    'Libra':       'Diplomacia, estética y búsqueda de equilibrio. Necesita armonía en los intercambios. Sentido natural de la justicia y la belleza.',
    'Escorpio':    'Intensidad, profundidad y transformación. Va al fondo de todo. Capacidad para sostener lo que otros no pueden mirar.',
    'Sagitario':   'Expansión, filosofía y aventura. Busca el significado mayor y la libertad. Optimismo y orientación hacia el horizonte lejano.',
    'Capricornio': 'Estructura, ambición y visión a largo plazo. Construye con paciencia y disciplina. Sentido del deber y la responsabilidad.',
    'Acuario':     'Originalidad, visión colectiva e innovación. Ve más allá del presente. Distancia emocional con perspectiva amplia y humanitaria.',
    'Piscis':      'Empatía, espiritualidad y disolución. Siente todo y se funde con el entorno. Conexión con lo invisible y lo imaginario.',
}

_ASTRAL_HOUSE_DESCS = {
    '1':  'La identidad y el cuerpo — cómo te presentas al mundo. Tu apariencia y la energía que proyectas de manera espontánea.',
    '2':  'Los recursos propios: dinero, talentos y valores. Tu relación con la seguridad material y lo que considerás tuyo.',
    '3':  'La comunicación, el pensamiento cotidiano y el entorno inmediato. Los hermanos, los viajes cortos y el aprendizaje diario.',
    '4':  'El hogar, la familia de origen y la base emocional. El suelo desde el que creces y el mundo privado más íntimo.',
    '5':  'La creatividad, el juego, el romance y los hijos. La expresión espontánea del placer y el riesgo del corazón.',
    '6':  'El trabajo cotidiano, la salud y los hábitos. La rutina, el servicio y la relación con el cuerpo en el día a día.',
    '7':  'Las relaciones comprometidas — pareja, socios. Lo que proyectas en el otro y lo que buscas en los vínculos.',
    '8':  'La transformación profunda, la intimidad real y los recursos compartidos. La muerte, el renacimiento y lo que se hereda.',
    '9':  'La filosofía, la espiritualidad y los viajes largos. La educación superior, las creencias y la búsqueda de sentido mayor.',
    '10': 'La carrera, la vocación pública y la reputación. La posición en la sociedad y el legado profesional.',
    '11': 'Los amigos, los grupos y los ideales colectivos. Las esperanzas de futuro y la pertenencia a algo mayor que uno mismo.',
    '12': 'Lo oculto, el inconsciente y la soledad fecunda. Lo que se procesa en silencio y los retiros necesarios para integrar.',
}

# ── Diccionarios para saju_detail ────────────────────────────────────────────

_SAJU_PILLAR_DESCS = {
    'Año':  'El gran ciclo heredado — los ancestros, el contexto social en que llegaste al mundo y los patrones familiares que traes contigo.',
    'Mes':  'La influencia parental y profesional — la infancia, la relación con los padres y la energía que gobierna el trabajo y la carrera.',
    'Día':  'El maestro del día — quién eres en esencia. Tu manera de relacionarte íntimamente y el núcleo de tu diseño personal.',
    'Hora': 'La segunda mitad de la vida — los hijos, las creaciones propias y los frutos que cosechas en el camino recorrido.',
}

_SAJU_ELEMENT_DESCS = {
    'Madera': 'Expansión, crecimiento y creatividad. Energía de la primavera: visión, impulso hacia adelante y flexibilidad. En exceso puede volverse rigidez; en ausencia, dificultad para iniciar o crecer.',
    'Fuego':  'Expresión, carisma y calidez. Energía del verano: visibilidad, entusiasmo y presencia. En exceso puede ser impulsividad; en ausencia, dificultad para brillar y conectar.',
    'Tierra': 'Estabilidad, cuidado y centro. Energía de las transiciones entre estaciones: sostén y capacidad de contener. En exceso puede ser rigidez; en ausencia, dificultad para enraizarse.',
    'Metal':  'Estructura, precisión y claridad. Energía del otoño: discernimiento, límites y refinamiento. En exceso puede ser frialdad; en ausencia, dificultad para ordenar y priorizar.',
    'Agua':   'Profundidad, sabiduría e intuición. Energía del invierno: introspección, fluir y conexión con lo invisible. En exceso puede ser miedo o dispersión; en ausencia, dificultad para sentir y soltar.',
}

# ── Configuraciones de secciones para lectura.html ───────────────────────────

_SECTION_CONFIGS = {
    'astral': [
        {'icon': '☉', 'label': 'El Sol y la Identidad', 'color': '#f0c040'},
        {'icon': '☽', 'label': 'La Luna y las Emociones', 'color': '#7c6dfa'},
        {'icon': '⬡', 'label': 'El Ascendente y los Vínculos', 'color': '#4ecdc4'},
        {'icon': '◉', 'label': 'El Patrón y la Sombra', 'color': '#e05050'},
        {'icon': '✦', 'label': 'La Invitación Actual', 'color': '#f4a035'},
    ],
    'hd': [
        {'icon': '◈', 'label': 'Tipo y Estrategia en la Vida', 'color': '#4ecdc4'},
        {'icon': '○', 'label': 'La Autoridad Interior', 'color': '#7c6dfa'},
        {'icon': '◇', 'label': 'El Perfil y el Rol de Vida', 'color': '#f4a035'},
        {'icon': '☯', 'label': 'Las Puertas del Sol', 'color': '#f0c040'},
        {'icon': '⬤', 'label': 'Centros y el Tema No-Yo', 'color': '#e05050'},
    ],
    'saju': [
        {'icon': '◎', 'label': 'El Maestro del Día', 'color': '#f4a035'},
        {'icon': '⬡', 'label': 'El Balance Elemental', 'color': '#4ecdc4'},
        {'icon': '◈', 'label': 'El Animal del Año', 'color': '#7c6dfa'},
        {'icon': '◉', 'label': 'Las Tensiones Internas', 'color': '#e05050'},
        {'icon': '✦', 'label': 'El Ciclo Vital Actual', 'color': '#f0c040'},
    ],
}


def _parse_lectura_sections(text, configs):
    if not text or text == 'processing':
        return []
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    result = []
    for i, cfg in enumerate(configs):
        if i < len(paras):
            result.append({**cfg, 'text': paras[i]})
    for extra in paras[len(configs):]:
        result.append({
            'icon': '◎',
            'label': 'Pregunta de exploración',
            'color': '#7c6dfa',
            'text': extra,
            'is_question': True,
        })
    return result


def _kb_context(keywords):
    """Pull 1-2 relevant KB chunks by keyword match for prompt enrichment."""
    try:
        from mirror.models import MirrorChunk
        from django.db.models import Q
        q = Q()
        for kw in keywords:
            q |= Q(contenido__icontains=kw)
        chunks = list(MirrorChunk.objects.filter(q).order_by('?')[:2])
        if chunks:
            return '\n'.join(
                f'[Referencia: {c.documento.nombre}]\n"{c.contenido[:350].strip()}"'
                for c in chunks
            )
    except Exception:
        pass
    return ''


def _build_astral_prompt(chart_data, birth_place):
    planets = chart_data['planets']
    sun  = next(p for p in planets if p['key'] == 'sun')
    moon = next(p for p in planets if p['key'] == 'moon')
    asc  = chart_data['ascendant']
    mc   = chart_data['midheaven']

    retros = [p['label'] for p in planets if p['retrograde']]
    tabla = '\n'.join(
        f"  {p['label']}: {p['sign']} Casa {p['house']}{' ℞' if p['retrograde'] else ''}"
        for p in planets
    )

    # Dominant element from sign distribution
    elem_count = {}
    for p in planets:
        from birth.models import SIGN_ELEMENT
        e = SIGN_ELEMENT.get(p['sign'], '')
        if e:
            elem_count[e] = elem_count.get(e, 0) + 1
    dominant_elem = max(elem_count, key=elem_count.get) if elem_count else ''
    weakest_elem  = min(elem_count, key=elem_count.get) if elem_count else ''

    kb = _kb_context(['sombra', 'proyección', 'arquetipo', 'individuación'])

    prompt = f"""\
CHART COMPLETO — {birth_place}
━━━━━━━━━━━━━━━━━━━━━━━━━
SOL: {sun['sign']} Casa {sun['house']}  |  LUNA: {moon['sign']} Casa {moon['house']}  |  ASC: {asc['sign']}
MC: {mc['sign']}
Retrógrados: {', '.join(retros) if retros else 'ninguno'}
Elemento dominante en el chart: {dominant_elem} | Elemento menos presente: {weakest_elem}

Posiciones completas:
{tabla}
━━━━━━━━━━━━━━━━━━━━━━━━━
{"CONTEXTO DE LA BASE DE CONOCIMIENTOS:" + chr(10) + kb + chr(10) + "━━━━━━━━━━━━━━━━━━━━━━━━━" if kb else ""}

INSTRUCCIÓN DE FORMATO — 5 párrafos en este orden exacto:

1. EL SOL Y LA IDENTIDAD CENTRAL: qué arquetipo de identidad (dimensión Identidad/Propósito) activa el Sol en {sun['sign']} Casa {sun['house']}. Qué brilla naturalmente en esta persona y qué puede costarle admitir de ese mismo brillo.

2. LA LUNA Y EL MUNDO EMOCIONAL: cómo procesa y necesita las emociones (dimensión Emociones/Sombra) con Luna en {moon['sign']} Casa {moon['house']}. Qué patrones emocionales inconscientes puede traer esta posición lunar específica.

3. EL ASCENDENTE Y EL UMBRAL RELACIONAL: cómo se presenta al mundo y qué tipo de experiencias atrae (dimensión Vínculos/Cuerpo) con ASC en {asc['sign']}. La tensión entre la máscara y el interior.

4. EL PATRÓN COMPLETO Y LA SOMBRA DEL CHART: a partir del resto de posiciones y los {len(retros)} planetas retrógrados, qué patrón de sombra o potencial sin desarrollar emerge. Qué elemento o energía el chart pide integrar (dimensión Sombra/Creatividad/Mente).

5. LA INVITACIÓN ACTUAL: sintetizar en qué etapa del viaje endonauta (despertar, exploración, integración, expresión) parece estar esta persona según la configuración del chart, y qué práctica o pregunta interior podría abrir la siguiente etapa.

Termina con UNA pregunta de exploración concreta, no retórica — algo que la persona pueda llevar a su diario o práctica.\
"""
    return prompt


def _deepseek_call(api_key, system_prompt, user_prompt, temperature=0.78, max_tokens=1200):
    resp = requests.post(
        'https://api.deepseek.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        json={
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': user_prompt},
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']


def _generate_interpretation_async(report_pk, birth_place):
    from django.db import connection
    connection.close()

    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)
        return

    try:
        report = BirthReport.objects.get(pk=report_pk)
        prompt = _build_astral_prompt(report.chart_data, birth_place)
        text = _deepseek_call(api_key, _SYSTEM_ESPEJO, prompt, max_tokens=2500)
        report.interpretation = text
        report.status = BirthReport.STATUS_COMPLETE
        report.save(update_fields=['interpretation', 'status', 'updated_at'])
    except Exception:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)


@login_required
def birth_profile(request):
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        bp = None

    if request.method == 'POST':
        birth_date = request.POST.get('birth_date', '').strip()
        birth_time = request.POST.get('birth_time', '').strip() or None
        birth_place = request.POST.get('birth_place', '').strip()
        gender = request.POST.get('gender', '').strip()

        if not birth_date or not birth_place:
            return render(request, 'birth/birth_form.html', {
                'bp': bp,
                'error': 'La fecha y el lugar de nacimiento son obligatorios.',
            })

        # Prefer coordinates sent from the autocomplete (already confirmed by user)
        lat_raw = request.POST.get('latitude', '').strip()
        lng_raw = request.POST.get('longitude', '').strip()
        if lat_raw and lng_raw:
            try:
                lat, lng = float(lat_raw), float(lng_raw)
            except ValueError:
                lat, lng = None, None
        else:
            lat, lng = _geocode(birth_place)
        tz_str = _get_timezone(lat, lng) if lat else 'UTC'

        if bp:
            bp.birth_date = birth_date
            bp.birth_time = birth_time
            bp.birth_place = birth_place
            bp.latitude = lat
            bp.longitude = lng
            bp.timezone_str = tz_str
            if gender in ('M', 'F'):
                bp.gender = gender
            bp.save()
        else:
            bp = BirthProfile.objects.create(
                user=request.user,
                birth_date=birth_date,
                birth_time=birth_time,
                birth_place=birth_place,
                latitude=lat,
                longitude=lng,
                timezone_str=tz_str,
                gender=gender if gender in ('M', 'F') else '',
            )

        return redirect('birth:profile')

    reports = {}
    if bp:
        for rtype in [BirthReport.TYPE_ASTRAL, BirthReport.TYPE_HD, BirthReport.TYPE_SAJU]:
            reports[rtype] = BirthReport.objects.filter(
                user=request.user, report_type=rtype
            ).first()

    return render(request, 'birth/birth_form.html', {
        'bp': bp,
        'astral_report': reports.get(BirthReport.TYPE_ASTRAL),
        'hd_report':     reports.get(BirthReport.TYPE_HD),
        'saju_report':   reports.get(BirthReport.TYPE_SAJU),
    })


@login_required
def astral_generate(request):
    if request.method != 'POST':
        return redirect('birth:profile')

    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        return redirect('birth:profile')

    _ensure_timezone(bp)
    chart_data = calculate_astral_chart(bp)

    report, _ = BirthReport.objects.update_or_create(
        user=request.user,
        report_type=BirthReport.TYPE_ASTRAL,
        defaults={
            'chart_data': chart_data,
            'status': BirthReport.STATUS_COMPLETE,
            'interpretation': '',
        },
    )
    return redirect('birth:astral_detail', pk=report.pk)


@login_required
def astral_detail(request, pk):
    report = get_object_or_404(
        BirthReport, pk=pk, user=request.user, report_type=BirthReport.TYPE_ASTRAL
    )
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        bp = None

    chart = report.chart_data or {}
    raw_planets = chart.get('planets', [])

    def _annotate(p, key_override=None):
        key = key_override or p.get('key', '')
        return {
            **p,
            'planet_desc': _ASTRAL_PLANET_DESCS.get(key, ''),
            'sign_desc':   _ASTRAL_SIGN_DESCS.get(p.get('sign', ''), ''),
            'house_desc':  _ASTRAL_HOUSE_DESCS.get(str(p.get('house', '')), ''),
            'elem_css':    _SIGN_ELEM_CSS.get(p.get('sign', ''), 'water'),
        }

    annotated_planets = [_annotate(p) for p in raw_planets]
    sun  = next((p for p in annotated_planets if p.get('key') == 'sun'), {})
    moon = next((p for p in annotated_planets if p.get('key') == 'moon'), {})
    asc_raw = chart.get('ascendant', {})
    mc_raw  = chart.get('midheaven', {})
    asc = _annotate({**asc_raw, 'house': 1,  'retrograde': False, 'degree': asc_raw.get('degree',''), 'label': 'Ascendente'}, key_override='asc')
    mc  = _annotate({**mc_raw,  'house': 10, 'retrograde': False, 'degree': mc_raw.get('degree',''),  'label': 'Medio Cielo'}, key_override='mc')

    return render(request, 'birth/astral_detail.html', {
        'report':             report,
        'bp':                 bp,
        'poll_url':           f'/nacimiento/reporte/{report.pk}/estado/',
        'is_processing':      report.status == BirthReport.STATUS_PROCESSING,
        'annotated_planets':  annotated_planets,
        'sun':                sun,
        'moon':               moon,
        'asc':                asc,
        'mc':                 mc,
    })


@login_required
def report_status(request, pk):
    report = get_object_or_404(BirthReport, pk=pk, user=request.user)
    return JsonResponse({
        'status': report.status,
        'interpretation': report.interpretation if report.status == BirthReport.STATUS_COMPLETE else '',
    })


# ── Human Design ───────────────────────────────────────────────────────────


def _build_hd_prompt(chart_data, birth_place):
    p = chart_data['personality']
    d = chart_data['design']
    channels_str = ', '.join(
        f"{ch['gates']} ({ch['name']})"
        for ch in chart_data.get('defined_channels', [])
    ) or 'ninguno definido'
    centers_str = ', '.join(chart_data['defined_centers'])
    undefined = [c for c in ['Cabeza','Ajna','Garganta','Identidad','Corazón',
                              'Plexo Solar','Sacral','Bazo','Raíz']
                 if c not in chart_data['defined_centers']]

    kb = _kb_context(['autorregulación', 'observador', 'toma de decisiones', 'cuerpo energético'])

    prompt = f"""\
DISEÑO HUMANO — {birth_place}
━━━━━━━━━━━━━━━━━━━━━━━━━
TIPO: {chart_data['type']}
ESTRATEGIA: {chart_data['strategy']}
AUTORIDAD: {chart_data.get('authority','')}
PERFIL: {chart_data['profile']}
DEFINICIÓN: {chart_data.get('definition','')}
TEMA NO-YO / FIRMA: {chart_data['not_self_theme']} → {chart_data.get('signature','')}

PUERTAS DEL SOL (consciente ↔ inconsciente):
  Personalidad Sol: Puerta {p['sun']['gate']} — {p['sun']['name']} (Línea {p['sun']['line']})
  Personalidad Tierra: Puerta {p['earth']['gate']} — {p['earth']['name']} (Línea {p['earth']['line']})
  Diseño Sol: Puerta {d['sun']['gate']} — {d['sun']['name']} (Línea {d['sun']['line']})
  Diseño Tierra: Puerta {d['earth']['gate']} — {d['earth']['name']} (Línea {d['earth']['line']})

CENTROS DEFINIDOS ({len(chart_data['defined_centers'])}): {centers_str}
CENTROS ABIERTOS ({len(undefined)}): {', '.join(undefined) if undefined else 'ninguno'}
CANALES DEFINIDOS: {channels_str}
━━━━━━━━━━━━━━━━━━━━━━━━━
{"CONTEXTO DE LA BASE DE CONOCIMIENTOS:" + chr(10) + kb + chr(10) + "━━━━━━━━━━━━━━━━━━━━━━━━━" if kb else ""}

INSTRUCCIÓN DE FORMATO — 5 párrafos en este orden exacto:

1. TIPO Y ESTRATEGIA EN LA VIDA COTIDIANA: no describas el tipo en abstracto — muestra cómo se manifiesta concretamente ser un {chart_data['type']} con estrategia "{chart_data['strategy']}" en el día a día, en el trabajo, en las relaciones. Qué fricción genera ignorar esta estrategia (dimensión Identidad/Cuerpo).

2. AUTORIDAD INTERIOR — LA FORMA DE DECIDIR: explica cómo esta persona toma decisiones alineadas con su diseño usando su autoridad {chart_data.get('authority','')}. Sé específico sobre el proceso interno (esperar, sentir, saber): no la definas en abstracto, muéstrala en una situación concreta (dimensión Emociones/Mente).

3. EL PERFIL Y EL ROL DE VIDA: el perfil {chart_data['profile']} define el patrón de cómo esta persona aprende y contribuye. Describe qué tipo de experiencias tiende a atraer, qué conflicto interno genera el perfil y cuál es el don que emerge cuando lo vive conscientemente (dimensión Propósito/Vínculos).

4. LAS PUERTAS DEL SOL — EL HILO CONSCIENTE E INCONSCIENTE: la Puerta {p['sun']['gate']} ({p['sun']['name']}) es la energía que esta persona irradia conscientemente; la Puerta {d['sun']['gate']} ({d['sun']['name']}) opera desde el inconsciente como una corriente de fondo. Cómo se integran o se tensionan (dimensión Creatividad/Sombra/Espiritualidad).

5. CENTROS DEFINIDOS, CENTROS ABIERTOS Y EL TEMA NO-YO: los centros definidos ({centers_str}) son energías consistentes que esta persona tiene para dar. Los centros abiertos son donde más fácilmente absorbe y se condiciona. Cómo se manifiesta el tema No-Yo "{chart_data['not_self_theme']}" y cómo reconocer cuando uno está viviendo desde el diseño vs. el condicionamiento (dimensión Sombra/Abundancia/Comunidad).

Termina con UNA pregunta de exploración concreta — algo que apunte directamente a la tensión más viva que surge de este diseño específico.\
"""
    return prompt


def _generate_hd_async(report_pk, birth_place):
    from django.db import connection
    connection.close()
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)
        return
    try:
        report = BirthReport.objects.get(pk=report_pk)
        prompt = _build_hd_prompt(report.chart_data, birth_place)
        text = _deepseek_call(api_key, _SYSTEM_ESPEJO, prompt, max_tokens=2500)
        report.interpretation = text
        report.status = BirthReport.STATUS_COMPLETE
        report.save(update_fields=['interpretation', 'status', 'updated_at'])
    except Exception:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)


@login_required
def hd_generate(request):
    if request.method != 'POST':
        return redirect('birth:profile')
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        return redirect('birth:profile')

    _ensure_timezone(bp)
    chart_data = calculate_hd_chart(bp)
    report, _ = BirthReport.objects.update_or_create(
        user=request.user, report_type=BirthReport.TYPE_HD,
        defaults={'chart_data': chart_data, 'status': BirthReport.STATUS_COMPLETE, 'interpretation': ''},
    )
    return redirect('birth:hd_detail', pk=report.pk)


@login_required
def hd_detail(request, pk):
    report = get_object_or_404(BirthReport, pk=pk, user=request.user, report_type=BirthReport.TYPE_HD)
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        bp = None
    chart = report.chart_data or {}
    profile_line = (chart.get('profile') or '')[0] if chart.get('profile') else ''
    hd_descs = {
        'type':       _HD_TYPE_DESCS.get(chart.get('type', ''), ''),
        'strategy':   _HD_STRATEGY_DESCS.get(chart.get('strategy', ''), ''),
        'authority':  _HD_AUTHORITY_DESCS.get(chart.get('authority', ''), ''),
        'profile':    _HD_PROFILE_LINE_DESCS.get(profile_line, ''),
        'definition': _HD_DEFINITION_DESCS.get(chart.get('definition', ''), ''),
        'not_self':   _HD_NOT_SELF_DESCS.get(chart.get('not_self_theme', ''), ''),
        'signature':  _HD_SIGNATURE_DESCS.get(chart.get('signature', ''), ''),
    }
    channels_with_descs = [
        {**ch, 'desc': _HD_CHANNEL_DESCS.get(_channel_key(ch.get('gates', '')), '')}
        for ch in chart.get('defined_channels', [])
    ]
    centers_with_descs = [
        {'name': c, 'desc': _HD_CENTER_DEFINED_DESCS.get(c, '')}
        for c in chart.get('defined_centers', [])
    ]
    annotated_planets_hd = []
    for pair in chart.get('planets_paired', []):
        p = dict(pair['p'])
        d = dict(pair['d'])
        p['gate_desc'] = _HD_GATE_DESCS.get(p.get('gate'), '')
        d['gate_desc'] = _HD_GATE_DESCS.get(d.get('gate'), '')
        annotated_planets_hd.append({
            'p': p, 'd': d,
            'planet_desc': _HD_PLANET_DESCS.get(p.get('label', ''), ''),
        })
    return render(request, 'birth/hd_detail.html', {
        'report': report, 'bp': bp,
        'poll_url': f'/nacimiento/reporte/{report.pk}/estado/',
        'hd_descs':              hd_descs,
        'channels_with_descs':   channels_with_descs,
        'centers_with_descs':    centers_with_descs,
        'annotated_planets_hd':  annotated_planets_hd,
    })


# ── Saju ───────────────────────────────────────────────────────────────────

def _build_saju_prompt(chart_data, birth_place):
    pillars = chart_data['pillars']
    ec = chart_data['element_count']
    daewoon = chart_data.get('daewoon')

    p_lines = '\n'.join(
        f"  Pilar {p['label']}: {p['stem']} ({p['rom_stem']}) — {p['elem_stem']} | "
        f"Rama {p['branch']} ({p['rom_branch']}) — {p['elem_branch']}, {p['animal']}"
        for p in pillars
    )
    elem_line = '  ' + ' | '.join(f"{e}: {ec.get(e,0)}" for e in ELEMENTS_ES)

    current = None
    next_cycle = None
    if daewoon:
        current = daewoon.get('current_cycle')
        if current:
            idx = daewoon['cycles'].index(current)
            next_cycle = daewoon['cycles'][idx+1] if idx < len(daewoon['cycles'])-1 else None

    daewoon_block = ''
    if current:
        daewoon_block = (
            f"\nCICLO VITAL ACTUAL (大運):\n"
            f"  {current['stem']}{current['branch']} — {current['elem_stem']} sobre {current['elem_branch']}\n"
            f"  Período: edades {current['age_start']}–{current['age_end']} "
            f"({current['year_start']}–{current['year_end']})\n"
        )
        if next_cycle:
            daewoon_block += (
                f"Próximo ciclo (comienza ~{next_cycle['year_start']}): "
                f"{next_cycle['stem']}{next_cycle['branch']} — {next_cycle['elem_stem']}\n"
            )

    kb = _kb_context(['cinco elementos', 'yin yang', 'fluir', 'Qi', 'madera fuego tierra metal agua'])

    # Day master decomposed: e.g. "Madera Yang" → element=Madera, polarity=Yang
    day_master_parts = chart_data['day_master'].split()
    dm_elem = day_master_parts[0] if day_master_parts else chart_data['day_master']
    dm_pol  = day_master_parts[1] if len(day_master_parts) > 1 else ''

    hour_known = chart_data.get('hour_known', True)
    total_chars = len(pillars) * 2
    pillar_refs = 'Mes, Día y Hora' if hour_known else 'Mes y Día'
    hora_note = '' if hour_known else '\nNOTA: La hora de nacimiento no está disponible — el Pilar de la Hora no fue calculado. El balance elemental es parcial (basado en 6 de 8 caracteres).\n'

    prompt = f"""\
SAJU — CUATRO PILARES DEL DESTINO — {birth_place}
━━━━━━━━━━━━━━━━━━━━━━━━━
MAESTRO DEL DÍA: {chart_data['day_master']} (elemento {dm_elem}, polaridad {dm_pol})
ANIMAL DEL AÑO: {chart_data['lunar_year_animal']}
{hora_note}
PILARES CALCULADOS (四柱八字):
{p_lines}

BALANCE ELEMENTAL ({total_chars} caracteres conocidos):
{elem_line}
  Dominante: {chart_data['dominant_element']} | Mínimo/ausente: {chart_data.get('weakest_element','equilibrado')}
{daewoon_block}━━━━━━━━━━━━━━━━━━━━━━━━━
{"CONTEXTO DE LA BASE DE CONOCIMIENTOS:" + chr(10) + kb + chr(10) + "━━━━━━━━━━━━━━━━━━━━━━━━━" if kb else ""}

INSTRUCCIÓN DE FORMATO — 5 párrafos en este orden exacto:

1. EL MAESTRO DEL DÍA — LA NATURALEZA CENTRAL: el Maestro del Día {chart_data['day_master']} define la energía esencial. No describas el elemento en abstracto — explica cómo se manifiesta como carácter, como forma de relacionarse con el mundo, qué tipo de fuerza interna tiene y dónde esa misma fuerza puede convertirse en rigidez o herida (dimensión Identidad/Cuerpo). Usa el elemento {dm_elem} como metáfora viva.

2. EL BALANCE ELEMENTAL — LO QUE SOBRA Y LO QUE FALTA: con {chart_data['dominant_element']} como elemento dominante y {chart_data.get('weakest_element','equilibrio') or 'equilibrio'} como el menos presente, describe qué tipo de energía gobierna la vida de esta persona y qué área de vida (emoción, relación, acción, reflexión, flujo) tiende a estar subdesarrollada. Qué prácticas o arquetipos podrían cultivar el elemento faltante (dimensión Emociones/Abundancia/Cuerpo).

3. EL ANIMAL DEL AÑO Y LOS PATRONES RELACIONALES: el {chart_data['lunar_year_animal']} como arquetipo relacional — cómo esta persona se mueve en sus vínculos, qué tipo de dinámicas tiende a atraer y qué patrón inconsciente en las relaciones refleja el animal (dimensión Vínculos/Sombra).

4. LAS TENSIONES INTERNAS — EL PATRÓN QUE SE REPITE: leyendo los pilares de {pillar_refs} (los pilares más personales disponibles), qué tensión o fricción elemental existe entre ellos. Qué conflicto interno se repite, qué patrón inconsciente emerge de esa configuración específica y cómo se manifiesta en decisiones o bloqueos recurrentes (dimensión Mente/Sombra/Creatividad).

5. EL CICLO VITAL ACTUAL — EL CAPÍTULO PRESENTE: {"con el ciclo actual de " + current['elem_stem'] + " sobre " + current['elem_branch'] + " (edades " + str(current['age_start']) + "–" + str(current['age_end']) + "), qué tipo de energía y aprendizaje está disponible en este período. Qué está pidiendo ser soltado y qué está emergiendo. Cómo prepararse para el próximo ciclo" + (" de " + next_cycle['elem_stem'] if next_cycle else "") + " (dimensión Propósito/Espiritualidad/Sueños)." if current else "describirás los ciclos vitales generales según los pilares disponibles, ya que no se cuenta con el ciclo 大運 actual."}

Termina con UNA pregunta de exploración concreta — algo específico a esta carta, no una pregunta genérica sobre crecimiento personal.\
"""
    return prompt


def _generate_saju_async(report_pk, birth_place):
    from django.db import connection
    connection.close()
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)
        return
    try:
        report = BirthReport.objects.get(pk=report_pk)
        prompt = _build_saju_prompt(report.chart_data, birth_place)
        text = _deepseek_call(api_key, _SYSTEM_ESPEJO, prompt, max_tokens=2500)
        report.interpretation = text
        report.status = BirthReport.STATUS_COMPLETE
        report.save(update_fields=['interpretation', 'status', 'updated_at'])
    except Exception:
        BirthReport.objects.filter(pk=report_pk).update(status=BirthReport.STATUS_FAILED)


@login_required
def saju_generate(request):
    if request.method != 'POST':
        return redirect('birth:profile')
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        return redirect('birth:profile')

    _ensure_timezone(bp)
    chart_data = calculate_saju_chart(bp)
    report, _ = BirthReport.objects.update_or_create(
        user=request.user, report_type=BirthReport.TYPE_SAJU,
        defaults={'chart_data': chart_data, 'status': BirthReport.STATUS_COMPLETE, 'interpretation': ''},
    )
    return redirect('birth:saju_detail', pk=report.pk)


@login_required
def saju_detail(request, pk):
    report = get_object_or_404(BirthReport, pk=pk, user=request.user, report_type=BirthReport.TYPE_SAJU)
    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        bp = None
    chart = report.chart_data or {}
    annotated_pillars = [
        {**p, 'pilar_desc': _SAJU_PILLAR_DESCS.get(p.get('label', ''), '')}
        for p in chart.get('pillars', [])
    ]
    return render(request, 'birth/saju_detail.html', {
        'report':            report,
        'bp':                bp,
        'poll_url':          f'/nacimiento/reporte/{report.pk}/estado/',
        'annotated_pillars': annotated_pillars,
        'saju_elem_descs':   _SAJU_ELEMENT_DESCS,
    })


# ── Lectura endonauta (vistas de interpretación AI) ───────────────────────

_BIRTH_TYPE_LABELS = {
    BirthReport.TYPE_ASTRAL: 'Carta Astral',
    BirthReport.TYPE_HD:     'Diseño Humano',
    BirthReport.TYPE_SAJU:   'Saju',
}

_BIRTH_ASYNC_FNS = {
    BirthReport.TYPE_ASTRAL: _generate_interpretation_async,
    BirthReport.TYPE_HD:     _generate_hd_async,
    BirthReport.TYPE_SAJU:   _generate_saju_async,
}

_BIRTH_LECTURA_NAMES = {
    BirthReport.TYPE_ASTRAL: 'astral_lectura',
    BirthReport.TYPE_HD:     'hd_lectura',
    BirthReport.TYPE_SAJU:   'saju_lectura',
}

_REPORT_TYPE_KEYS = {
    BirthReport.TYPE_ASTRAL: 'astral',
    BirthReport.TYPE_HD:     'hd',
    BirthReport.TYPE_SAJU:   'saju',
}


def _birth_lectura_view(request, pk, report_type):
    from django.urls import reverse
    from mirror.models import ConflictSession
    report = get_object_or_404(BirthReport, pk=pk, user=request.user, report_type=report_type)
    is_processing = report.interpretation == 'processing'
    is_revealed   = bool(report.interpretation) and report.interpretation != 'processing'
    _detail_names = {
        BirthReport.TYPE_ASTRAL: 'birth:astral_detail',
        BirthReport.TYPE_HD:     'birth:hd_detail',
        BirthReport.TYPE_SAJU:   'birth:saju_detail',
    }
    back_view = _detail_names.get(report_type, 'birth:profile')
    type_key  = _REPORT_TYPE_KEYS.get(report_type, 'astral')
    sec_cfg   = _SECTION_CONFIGS.get(type_key, [])
    sections  = _parse_lectura_sections(report.interpretation, sec_cfg) if is_revealed else []
    espejo_count = ConflictSession.objects.filter(user=request.user, status='archived').count()
    desbloqueado = espejo_count >= 1
    return render(request, 'birth/lectura.html', {
        'report':               report,
        'label':                _BIRTH_TYPE_LABELS.get(report_type, ''),
        'is_processing':        is_processing,
        'is_revealed':          is_revealed,
        'poll_url':             f'/nacimiento/reporte/{report.pk}/lectura-estado/',
        'reveal_url':           f'/nacimiento/reporte/{report.pk}/revelar/',
        'back_url':             reverse(back_view, args=[report.pk]),
        'sections':             sections,
        'sections_config_json': json.dumps(sec_cfg, ensure_ascii=False),
        'desbloqueado':         desbloqueado,
    })


@login_required
def astral_lectura(request, pk):
    return _birth_lectura_view(request, pk, BirthReport.TYPE_ASTRAL)


@login_required
def hd_lectura(request, pk):
    return _birth_lectura_view(request, pk, BirthReport.TYPE_HD)


@login_required
def saju_lectura(request, pk):
    return _birth_lectura_view(request, pk, BirthReport.TYPE_SAJU)


@login_required
def birth_insight_reveal(request, pk):
    if request.method != 'POST':
        return redirect('birth:profile')
    report = get_object_or_404(BirthReport, pk=pk, user=request.user)

    if report.interpretation and report.interpretation != 'processing':
        lectura_name = _BIRTH_LECTURA_NAMES.get(report.report_type, 'profile')
        return redirect(f'birth:{lectura_name}', pk=pk)

    try:
        bp = request.user.birth_profile
    except BirthProfile.DoesNotExist:
        return redirect('birth:profile')

    from tokens.service import spend, has_balance
    if not has_balance(request.user, 'report'):
        lectura_name = _BIRTH_LECTURA_NAMES.get(report.report_type, 'profile')
        return redirect(f'birth:{lectura_name}', pk=pk)

    label = _BIRTH_TYPE_LABELS.get(report.report_type, 'Lectura')
    spend(request.user, 'report', reason=f'Lectura endonauta — {label}')

    BirthReport.objects.filter(pk=pk).update(
        interpretation='processing',
        status=BirthReport.STATUS_PROCESSING,
    )
    fn = _BIRTH_ASYNC_FNS.get(report.report_type)
    if fn:
        threading.Thread(target=fn, args=[report.pk, bp.birth_place], daemon=True).start()

    lectura_name = _BIRTH_LECTURA_NAMES.get(report.report_type, 'profile')
    return redirect(f'birth:{lectura_name}', pk=pk)


@login_required
def birth_insight_status(request, pk):
    report = get_object_or_404(BirthReport, pk=pk, user=request.user)
    if report.interpretation in ('', 'processing'):
        return JsonResponse({'status': 'processing'})
    if report.status == BirthReport.STATUS_FAILED:
        return JsonResponse({'status': 'failed'})
    return JsonResponse({'status': 'complete', 'interpretation': report.interpretation})


@login_required
def toggle_report_public(request, pk):
    from django.views.decorators.http import require_POST
    report = get_object_or_404(BirthReport, pk=pk, user=request.user)
    report.is_public = not report.is_public
    report.save(update_fields=['is_public'])
    return JsonResponse({'ok': True, 'is_public': report.is_public})
