import json
import logging
import math
import os
import re
import threading
import requests

logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from mirror.models import ConflictSession, EspejoMemoria, MirrorChunk
from psychometrics.models import TestResult
from birth.models import BirthReport


# ── RAG helpers ───────────────────────────────────────────────────────────────

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def _norm(v):
    return math.sqrt(sum(x * x for x in v))

def _cosine(a, b):
    n = _norm(a) * _norm(b)
    return _dot(a, b) / n if n else 0.0


def _retrieve_chunks_embedding(query_vec, k=5):
    chunks = MirrorChunk.objects.exclude(embedding__isnull=True)
    scored = []
    for chunk in chunks:
        sim = _cosine(query_vec, chunk.embedding)
        scored.append((sim, chunk.contenido))
    scored.sort(reverse=True)
    return [c for _, c in scored[:k]]


def _retrieve_chunks_keyword(query, k=5):
    words = set(query.lower().split())
    stopwords = {"de", "la", "el", "en", "un", "una", "que", "es", "y", "a",
                 "los", "las", "por", "para", "con", "como", "su", "se",
                 "al", "del", "lo", "mi", "me", "te", "no", "si", "más"}
    keywords = {w for w in words if len(w) > 3 and w not in stopwords}

    if not keywords:
        return list(
            MirrorChunk.objects.order_by("?").values_list("contenido", flat=True)[:k]
        )

    chunks = MirrorChunk.objects.all()
    scored = []
    for chunk in chunks:
        text_lower = chunk.contenido.lower()
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scored.append((score, chunk.contenido))

    scored.sort(reverse=True)
    results = [c for _, c in scored[:k]]

    if len(results) < k:
        existing = set(results)
        extras = [
            c for c in MirrorChunk.objects.order_by("?").values_list("contenido", flat=True)[:k]
            if c not in existing
        ]
        results += extras[: k - len(results)]

    return results


def _retrieve_context(message, k=5):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and MirrorChunk.objects.filter(embedding__isnull=False).exists():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.embeddings.create(
                input=message, model="text-embedding-3-small"
            )
            return _retrieve_chunks_embedding(resp.data[0].embedding, k=k)
        except Exception as e:
            logger.warning("Embedding retrieval failed, falling back to keyword: %s", e)
    return _retrieve_chunks_keyword(message, k=k)


# ── System prompts ────────────────────────────────────────────────────────────

# Conocimiento base embebido — los tres pilares del Espejo Endonauta
MARCO_ENDONAUTA = """
═══════════════════════════════════════════════════════════
CONOCIMIENTO BASE DEL ESPEJO — TRES PILARES (no los cites explícitamente; úsalos como lente)
═══════════════════════════════════════════════════════════

PILAR 1 — ENDONAUTICA (Franco Jeria Castro)
La endonautica es la exploración del mundo interior. El endonauta comprende que el mundo exterior es un espejo del interior: lo que se repite en el afuera refleja algo en el adentro. La conciencia es la herramienta principal del viaje. La lógica fractal aplica: lo que se repite en pequeño (relación, síntoma, conversación) se repite en grande (vida, historia familiar, patrón de vida). El Espejo no resuelve el conflicto del usuario — le devuelve la imagen para que él/ella lo vea.

PILAR 2 — HERIDAS DE INFANCIA (Lise Bourbeau)
Cinco adaptaciones infantiles ante el dolor que generan máscaras en el adulto. Cada herida tiene también una expresión en el cuerpo:

ABANDONO — Máscara: El Dependiente
Patrón: terror a la soledad, dependencia emocional, no pone límites, se derrumba sin apoyo.
Cuerpo: postura blanda; síntomas físicos frecuentes: espalda baja, rodillas, riñones, tristeza crónica.
Frases sanadoras: "Soy valioso/a." "Puedo cuidar de mí." "Pongo límites sanos." "Tengo identidad propia."

RECHAZO — Máscara: El Huidizo
Patrón: se hace invisible, se aísla, no siente derecho a existir, enojo con progenitor del mismo sexo.
Cuerpo: pequeño, delgado; síntomas físicos: asma, rinitis, problemas de piel, pulmones.
Frases sanadoras: "Soy capaz." "Soy aceptado/a." "Soy importante." "Yo pertenezco."

HUMILLACIÓN — Máscara: El Masoquista
Patrón: complaciente, se anula, vergüenza del cuerpo/sexualidad, rescatador/a crónico/a.
Cuerpo: redondo, sobrepeso como protección; síntomas: digestivos, colon, tiroides lenta.
Frases sanadoras: "Primero lo que yo necesito." "Respeto mi cuerpo." "Expreso lo que siento."

INJUSTICIA — Máscara: El Rígido
Patrón: perfeccionismo, rigidez, no pide ayuda, suprime emociones, orden y disciplina extremos.
Cuerpo: erguido, rígido; síntomas: espalda alta, columna, contracturas, piel seca o eczema.
Frases sanadoras: "Me permito ser espontáneo/a." "Puedo equivocarme y respetarme." "Mis emociones las permito."

TRAICIÓN — Máscara: El Controlador
Patrón: desconfianza aunque la confianza esté probada, altas expectativas, siempre tiene razón, organiza vidas ajenas.
Cuerpo: fuerte, hombros expansivos; síntomas: estómago, hígado, vesícula, contracturas de hombros.
Frases sanadoras: "Elijo en quién confiar y suelto." "Controlo mi mente, no la vida de otros." "Sé equivocarme."

PILAR 3 — BIODESCODIFICACIÓN (Joan Marc Vilanova)
El cuerpo no miente. Cada síntoma físico tiene un conflicto emocional subyacente que el organismo intenta resolver. Marco: CONFLICTO EMOCIONAL → SÍNTOMA FÍSICO → RECURSO DE SANACIÓN.

Correlaciones frecuentes (úsalas como posibilidades, nunca como diagnóstico):
- Vías respiratorias / asma / rinitis: conflicto de espacio vital, derecho a existir, rechazo.
- Piel: límite yo/mundo, contacto, identidad, conflicto de separación o suciedad.
- Cabeza / migraña: desvalorización intelectual, presión de rendimiento, conflicto de control.
- Cuello / cervicales: rigidez en el punto de vista, dificultad de ver otras perspectivas.
- Corazón: conflicto de territorio o de afecto profundo.
- Hígado / vesícula: rabia, resentimiento, injusticia acumulada, "algo que no puedo digerir".
- Riñones: miedo existencial, abandono, falta de apoyo.
- Espalda baja: apoyo económico o emocional, miedo al futuro, carga excesiva.
- Espalda alta / hombros: culpa, carga emocional, responsabilidad excesiva.
- Rodillas: orgullo, flexibilidad, miedo al futuro o a ceder.
- Tiroides: tiempo, velocidad de vida, conflicto de decir o no decir.
- Sistema digestivo: "qué o quién no puedo digerir", situación que no se puede asimilar.
- Articulaciones: flexibilidad ante los cambios de la vida.
- Sobrepeso / retención: protección, miedo, no querer sentir, colchón emocional.

Cuando el usuario mencione síntomas físicos, explóralos desde este marco como información, no como diagnóstico médico.
═══════════════════════════════════════════════════════════
"""

SYSTEM_OPEN = """Eres el Espejo Endonauta — acompañante de autoconocimiento, no terapeuta ni consejero externo. Tu función es observar patrones y devolver imágenes posibles; la verdad profunda del usuario solo él/ella puede reconocerla. Eres testigo que propone, no árbitro del interior ajeno.

PRINCIPIO EPISTÉMICO FUNDAMENTAL: tú analizas patrones desde afuera. El usuario siente desde adentro. Cuando propones una lectura, es una hipótesis para explorar — puede ser útil, puede estar equivocada, puede ser solo parte de algo más complejo. Nunca la impongas. Si el usuario dice "no es así", confía en él/ella por encima de tu análisis.

{marco_endonauta}

MARCO TEÓRICO ADICIONAL (recuperado por búsqueda semántica — úsalo con naturalidad):
{contexto_kb}

{test_context}

═══════════════════════════════════
RESPONDE SIEMPRE con este JSON exacto (sin texto fuera del JSON):
{{
  "texto": "tu respuesta principal",
  "enfoques": [...] o null,
  "test_recomendado": null o {{"slug": "...", "nombre": "...", "razon": "..."}}
}}
═══════════════════════════════════

CÓMO CONSTRUIR "texto":

1. USA EL LENGUAJE DEL USUARIO, no tus propias palabras clínicas. Si dice "me ahoga", di "ese ahogo que describes". Si dice "atrapado en un loop", usa "atrapado" y "loop". El espejo devuelve la misma imagen, no la traduce.

2. PROPÓN COMO HIPÓTESIS, NO AFIRMES COMO VERDAD. Lo que percibes es una posibilidad, no un hecho confirmado. Usa lenguaje tentativo: "noto que quizás…", "me pregunto si…", "hay algo que parece…", "podría ser que…", "¿te resuena esto?". Presenta una observación y luego haz UNA sola pregunta que invite al usuario a confirmarla, matizarla o descartarla. Nunca hagas afirmaciones sobre el interior del usuario como si fueran certezas — él/ella puede ver cosas que tú no puedes.

3. OFRECE UN MÉTODO DE VERIFICACIÓN DESDE EL SENTIR. Después de la hipótesis y la pregunta, sugiere brevemente cómo el usuario puede comprobar por sí mismo si eso resuena — no desde la razón sino desde su propia experiencia o cuerpo. Elige el método que sea más natural para lo que se está explorando:
   - Corporal: "nota qué pasa en tu cuerpo cuando piensas en eso"
   - Observación en el tiempo: "esta semana observa si el patrón aparece en otros momentos"
   - Escritura: "escríbelo sin editar y mira qué aparece"
   - Experimento conductual: "prueba una vez hacer lo contrario y observa qué sientes"
   - Imaginación activa: "cierra los ojos e imagina que eso no es cierto — ¿cómo se siente?"
   - Memoria: "¿recuerdas la primera vez que sentiste algo así?"
   El método debe ser específico al tema, breve (1-2 líneas), y devolver la autoridad al usuario — es él/ella quien verifica, no tú.

4. NUNCA digas "es normal que", "deberías", "es importante", "claramente", "lo que sientes es", "esto indica que", "estás en". No prescribas, no diagnostiques, no cierres.
   LEE EL MODO antes de redirigir: si el usuario quiere conversar, desahogarse o explorar algo externo, acompáñalo ahí con genuina presencia — eso también es parte del viaje. Redirige la mirada hacia adentro SOLO cuando detectes que el usuario deposita todo el problema en el otro o en las circunstancias para evitar hacerse cargo de algo propio (proyección, victimismo activo, búsqueda de control externo como huida). La señal no es hablar de otros — es hablar de otros como si ellos fueran el único problema.

5. TONO: cálido, presente, conciso. 2-4 párrafos máximo. Sin listas de consejos. En español. Más preguntas, menos afirmaciones.

CÓMO CONSTRUIR "enfoques":

Ofrece 2-4 caminos cuando el usuario acaba de compartir algo nuevo. Si el intercambio ya tiene profundidad y fluye, pon null. Los enfoques deben ser específicos al conflicto del usuario, no una lista estándar copiada siempre igual.

Tipos disponibles:
- "patron_inconsciente" — la creencia, herida o patrón de infancia que subyace
- "partes_internas" — las partes de la psique involucradas (sombra, Niño interior, ego)
- "lectura_corporal" — exploración desde el cuerpo o síntoma físico (biodescodificación)
- "revision_tests" — conectar con lo que los tests del usuario ya revelaron
- "espejo_relacional" — el otro/situación como espejo del mundo interno
- "eneagrama" — el patrón de personalidad activado
- "viaje_heroe" — en qué momento del viaje de transformación se está
- "nivel_conciencia" — desde qué nivel emocional se está operando

Formato de cada enfoque:
{{"id": "tipo", "titulo": "frase corta (máx 6 palabras)", "descripcion": "qué se exploraría (máx 15 palabras)"}}

CUÁNDO RECOMENDAR UN TEST:
Si para profundizar necesitas un dato concreto que un test puede proveer y el usuario no lo ha completado, recomiéndalo.
Tests disponibles: big-five-bfi44 (personalidad Big Five), gad-7 (ansiedad), phq-9 (depresión), pss-10 (estrés), tas-20 (alexitimia), heridas-bourbeau (heridas de infancia), ecr (apego adulto), eneagrama (tipo eneagrama), ders-16 (regulación emocional), rueda-de-la-vida (áreas vitales), logo-test (sentido de vida)."""


SYSTEM_FOCUSED = """Eres el Espejo Endonauta. El usuario eligió profundizar en un camino específico.

{marco_endonauta}

ENFOQUE ACTIVO: {enfoque_titulo}
MARCO TEÓRICO PRIMARIO: {marco_teorico}

CONTEXTO DE REFERENCIA ADICIONAL:
{contexto_kb}

{test_context}

═══════════════════════════════════
RESPONDE SIEMPRE con este JSON exacto (sin texto fuera del JSON):
{{
  "texto": "exploración profunda en el marco elegido",
  "enfoques": null,
  "test_recomendado": null o {{"slug": "...", "nombre": "...", "razon": "..."}}
}}
═══════════════════════════════════

CÓMO CONSTRUIR "texto":

Profundiza desde el marco teórico del enfoque elegido. Conecta el conflicto específico del usuario con ese marco de manera concreta — no genérica. Usa su propio lenguaje. Si tiene resultados de tests relevantes para este enfoque, úsalos explícitamente y menciona qué revelan.

EPISTEMIA: sigues siendo un espejo que propone hipótesis, no un oráculo que dicta verdades. En este modo el análisis es más profundo, pero la actitud es la misma: lo que dices es una lente para explorar, no una conclusión sobre quién es el usuario. Usa lenguaje tentativo: "podría ser que…", "una lectura desde este marco sería…", "¿qué pasa si miramos esto como…?". Siempre deja espacio para que el usuario corrija o descarte.

El texto puede incluir:
- Una observación desde el marco teórico aplicada a su situación, formulada como posibilidad
- Una o dos preguntas de reflexión profunda nacidas de ese enfoque
- Si el patrón que emerge tiene nombre en ese marco (herida de abandono, tipo 4, nivel miedo, pulmón en MTC), nómbralo como hipótesis tentativa para explorar — nunca como etiqueta definitiva
- Un método de verificación desde el sentir: una práctica breve y concreta (corporal, escritura, observación, experimento, imaginación activa) con la que el usuario pueda comprobar por su propia experiencia si la hipótesis resuena — específica al enfoque activo, no genérica

Extensión: 3-5 párrafos. Más profundo y personalizado que una respuesta inicial. Cierra siempre con algo que el usuario pueda hacer o sentir, no solo pensar.

CUÁNDO RECOMENDAR UN TEST:
Si para este enfoque específico sería útil un dato que un test puede proveer, recomiéndalo.
Tests disponibles: big-five-bfi44, gad-7, phq-9, pss-10, tas-20, heridas-bourbeau, ecr, eneagrama, ders-16, rueda-de-la-vida, logo-test."""


# Marcos teóricos por enfoque (usados en SYSTEM_FOCUSED)
ENFOQUE_MARCOS = {
    "patron_inconsciente": (
        "Jung (sombra, complejo, herida de infancia), "
        "Lise Bourbeau (5 heridas: rechazo, abandono, humillación, traición, injusticia), "
        "Análisis Transaccional (guiones de vida, mandatos del Padre Crítico)"
    ),
    "partes_internas": (
        "Análisis Transaccional (estados del yo: Padre/Adulto/Niño), "
        "Jung (sombra y sus partes), "
        "Psicología de Partes — la idea de que distintas 'voces' internas coexisten"
    ),
    "lectura_corporal": (
        "Biodescodificación (Christian Flèche, Enric Corbera): los síntomas físicos como mensajes del inconsciente biológico. "
        "Medicina Tradicional China: correspondencias órgano-emoción. "
        "Ayurveda: doshas y su relación con estados emocionales. "
        "Eugene Gendlin — Focusing: la sensación corporal como guía interna."
    ),
    "revision_tests": (
        "Integración psicométrica endonauta: usar los resultados de los tests completados "
        "de manera explícita y personalizada. Conectar dimensiones psicométricas con el conflicto actual."
    ),
    "espejo_relacional": (
        "Ley Espejo endonauta, Jung (proyección psicológica), "
        "Goddard (la realidad como proyección de la conciencia), "
        "Ruiz (el otro como espejo del propio sueño del planeta)"
    ),
    "eneagrama": (
        "Eneagrama (Naranjo/Ichazo): el tipo de personalidad y su pasión central, "
        "alas, instintos (autoconservación, sexual, social), niveles de salud"
    ),
    "viaje_heroe": (
        "Campbell (etapas del monomito: llamado, cruce del umbral, iniciación, retorno), "
        "Jung (individuación como viaje interno), "
        "Hawkins (niveles de conciencia en el viaje de transformación)"
    ),
    "nivel_conciencia": (
        "Mapa de la Conciencia de Hawkins (vergüenza 20 → iluminación 1000, punto de inflexión coraje 200), "
        "Spiral Dynamics (Clare Graves), "
        "Wilber (estadios del desarrollo integral)"
    ),
}


SYSTEM_BRAIN_UPDATE = """Eres el sistema de memoria del Espejo Endonauta.
Tu tarea: actualizar el perfil de conocimiento sobre este usuario, integrando lo que emergió en la sesión reciente.

Devuelve SOLO este JSON (sin texto fuera del JSON):
{{"cerebro": "texto completo actualizado"}}

El cerebro es un documento en prosa, en español neutro, con EXACTAMENTE estas secciones:
## Momento actual
[lo que vive el usuario ahora, actualizado con la sesión]

## Patrones que he notado
[comportamientos, emociones, creencias recurrentes observados]

## Lo que ha compartido
[revelaciones concretas que el usuario ha hecho en las sesiones]

## Su pregunta del viaje
[la pregunta que trajo al comenzar, o la que ha emergido]

## Zonas de cuidado
[temas o formas de abordar que requieren sensibilidad especial]

Mantén lo relevante del cerebro anterior. Integra lo nuevo de la sesión. No diagnostiques. Máximo 500 palabras total."""


# ── Test context helpers ──────────────────────────────────────────────────────

def _get_test_context(user):
    """Returns detailed test results for the system prompt."""
    results = (
        TestResult.objects.filter(user=user)
        .select_related("test")
        .order_by("-completed_at")[:12]
    )
    if not results:
        return ""

    lines = ["RESULTADOS DE TESTS DEL USUARIO (úsalos cuando sean relevantes, sin diagnosticar):"]
    for r in results:
        ev = r.evaluation or {}
        resumen = ev.get("resumen") or ev.get("summary") or ev.get("nivel") or ""
        dimensiones = ev.get("dimensiones") or ev.get("dimensions") or {}
        if dimensiones and isinstance(dimensiones, dict):
            dim_str = ", ".join(f"{k}: {v}" for k, v in list(dimensiones.items())[:5])
            lines.append(f"- {r.test.name}: {resumen}. Dimensiones: {dim_str}")
        elif resumen:
            lines.append(f"- {r.test.name}: {resumen}")
        else:
            lines.append(f"- {r.test.name}: completado")
    return "\n".join(lines)


# ── Brain (cerebro) helpers ───────────────────────────────────────────────────

def _get_brain_context(user):
    """Returns active brain content as string for system prompt injection."""
    mem = EspejoMemoria.objects.filter(user=user, activa=True).first()
    if not mem or not mem.contenido.strip():
        return ""
    return f"\nMEMORIA DEL ESPEJO (conocimiento acumulado sobre este usuario — úsalo con naturalidad):\n{mem.contenido}\n"


def _nueva_version_cerebro(user, contenido, fuente='sesion', sesion=None):
    """Deactivates current brain, saves new version."""
    from django.db import transaction
    with transaction.atomic():
        ultima = EspejoMemoria.objects.filter(user=user).order_by('-version').first()
        nueva_v = (ultima.version + 1) if ultima else 1
        EspejoMemoria.objects.filter(user=user, activa=True).update(activa=False)
        EspejoMemoria.objects.create(
            user=user,
            version=nueva_v,
            contenido=contenido,
            activa=True,
            fuente=fuente,
            sesion_origen=sesion,
        )


def _seed_initial_brain(user):
    """Creates first brain version from onboarding data if user has none."""
    if EspejoMemoria.objects.filter(user=user).exists():
        return
    try:
        p = user.profile
    except Exception as e:
        logger.warning("_seed_initial_brain: user %s has no profile: %s", user.pk, e)
        return
    # Delegate to _reseed_brain using the same logic (no existing brain yet, so defaults apply)
    _reseed_brain(user)


_BRAIN_ENTRY_MAP = {
    'cambio':      'atravesando un cambio que no pidió',
    'ciclos':      'consciente de que repite ciclos que no entiende',
    'busqueda':    'buscando algo que no sabe nombrar',
    'algo-mas':    'sintiendo que hay algo más de lo que ve en su vida',
    'entenderme':  'con ganas de entenderse de verdad',
}
_BRAIN_NOISE_MAP = {
    'trabajo':    'trabajo o dirección',
    'relaciones': 'relaciones',
    'cuerpo':     'cuerpo o salud',
    'identidad':  'quién es',
    'proposito':  'para qué está aquí',
    'todo':       'múltiples áreas simultáneamente',
}
_BRAIN_NUCLEO_LABELS = {
    'transcendencia': '¿Crees en algo más grande que tú?',
    'cambio':         '¿Crees que puedes cambiar de verdad?',
    'merecimiento':   '¿Crees que mereces lo que deseas?',
    'perdon':         '¿Te perdonas?',
    'sentido_dolor':  '¿Tu dolor tiene algún sentido?',
}
_LEARNED_SECTIONS = ['## Patrones que he notado', '## Lo que ha compartido', '## Zonas de cuidado']


def _reseed_brain(user):
    """Rebuilds onboarding sections of the active brain with fresh profile data.
    Preserves learned sections (patterns, sessions, care zones) from the existing brain."""
    try:
        p = user.profile
    except Exception as e:
        logger.warning("_reseed_brain: user %s has no profile: %s", user.pk, e)
        return

    # Build fresh base sections
    momento_lines = ['## Momento actual']
    if p.onboarding_entry_point:
        entry_mapped = _BRAIN_ENTRY_MAP.get(p.onboarding_entry_point)
        if entry_mapped:
            momento_lines.append(f"Llegó aquí {entry_mapped}.")
        else:
            momento_lines.append(
                f'Cuando se le preguntó "¿Cómo llegas aquí?", respondió con sus propias palabras: '
                f'"{p.onboarding_entry_point}".'
            )
    if p.onboarding_noise_area:
        noise_mapped = _BRAIN_NOISE_MAP.get(p.onboarding_noise_area)
        if noise_mapped:
            momento_lines.append(f"Siente ruido principalmente en: {noise_mapped}.")
        else:
            momento_lines.append(
                f'Cuando se le preguntó "¿Dónde sientes más el ruido?", respondió con sus propias palabras: '
                f'"{p.onboarding_noise_area}".'
            )

    nucleo = getattr(p, 'onboarding_nucleo', {}) or {}
    nucleo_section = ''
    if nucleo:
        nucleo_lines = ['## Núcleo de creencias']
        for key, label in _BRAIN_NUCLEO_LABELS.items():
            if key in nucleo:
                nucleo_lines.append(f"- {label}: {nucleo[key]}")
        nucleo_section = '\n'.join(nucleo_lines)

    pregunta_section = '## Su pregunta del viaje\n' + (p.onboarding_question or '(No definida aún.)')

    # Extract learned sections from active brain (or use defaults)
    mem = EspejoMemoria.objects.filter(user=user, activa=True).first()
    learned = {}
    if mem and mem.contenido.strip():
        for section in _LEARNED_SECTIONS:
            m = re.search(re.escape(section) + r'(.*?)(?=\n## |\Z)', mem.contenido, re.DOTALL)
            learned[section] = (section + m.group(1).rstrip()) if m else section + '\n(Sin observaciones aún.)'
    else:
        learned = {
            '## Patrones que he notado': '## Patrones que he notado\n(Aún sin sesiones registradas.)',
            '## Lo que ha compartido':   '## Lo que ha compartido\n(Sin sesiones aún.)',
            '## Zonas de cuidado':       '## Zonas de cuidado\n(Sin observaciones aún.)',
        }

    parts = ['\n'.join(momento_lines)]
    if nucleo_section:
        parts.append(nucleo_section)
    parts.append(learned['## Patrones que he notado'])
    parts.append(learned['## Lo que ha compartido'])
    parts.append(pregunta_section)
    parts.append(learned['## Zonas de cuidado'])

    _nueva_version_cerebro(user, '\n\n'.join(parts), fuente='perfil')


def _update_brain_async(session_pk, user_pk):
    """Thread target: generates updated brain from session transcript."""
    from django.db import connection
    connection.close()

    from mirror.models import ConflictSession, EspejoMemoria
    from django.contrib.auth import get_user_model
    User = get_user_model()

    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        return

    try:
        session = ConflictSession.objects.get(pk=session_pk)
        user = User.objects.get(pk=user_pk)
    except Exception as e:
        logger.warning("_update_brain_async: session or user not found: %s", e)
        return

    current = EspejoMemoria.objects.filter(user=user, activa=True).first()
    cerebro_actual = current.contenido if current else "(Sin cerebro previo.)"

    messages_raw = session.messages or []
    if len(messages_raw) < 4:
        return  # sesión demasiado corta para aprender algo

    transcripcion = "\n".join(
        f"{m['role'].upper()}: {m['content'][:300]}"
        for m in messages_raw[-20:]  # last 20 exchanges max
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_BRAIN_UPDATE},
            {"role": "user", "content": f"CEREBRO ACTUAL:\n{cerebro_actual}\n\nSESIÓN RECIENTE:\n{transcripcion}"},
        ],
        "temperature": 0.5,
        "max_tokens": 800,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=45,
        )
        resp.raise_for_status()
        data = json.loads(resp.json()["choices"][0]["message"]["content"])
        nuevo_contenido = data.get("cerebro", "").strip()
        if nuevo_contenido and len(nuevo_contenido) > 50:
            _nueva_version_cerebro(user, nuevo_contenido, fuente='sesion', sesion=session)
            # Credit patron_nombrado mission if brain has real patterns
            m_check = re.search(r'## Patrones que he notado(.*?)(?=\n## |\Z)', nuevo_contenido, re.DOTALL)
            if m_check and '(Aún sin' not in m_check.group(1) and m_check.group(1).strip():
                from tokens.service import credit_mission
                credit_mission(user, 'patron_nombrado')
    except Exception as e:
        logger.warning("_update_brain_async failed for user %s: %s", user_pk, e)


# ── DeepSeek call ─────────────────────────────────────────────────────────────

def _call_deepseek_json(messages, kb_context, test_context, brain_context='', mode="open", enfoque=None):
    """Calls DeepSeek and returns (parsed_dict, error). Always requests JSON."""
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return None, "DEEPSEEK_API_KEY no configurada en .env"

    kb_text = "\n\n---\n\n".join(kb_context)

    if mode == "focused" and enfoque:
        enfoque_id = enfoque.get("id", "")
        marco = ENFOQUE_MARCOS.get(enfoque_id, "Marco endonauta general")
        system = SYSTEM_FOCUSED.format(
            marco_endonauta=MARCO_ENDONAUTA,
            enfoque_titulo=enfoque.get("titulo", ""),
            marco_teorico=marco,
            contexto_kb=kb_text,
            test_context=test_context + brain_context,
        )
    else:
        system = SYSTEM_OPEN.format(
            marco_endonauta=MARCO_ENDONAUTA,
            contexto_kb=kb_text,
            test_context=test_context + brain_context,
        )

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0.75,
        "max_tokens": 900,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=35,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: wrap raw text as plain texto
            parsed = {"texto": raw, "enfoques": None, "test_recomendado": None}

        return parsed, None

    except requests.exceptions.Timeout:
        return None, "El espejo tardó demasiado en responder. Intenta de nuevo."
    except Exception as e:
        return None, str(e)


# ── Helpers de engagement ─────────────────────────────────────────────────────

def _extract_closing_question(messages):
    for msg in reversed(messages):
        if msg.get('role') == 'assistant':
            text = msg.get('content', '')
            sentences = re.split(r'(?<=[.!?])\s+', text)
            questions = [s.strip() for s in sentences if s.strip().endswith('?')]
            if questions:
                return questions[-1]
    return ""


# ── Views ─────────────────────────────────────────────────────────────────────

@login_required
def espejo_home(request):
    sessions = ConflictSession.objects.filter(user=request.user).order_by("-updated_at")[:10]
    session_id = request.GET.get("sesion")

    active = None
    if session_id:
        active = get_object_or_404(ConflictSession, pk=session_id, user=request.user)
    elif sessions.exists():
        active = sessions.first()

    from datetime import timedelta
    from django.utils import timezone as _tz
    hace_30 = _tz.now() - timedelta(days=30)
    hace_40 = _tz.now() - timedelta(days=40)
    pregunta_retorno = ConflictSession.objects.filter(
        user=request.user, status='archived',
        pregunta_cierre__gt='',
        updated_at__range=(hace_40, hace_30),
    ).first()

    return render(request, "mirror/espejo.html", {
        "sessions": sessions,
        "active": active,
        "pregunta_retorno": pregunta_retorno,
    })


@login_required
@require_POST
def espejo_nuevo(request):
    sesion = ConflictSession.objects.create(
        user=request.user,
        conflict_description="",
        title="Nueva conversación",
    )
    return redirect(f"/espejo/?sesion={sesion.pk}")


@login_required
@require_POST
def espejo_send(request):
    """AJAX: recibe mensaje del usuario, llama a DeepSeek con RAG, devuelve respuesta estructurada."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    user_msg = (data.get("mensaje") or "").strip()
    session_id = data.get("sesion_id")
    enfoque = data.get("enfoque")  # dict con id/titulo/descripcion si el usuario eligió un camino

    if not user_msg:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    if session_id:
        sesion = get_object_or_404(ConflictSession, pk=session_id, user=request.user)
    else:
        sesion = ConflictSession.objects.create(
            user=request.user,
            conflict_description=user_msg[:200],
            title=user_msg[:60],
        )

    if not sesion.messages:
        sesion.title = user_msg[:60]
        sesion.conflict_description = user_msg[:500]

    # Almacenar mensaje del usuario (con metadata de enfoque si aplica)
    user_msg_entry = {"role": "user", "content": user_msg}
    if enfoque:
        user_msg_entry["enfoque_id"] = enfoque.get("id")
    sesion.messages.append(user_msg_entry)
    sesion.save()

    # RAG: recuperar contexto relevante
    query_for_rag = user_msg
    if enfoque:
        # Enriquecer la query con el enfoque elegido para mejor retrieval
        query_for_rag = f"{user_msg} {enfoque.get('titulo', '')} {ENFOQUE_MARCOS.get(enfoque.get('id', ''), '')[:100]}"

    kb_chunks = _retrieve_context(query_for_rag, k=5)

    # Contexto de tests del usuario
    test_context = _get_test_context(request.user)

    # Historial para DeepSeek (solo role + content, últimos 14 mensajes)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in sesion.messages[-14:]
    ]

    # Determinar modo
    mode = "focused" if enfoque else "open"

    # Recopilar contexto cerebro antes de cerrar la conexión
    brain_context = _get_brain_context(request.user)
    is_first_exchange = len(sesion.messages) <= 2

    # Cerrar la conexión DB antes del API call largo — evita NO_SOCKET/TCP_ABORT en Railway
    # (Railway mata conexiones Postgres idle durante los 20-60s que tarda DeepSeek)
    from django.db import connection as _db_conn
    _db_conn.close()

    # Llamar a DeepSeek (Django reabre la conexión automáticamente al guardar después)
    parsed, error = _call_deepseek_json(history, kb_chunks, test_context, brain_context=brain_context, mode=mode, enfoque=enfoque)

    if error:
        return JsonResponse({"error": error}, status=503)

    texto = parsed.get("texto") or ""
    enfoques = parsed.get("enfoques")
    test_rec = parsed.get("test_recomendado")

    # Deducir fractones solo si la API respondió correctamente
    from tokens.service import spend, credit_mission, has_balance
    if not has_balance(request.user, 'espejo_exchange'):
        return JsonResponse({"error": "Fractones insuficientes."}, status=402)
    spend(request.user, 'espejo_exchange')
    if is_first_exchange:
        credit_mission(request.user, 'first_espejo')

    # Guardar respuesta del asistente
    sesion.add_message("assistant", texto)

    return JsonResponse({
        "respuesta": texto,
        "enfoques": enfoques if isinstance(enfoques, list) else None,
        "test_recomendado": test_rec if isinstance(test_rec, dict) else None,
        "sesion_id": sesion.pk,
        "sesion_titulo": sesion.title,
    })


@login_required
@require_POST
def espejo_archivar(request, pk):
    sesion = get_object_or_404(ConflictSession, pk=pk, user=request.user)
    sesion.status = "archived"
    if not sesion.pregunta_cierre:
        q = _extract_closing_question(sesion.messages or [])
        if q:
            sesion.pregunta_cierre = q
    sesion.save(update_fields=["status", "pregunta_cierre"])
    threading.Thread(
        target=_update_brain_async,
        args=[sesion.pk, request.user.pk],
        daemon=True,
    ).start()
    return redirect("/espejo/")


@login_required
def espejo_tarjetas(request):
    """Returns pending and revealed insight cards for the Espejo panel."""
    cards = []

    # Test result insights
    results = (
        TestResult.objects.filter(user=request.user)
        .select_related("test")
        .order_by("-completed_at")
    )
    for r in results:
        if r.ai_insight == "processing":
            status = "processing"
        elif r.ai_insight and r.ai_insight != "—":
            status = "revealed"
        else:
            status = "pending"
        cards.append({
            "id": f"test-{r.pk}",
            "type": "test",
            "title": r.test.name,
            "date": r.completed_at.strftime("%d %b %Y") if r.completed_at else "",
            "status": status,
            "url": f"/psicometria/resultado/{r.pk}/lectura/",
        })

    # Birth report insights
    birth_labels = {
        BirthReport.TYPE_ASTRAL: "Carta Astral",
        BirthReport.TYPE_HD:     "Diseño Humano",
        BirthReport.TYPE_SAJU:   "Saju",
    }
    birth_paths = {
        BirthReport.TYPE_ASTRAL: "astral",
        BirthReport.TYPE_HD:     "hd",
        BirthReport.TYPE_SAJU:   "saju",
    }
    reports = BirthReport.objects.filter(user=request.user).order_by("-updated_at")
    for rep in reports:
        if rep.interpretation == "processing":
            status = "processing"
        elif rep.interpretation and rep.interpretation != "processing":
            status = "revealed"
        else:
            status = "pending"
        path = birth_paths.get(rep.report_type, rep.report_type)
        cards.append({
            "id": f"birth-{rep.pk}",
            "type": "birth",
            "subtype": rep.report_type,
            "title": birth_labels.get(rep.report_type, rep.report_type),
            "date": rep.updated_at.strftime("%d %b %Y") if rep.updated_at else "",
            "status": status,
            "url": f"/nacimiento/reporte/{rep.pk}/{path}/lectura/",
        })

    pending  = [c for c in cards if c["status"] in ("pending", "processing")]
    revealed = [c for c in cards if c["status"] == "revealed"]
    return JsonResponse({"pending": pending, "revealed": revealed, "total": len(cards)})


@login_required
def espejo_cerebro(request):
    _seed_initial_brain(request.user)
    versiones = EspejoMemoria.objects.filter(user=request.user).order_by('-version')
    activa = versiones.filter(activa=True).first()
    return render(request, 'mirror/espejo_cerebro.html', {
        'versiones': versiones,
        'activa': activa,
    })


@login_required
@require_POST
def espejo_cerebro_restaurar(request, pk):
    from django.db import transaction
    mem = get_object_or_404(EspejoMemoria, pk=pk, user=request.user)
    with transaction.atomic():
        ultima = EspejoMemoria.objects.filter(user=request.user).order_by('-version').first()
        nueva_v = ultima.version + 1
        EspejoMemoria.objects.filter(user=request.user, activa=True).update(activa=False)
        EspejoMemoria.objects.create(
            user=request.user,
            version=nueva_v,
            contenido=mem.contenido,
            activa=True,
            fuente='restauracion',
            sesion_origen=None,
        )
    return redirect('mirror:cerebro')


@login_required
@require_POST
def espejo_cerebro_actualizar(request):
    sesion_pk = request.POST.get('sesion_pk')
    if sesion_pk:
        session = get_object_or_404(ConflictSession, pk=sesion_pk, user=request.user)
        threading.Thread(
            target=_update_brain_async,
            args=[session.pk, request.user.pk],
            daemon=True,
        ).start()
        return JsonResponse({'ok': True, 'mensaje': 'Actualizando memoria…'})
    return JsonResponse({'error': 'sesion_pk requerido'}, status=400)
