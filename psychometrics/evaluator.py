def evaluate_test(test_name, details):
    """
    Procesa los puntajes crudos y los enriquece con análisis clínico,
    porcentajes y una conclusión endonáutica.
    """
    enriched = {
        "dimensiones": [],
        "conclusion": "",
        "overall_score": sum(details.values()) if details else 0
    }

    if not details:
        return enriched

    if 'Big Five' in test_name:
        enriched = _eval_big_five(details)
    elif 'Jung' in test_name:
        enriched = _eval_jung(details)
    elif 'Eneagrama' in test_name:
        enriched = _eval_eneagrama(details)
    elif 'GAD-7' in test_name or 'Ansiedad' in test_name:
        enriched = _eval_gad7(details)
    elif 'PHQ-9' in test_name or 'Salud del Paciente' in test_name:
        enriched = _eval_phq9(details)
    elif 'Pittsburgh' in test_name or 'PSQI' in test_name:
        enriched = _eval_psqi(details)
    elif 'Estrés' in test_name and 'PSS-10' in test_name:
        enriched = _eval_pss10(details)
    elif 'Consciencia Interoceptiva' in test_name or 'MAIA' in test_name:
        enriched = _eval_maia(details)
    elif 'Neurosensorial' in test_name:
        enriched = _eval_neurosensorial(details)
    elif 'Vitalidad Subjetiva' in test_name or 'SVI' in test_name:
        enriched = _eval_svi(details)
    elif 'Experiencias en Relaciones' in test_name or 'ECR' in test_name:
        enriched = _eval_ecr(details)
    elif 'Heridas de la Infancia' in test_name:
        enriched = _eval_heridas(details)
    elif 'Creencias Irracionales' in test_name or 'IBI' in test_name:
        enriched = _eval_ibi(details)
    elif 'Autosabotaje' in test_name:
        enriched = _eval_autosabotaje(details)
    elif 'Tríada Oscura' in test_name or 'SD3' in test_name or 'Dirty Dozen' in test_name:
        enriched = _eval_dirty_dozen(details)
    elif 'Alexitimia' in test_name or 'TAS-20' in test_name:
        enriched = _eval_tas20(details)
    elif 'Regulación Emocional' in test_name or 'DERS' in test_name:
        enriched = _eval_ders(details)
    elif 'Perfil de Chakras' in test_name:
        enriched = _eval_chakras(details)
    elif 'Bienestar Espiritual' in test_name or 'SWB' in test_name:
        enriched = _eval_swb(details)
    elif 'Trascendencia' in test_name or 'Cloninger' in test_name:
        enriched = _eval_cloninger(details)
    elif 'Logo-Test' in test_name:
        enriched = _eval_logotest(details)
    elif 'Recuerdo Onírico' in test_name or 'DRI' in test_name:
        enriched = _eval_dri_das(details)
    elif 'Lucidez' in test_name or 'DLQ' in test_name:
        enriched = _eval_lucidez(details)
    elif 'VIA' in test_name:
        enriched = _eval_via(details)
    elif 'RIASEC' in test_name or 'Holland' in test_name:
        enriched = _eval_riasec(details)
    elif 'MWQ' in test_name or 'Sentido del Trabajo' in test_name:
        enriched = _eval_mwq(details)
    elif 'Kolb' in test_name:
        enriched = _eval_kolb(details)
    elif 'Curiosidad Epistémica' in test_name or 'CEQ' in test_name:
        enriched = _eval_ceq(details)
    elif 'Apoyo Social' in test_name or 'MOS-SSS' in test_name:
        enriched = _eval_comunidad(details)
    elif 'Fortalezas Prosociales' in test_name:
        enriched = _eval_comunicacion(details)
    elif 'Actitudes hacia el Dinero' in test_name or 'MAQ' in test_name:
        enriched = _eval_maq(details)
    elif 'Estrés Financiero' in test_name or 'FSS' in test_name:
        enriched = _eval_fss(details)
    elif 'Identidad Creativa' in test_name or 'CIQ' in test_name:
        enriched = _eval_creatividad(details)
    elif 'Rueda de la Vida' in test_name:
        enriched = _eval_integracion(details)
    elif 'Coherencia' in test_name or 'SOC-29' in test_name:
        enriched = _eval_soc29(details)
    else:
        enriched = _eval_generic(details)

    return enriched


# ─────────────────────────────────────────────────────────────────────
# LÓGICA DE DUALIDAD SOMBRA / LUZ
# ─────────────────────────────────────────────────────────────────────

def _get_polarity(dim, pct, es_interferencia=False):
    """
    Lógica de dualidad sombra/luz del método endonauta.

    es_interferencia=False → puntaje alto es LUZ (capacidad, fortaleza)
    es_interferencia=True  → puntaje alto es SOMBRA (patrón inconsciente)

    La sombra no es el enemigo — es un patrón sin integrar.
    """
    if es_interferencia:
        if pct <= 25:
            return (
                'luz',
                'Patrón integrado. Baja activación de esta interferencia.',
                'Mantén la observación. La integración no es ausencia — es elección consciente.'
            )
        elif pct <= 55:
            return (
                'transición',
                'Patrón latente. Emerge bajo estrés o en relaciones íntimas.',
                'Observa cuándo se activa este patrón. El disparador es el mapa.'
            )
        elif pct <= 75:
            return (
                'sombra',
                'Patrón activo. Opera con frecuencia, a veces sin que lo notes.',
                'Nombra el patrón cada vez que aparezca. Nombrarlo es el primer acto de integración.'
            )
        else:
            return (
                'sombra_dominante',
                'Patrón dominante. Estructura gran parte de tu forma de relacionarte y decidir.',
                'Este es tu trabajo más profundo. No para eliminarlo — para conocerlo tan bien que deje de controlarte.'
            )
    else:
        if pct <= 20:
            return (
                'sombra',
                'Capacidad suprimida o subdesarrollada. Puede estar bloqueada por miedo o historia.',
                'Esta dimensión pide atención. No como defecto — como territorio inexplorado.'
            )
        elif pct <= 45:
            return (
                'transición',
                'Capacidad emergente. Disponible pero inconsistente bajo presión.',
                'Ejercita esta dimensión intencionalmente. La inconsistencia es señal de que el músculo está creciendo.'
            )
        elif pct <= 80:
            return (
                'luz',
                'Capacidad activa e integrada. Opera con fluidez en tu vida.',
                'Úsala conscientemente. Una fortaleza que no se elige puede volverse automática y rígida.'
            )
        else:
            return (
                'luz_intensa',
                'Capacidad muy alta. Fortaleza dominante — también puede ser zona de confort excesiva.',
                'Pregúntate: ¿estás eligiendo esta fortaleza o dependiendo de ella? La maestría incluye saber cuándo no usarla.'
            )


def _dim_entry(nombre, score, max_score, nivel=None, analisis='', descripcion='',
               polaridad=None, mensaje_polaridad='', accion_sugerida=''):
    pct = min((score / max_score) * 100, 100) if max_score > 0 else 0
    entry = {
        'nombre': nombre,
        'puntos': score,
        'max': max_score,
        'pct': pct,
        'nivel': nivel or '',
        'analisis': analisis,
        'descripcion': descripcion,
    }
    if polaridad:
        entry['polaridad'] = polaridad
        entry['mensaje_polaridad'] = mensaje_polaridad
        entry['accion_sugerida'] = accion_sugerida
    return entry


# ─────────────────────────────────────────────────────────────────────
# BIG FIVE — BFI-44 (John, Donahue & Kentle, 1991)
# Escala: 1-5 | Ítems: 8-10 por dimensión
# Max scores: E=40, A=45, C=45, N=40, O=50
# ─────────────────────────────────────────────────────────────────────

def _eval_big_five(details):
    max_scores = {
        'Extraversión':     40,  # 8 ítems × 5
        'Amabilidad':       45,  # 9 ítems × 5
        'Responsabilidad':  45,  # 9 ítems × 5
        'Neuroticismo':     40,  # 8 ítems × 5
        'Apertura':         50   # 10 ítems × 5
    }
    desc_teoricas = {
        'Extraversión': "Orientación de la energía hacia el mundo exterior vs. interior. Biológicamente asociada a la sensibilidad dopaminérgica ante la recompensa social.",
        'Amabilidad': "Tendencia a la compasión y cooperación vs. competitividad y escepticismo. Evolutivamente equilibra altruismo grupal con supervivencia individual.",
        'Responsabilidad': "Control de impulsos, planificación y orientación a metas. Vinculada al funcionamiento de la corteza prefrontal y la tolerancia a la gratificación diferida.",
        'Neuroticismo': "Sensibilidad del sistema nervioso a estímulos negativos. Mide la reactividad emocional ante el estrés, la ansiedad y la incertidumbre.",
        'Apertura': "Permeabilidad psíquica a nuevas ideas, experiencias estéticas y conceptos abstractos. Se correlaciona con creatividad y pensamiento lateral."
    }
    analysis_texts = {
        'Extraversión': [
            "Tu puntaje indica un rasgo predominantemente introvertido. Eres reservado, reflexivo e independiente. El riesgo es el aislamiento extremo; el don es tu profunda capacidad de observación.",
            "Posees una extraversión ambivertida. Disfrutas tanto del tiempo a solas como de la interacción social, adaptándote bien al contexto.",
            "Altamente extravertido/a. Eres sociable, enérgico y orientado al mundo exterior. Tu don es la acción grupal; tu desafío, aprender a sostener el silencio."
        ],
        'Amabilidad': [
            "Baja amabilidad. Eres competitivo, directo, crítico y escéptico. Priorizas la lógica sobre la armonía del grupo. Eres difícil de engañar, pero podrías parecer frío.",
            "Punto medio saludable. Sabes cuándo cooperar y cuándo defender tus límites con firmeza.",
            "Alta amabilidad. Eres compasivo, cooperativo y confías en los demás. El riesgo es sacrificar tus propias necesidades para no incomodar."
        ],
        'Responsabilidad': [
            "Nivel bajo. Eres espontáneo, flexible y prefieres improvisar. Toleras el desorden, pero podrías sufrir de procrastinación crónica.",
            "Nivel adecuado. Capaz de cumplir metas sin obsesionarte con el orden absoluto.",
            "Muy alta. Altamente disciplinado, eficiente y estructurado. Alcanzas metas fácilmente, pero puedes llegar a ser rígido."
        ],
        'Neuroticismo': [
            "Bajo neuroticismo (alta estabilidad). Emocionalmente resiliente, calmado y resistente al estrés.",
            "Reactividad emocional promedio. Logras volver a tu centro emocional sin que el estrés te paralice prolongadamente.",
            "Alto neuroticismo. Muy sensible a estímulos. Tu sistema nervioso actúa como un radar ultra-sensible; tu tarea es el enraizamiento somático."
        ],
        'Apertura': [
            "Baja apertura. Práctico, tradicional, prefieres lo familiar. La rutina y los hechos probados te dan seguridad.",
            "Apertura equilibrada. Abierto a la novedad pero mantienes un pie en la realidad práctica.",
            "Apertura muy alta. Profundamente imaginativo, curioso y poco convencional. Tu desafío no es generar ideas, sino aterrizarlas."
        ]
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_scores.get(dim, 50)
        t1, t2 = max_s * 0.33, max_s * 0.66
        pct = min((score / max_s) * 100, 100)
        if score <= t1:
            idx, nivel = 0, 'Bajo'
        elif score <= t2:
            idx, nivel = 1, 'Medio'
        else:
            idx, nivel = 2, 'Alto'
        txts = analysis_texts.get(dim, ['', '', ''])
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'nivel': nivel, 'analisis': txts[idx],
            'descripcion': desc_teoricas.get(dim, '')
        })
    if dimensiones:
        sd = sorted(dimensiones, key=lambda x: x['pct'])
        conclusion = (f"Tu rasgo dominante ({sd[-1]['nombre']}) es tu mayor ventaja evolutiva y también tu zona de confort automática. "
                      f"Tu puntaje más bajo en {sd[0]['nombre']} señala tu territorio de sombra o área subdesarrollada. "
                      "En la práctica endonáutica buscamos volverte elástico/a: usar tu fortaleza como herramienta consciente e integrar "
                      "la energía de la dimensión más baja cuando la situación lo requiera.")
    else:
        conclusion = "El perfil de los Cinco Grandes revela la arquitectura de tu ego cotidiano."
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# JUNG — adaptación MBTI (no validada psicométricamente como la MBTI)
# Escala: 1-5 | 3 ítems por dimensión | max real = 15 por dimensión
# NOTA: versión screening. MBTI oficial tiene 93+ ítems.
# ─────────────────────────────────────────────────────────────────────

def _eval_jung(details):
    # max real: 3 ítems × 5 = 15
    MAX_PER_DIM = 15
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        es_extremo = pct > 87 or pct < 13  # ≥13/15 o ≤2/15
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=es_extremo)
        nivel = "Preferencia Clara" if pct > 70 or pct < 30 else "Equilibrado"
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': f"Función {dim.lower()}.",
            'analisis': "Orientación psicológica junguiana."
        })
    return {
        "dimensiones": dimensiones,
        "conclusion": ("La tipología de Jung nos enseña que el equilibrio no es ser 'un poco de todo', "
                       "sino conocer nuestras funciones dominantes e integrar las inferiores (la sombra) "
                       "para alcanzar la individuación. ⚠️ Screening de 3 ítems — orientativo.")
    }


# ─────────────────────────────────────────────────────────────────────
# ENEAGRAMA (modelo de Riso-Hudson — no validado psicométricamente)
# Escala: 1-5 | 1 ítem por tipo | max real = 5 por tipo
# NOTA: 1 ítem por tipo tiene confiabilidad muy baja. Solo orientativo.
# ─────────────────────────────────────────────────────────────────────

def _eval_eneagrama(details):
    # max real: 1 ítem × 5 = 5
    MAX_PER_DIM = 5
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        es_fijacion = pct >= 80
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=es_fijacion)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol,
            'mensaje_polaridad': "Fuerte identificación con este eneatipo." if es_fijacion else "Energía disponible.",
            'accion_sugerida': "Desidentificación del ego / trabajo con la pasión" if es_fijacion else "Desarrollo de virtudes",
            'nivel': "Dominante" if pct >= 80 else "Influencia",
            'descripcion': f"Eneatipo {dim}.",
            'analisis': "Mapa de la personalidad egoica."
        })
    return {
        "dimensiones": dimensiones,
        "conclusion": ("El eneagrama describe las 9 formas de 'olvidar' quiénes somos. Tu tipo dominante es tu mayor "
                       "talento (Luz) y tu mayor trampa (Sombra). El camino es pasar de la compulsión a la consciencia. "
                       "⚠️ Screening de 1 ítem por tipo — solo indicativo.")
    }


# ─────────────────────────────────────────────────────────────────────
# GAD-7 (Spitzer et al., 2006)
# Escala: 0-3 (likert3) | 7 ítems | Max = 21
# Corte: 0-4 mínima, 5-9 leve, 10-14 moderada, 15-21 severa
# ─────────────────────────────────────────────────────────────────────

def _eval_gad7(details):
    score = sum(details.values())
    max_s = 21  # 7 ítems × 3
    pct = min((score / max_s) * 100, 100)
    if score <= 4:
        nivel, txt = "Mínima", "Tus niveles de ansiedad están dentro de un rango saludable y manejable."
    elif score <= 9:
        nivel, txt = "Leve", "Experimentas cierta ansiedad que podría beneficiarse de prácticas de mindfulness y arraigo."
    elif score <= 14:
        nivel, txt = "Moderada", "La ansiedad está afectando tu bienestar. Es importante integrar herramientas de regulación nerviosa."
    else:
        nivel, txt = "Severa", "Experimentas un alto grado de ansiedad. Se sugiere priorizar el trabajo de regulación somática y apoyo profesional."
    dimensiones = [{
        'nombre': 'Nivel de Ansiedad (GAD-7)', 'puntos': score, 'max': max_s, 'pct': pct,
        'nivel': nivel,
        'descripcion': "Mide la presencia clínica de preocupación excesiva, inquietud motora y activación simpática generalizada (Spitzer et al., 2006).",
        'analisis': txt
    }]
    conclusion = ("La ansiedad no es un error de tu sistema — es una señal. En términos endonáuticos, la ansiedad crónica "
                  "suele indicar que el sistema nervioso ha perdido su sentido de seguridad. El trabajo no es eliminar la ansiedad "
                  "luchando contra ella, sino descender al cuerpo y devolverle la certeza somática de que estás a salvo.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# PHQ-9 — Patient Health Questionnaire-9 (Kroenke & Spitzer, 2001)
# Escala: 0-3 (likert3) | 9 ítems | Max = 27
# Cutoffs: 0-4 mínimo, 5-9 leve, 10-14 moderado, 15-19 moderado-severo, 20-27 severo
# Libre de derechos de autor. Validado en español.
# ─────────────────────────────────────────────────────────────────────

def _eval_phq9(details):
    score = sum(details.values())
    max_s = 27  # 9 ítems × 3
    pct = min((score / max_s) * 100, 100)
    if score <= 4:
        nivel, txt = "Mínimo", "Sin indicadores clínicamente relevantes de depresión."
    elif score <= 9:
        nivel, txt = "Leve", "Síntomas leves presentes. Seguimiento recomendado y atención a hábitos de autocuidado."
    elif score <= 14:
        nivel, txt = "Moderado", "Síntomas moderados que impactan el funcionamiento. Se sugiere evaluación clínica."
    elif score <= 19:
        nivel, txt = "Moderado-Severo", "Síntomas importantes. Consulta con profesional de salud mental recomendada."
    else:
        nivel, txt = "Severo", "Síntomas severos. Evaluación clínica urgente recomendada."
    dimensiones = [{
        'nombre': 'Indicadores Depresivos (PHQ-9)', 'puntos': score, 'max': max_s, 'pct': pct,
        'nivel': nivel,
        'descripcion': "Mide la presencia y severidad de síntomas depresivos basados en criterios DSM (Kroenke & Spitzer, 2001). Instrumento validado en español.",
        'analisis': txt
    }]
    conclusion = ("La depresión a menudo funciona como un mecanismo de apagado del sistema biológico cuando hemos estado "
                  "luchando o rindiendo demasiado tiempo. En términos endonáuticos, la melancolía profunda suele ser una llamada "
                  "del alma a retirar la energía del mundo exterior para reparar el mundo interior. "
                  "Si presentas pensamientos de hacerte daño (ítem 9), busca apoyo profesional de inmediato.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# PSS-10 (Cohen, Kamarck & Mermelstein, 1983)
# Escala: 0-4 (likert4) | 10 ítems | Max = 40
# Ítems positivos (reverse): 4, 5, 6, 7, 9 → ya aplicados en views.py
# Corte: 0-13 bajo, 14-26 moderado, 27-40 alto
# ─────────────────────────────────────────────────────────────────────

def _eval_pss10(details):
    score = sum(details.values())
    max_s = 40  # 10 ítems × 4
    pct = min((score / max_s) * 100, 100)
    if score <= 13:
        nivel, txt = "Bajo", "Tu nivel de estrés percibido es bajo. Tienes una buena sensación de control sobre las demandas de tu vida."
    elif score <= 26:
        nivel, txt = "Moderado", "Experimentas un estrés moderado. Las demandas de la vida a veces superan tu capacidad percibida para manejarlas."
    else:
        nivel, txt = "Alto", "Tu nivel de estrés percibido es alto. Es prioritario implementar herramientas de regulación y evaluar cargas externas."
    dimensiones = [{
        'nombre': 'Estrés Percibido (PSS-10)', 'puntos': score, 'max': max_s, 'pct': pct,
        'nivel': nivel,
        'descripcion': "Mide el grado en que las situaciones de la vida se evalúan como abrumadoras, impredecibles o incontrolables (Cohen et al., 1983).",
        'analisis': txt
    }]
    conclusion = ("El estrés no es lo que te sucede, sino cómo tu biología y psicología interpretan lo que te sucede "
                  "frente a los recursos que crees tener. El trabajo endonáutico invita a desplazar el foco desde el control "
                  "de lo externo hacia el anclaje somático interno.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# PSQI (Buysse et al., 1989) — versión simplificada
# Escala: 0-3 (likert3) | Componentes scored 0-3 (mayor = peor)
# Max real por componente: 1 ítem × 3 = 3; 2 ítems × 3 = 6
# NOTA: el PSQI completo (19 ítems) tiene algoritmo de puntuación complejo.
# Esta versión usa 9 ítems agrupados en componentes; interpretación orientativa.
# ─────────────────────────────────────────────────────────────────────

def _eval_psqi(details):
    # max por componente según ítems reales en seed con escala likert3 (0-3)
    maximos = {
        'Calidad Subjetiva': 3,   # 1 ítem × 3
        'Latencia':          6,   # 2 ítems × 3
        'Duración':          3,   # 1 ítem × 3
        'Perturbaciones':    6,   # 2 ítems × 3
        'Medicación':        3,   # 1 ítem × 3
        'Disfunción diurna': 6,   # 2 ítems × 3
    }
    descripciones = {
        'Calidad Subjetiva': 'Tu propia percepción de la capacidad restauradora de tu sueño.',
        'Latencia': 'Tiempo que tarda tu sistema nervioso en hacer la transición vigilia→sueño.',
        'Duración': 'Horas de sueño efectivo (reparación celular y poda sináptica).',
        'Perturbaciones': 'Micro-despertares por estrés biológico, ambiental o psíquico.',
        'Medicación': 'Dependencia exógena para inducir el sueño.',
        'Disfunción diurna': 'Impacto de la falta de recuperación nocturna en tu vitalidad diurna.',
    }
    dimensiones = []
    worst_dim, worst_pct = None, -1
    for dim, score in details.items():
        max_s = maximos.get(dim, 3)
        pct = min((score / max_s) * 100, 100) if max_s > 0 else 0
        salud_pct = 100 - pct  # invertido: mayor pct = peor → mostrar como "salud"
        if pct <= 25:
            nivel, analisis = "Óptimo", "No presentas alteraciones significativas en esta dimensión."
        elif pct <= 50:
            nivel, analisis = "Leve", "Hay cierta alteración ligera que podría beneficiarse de ajustes en tu higiene de sueño."
        elif pct <= 75:
            nivel, analisis = "Moderado", "La desregulación en esta área está afectando tu arquitectura de sueño."
        else:
            nivel, analisis = "Severo", "Esta área presenta una interrupción severa que requiere intervención o cambios conductuales radicales."
        dimensiones.append({
            'nombre': dim, 'puntos': max_s - score, 'max': max_s,
            'pct': salud_pct, 'nivel': nivel,
            'descripcion': descripciones.get(dim, ''), 'analisis': analisis
        })
        if pct > worst_pct:
            worst_pct = pct
            worst_dim = dim

    conclusion = f"El sueño es el taller de reparación de tu biología. Tu mayor debilidad estructural nocturna es '{worst_dim}'. "
    if worst_dim in ("Latencia", "Disfunción diurna"):
        conclusion += "Esto sugiere que tu problema de sueño no es 'de la noche', sino del 'día'. Tu sistema nervioso no logra apagar el tono simpático. ⚠️ Versión simplificada — el PSQI completo requiere 19 ítems y algoritmo específico."
    else:
        conclusion += "El trabajo endonáutico dicta que la noche es el espejo del día. Ajustar tu ritmo circadiano y tu anclaje a la seguridad corporal es el primer paso. ⚠️ Versión simplificada del PSQI completo."
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# MAIA-2 (Mehling et al., 2018) — versión de 21 ítems
# Escala: 1-5 (likert5) | ítems por subscala variables
# Max real por subscala: 3 ítems × 5 = 15; 2 ítems × 5 = 10
# ─────────────────────────────────────────────────────────────────────

def _eval_maia(details):
    # Ítems por subscala en el seed (conteo real)
    max_por_subscala = {
        'Notar':               15,  # 3 ítems × 5
        'No-Distracción':      15,  # 3 ítems × 5 (reverse)
        'No-Preocupación':     10,  # 2 ítems × 5 (reverse)
        'Atención':            15,  # 3 ítems × 5
        'Consciencia Emocional': 15,  # 3 ítems × 5
        'Auto-regulación':     15,  # 3 ítems × 5
        'Escucha Corporal':    10,  # 2 ítems × 5
        'Confianza':           10,  # 2 ítems × 5
    }
    descripciones = {
        'Notar': 'Consciencia de sensaciones corporales incómodas, confortables y neutrales.',
        'No-Distracción': 'Tendencia a no ignorar o distraerse de las sensaciones de dolor o malestar.',
        'No-Preocupación': 'Tendencia a no experimentar angustia emocional con las sensaciones dolorosas.',
        'Atención': 'Capacidad de sostener y controlar la atención en sensaciones corporales.',
        'Consciencia Emocional': 'Consciencia de la conexión entre sensaciones corporales y estados emocionales.',
        'Auto-regulación': 'Habilidad para regular el malestar psicológico mediante la atención al cuerpo.',
        'Escucha Corporal': 'Escucha activa del cuerpo como fuente de introspección.',
        'Confianza': 'Experimentar el propio cuerpo como seguro y confiable.'
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_subscala.get(dim, 15)
        pct = min((score / max_s) * 100, 100)
        if pct <= 33:
            nivel, txt = "Desconexión", "Baja integración. Sugiere evitación o falta de entrenamiento en esta área."
        elif pct <= 66:
            nivel, txt = "Moderado", "Capacidad funcional, pero vulnerable bajo estrés."
        else:
            nivel, txt = "Alta Integración", "Excelente regulación y consciencia en esta área."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''), 'analisis': txt
        })
    conclusion = ("La interocepción es la base de toda inteligencia emocional. El MAIA no evalúa tu 'condición física', "
                  "sino cómo tu mente 'habita' tu cuerpo. Desarrollar consciencia interoceptiva es el primer paso "
                  "para desactivar las respuestas traumáticas y automáticas de tu sistema nervioso.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# PERFIL NEUROSENSORIAL — adaptación del Sensory Profile de Dunn (2014)
# Escala: 1-5 (likert5) | 2 ítems por cuadrante | max real = 10
# NOTA: adaptación de 8 ítems. Sensory Profile completo: 60 ítems.
# ─────────────────────────────────────────────────────────────────────

def _eval_neurosensorial(details):
    MAX_PER_DIM = 10  # 2 ítems × 5
    descripciones = {
        'Bajo Registro': 'El cerebro no percibe fácilmente los estímulos ambientales. Requiere intensidad para notar.',
        'Búsqueda Sensorial': 'El sistema anhela estimulación y la busca activamente para mantenerse alerta.',
        'Sensibilidad Sensorial': 'Respuestas intensas a estímulos comunes. Los estímulos se perciben rápidamente y abruman.',
        'Evitación Sensorial': 'Saturación rápida que lleva a bloquear o alejarse de los estímulos.'
    }
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        if pct <= 33:
            nivel, txt = "Poco probable", "No exhibes este patrón neurosensorial de forma dominante."
        elif pct <= 66:
            nivel, txt = "Moderado", "Muestras este patrón de forma adaptativa."
        else:
            nivel, txt = "Muy probable", "Este patrón domina tu forma de procesar el mundo."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''), 'analisis': txt
        })
    conclusion = ("Tu perfil neurosensorial es tu 'hardware' original. Muchas personas creen que tienen 'problemas de ansiedad' "
                  "cuando en realidad tienen un sistema nervioso hiper-sensible. Entender tu perfil es el mapa técnico para "
                  "diseñar un entorno donde puedas prosperar. ⚠️ Screening de 8 ítems — orientativo.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# SVI — Subjective Vitality Scale (Ryan & Frederick, 1997)
# Escala: 1-7 (likert7) | 6 ítems | Max = 42
# Puntuación: media de ítems (1-7) o suma (6-42)
# ─────────────────────────────────────────────────────────────────────

def _eval_svi(details):
    score = sum(details.values())
    max_s = 42  # 6 ítems × 7
    pct = min((score / max_s) * 100, 100)
    if pct >= 75:
        nivel, txt = "Vibrante", "Tu nivel de vitalidad subjetiva es alto. Hay alineación entre tu energía interna y tu vida externa."
    elif pct >= 45:
        nivel, txt = "Media", "Vitalidad funcional. Hay energía disponible pero también zonas de fuga o resistencia interna."
    else:
        nivel, txt = "Agotada", "Tu nivel de vitalidad es bajo. Revisa dónde estás fugando energía emocional o actuando en contra de tus valores."
    pol, msg, acc = _get_polarity('Vitalidad', pct, es_interferencia=False)
    dimensiones = [{
        'nombre': 'Vitalidad Subjetiva', 'puntos': score, 'max': max_s, 'pct': pct,
        'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
        'nivel': nivel,
        'descripcion': "Sensación de estar vivo/a y con energía disponible (Ryan & Frederick, 1997). Escala 1-7, 6 ítems.",
        'analisis': txt
    }]
    conclusion = ("La vitalidad subjetiva es el termómetro de tu alineación interna. Cuando tu energía fluye sin resistencias "
                  "(conflictos, mentiras, represión), te sientes vital independientemente del cansancio físico. "
                  "Si te sientes agotado/a sin causa física, revisa dónde estás fugando energía emocional.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# ECR — Experiences in Close Relationships (Brennan et al., 1998)
# Escala: 1-7 (likert7) | 5 ítems Ansiedad + 5 Evitación | Max = 35 por dim
# Punto medio: 3.5/ítem → 5 ítems = 17.5 → umbral = 18
# Corte apego seguro: ambas dimensiones ≤ 18 (< punto medio)
# ─────────────────────────────────────────────────────────────────────

def _eval_ecr(details):
    MAX_PER_DIM = 35  # 5 ítems × 7
    descripciones = {
        'Ansiedad de Apego': 'El grado de preocupación por el abandono o rechazo, impulsando un comportamiento aferrado o dependiente.',
        'Evitación de Apego': 'El grado de incomodidad con la cercanía emocional, impulsando la hiper-independencia y el distanciamiento.'
    }
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        if pct <= 40:
            nivel, txt = "Bajo (Seguro)", "No presentas activación significativa de esta defensa."
        elif pct <= 70:
            nivel, txt = "Moderado", "Activación condicional ante estrés interpersonal."
        else:
            nivel, txt = "Alto (Inseguro)", "Fuerte mecanismo de defensa activo en tus relaciones."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''), 'analisis': txt
        })

    ansiedad = details.get('Ansiedad de Apego', 0)
    evitacion = details.get('Evitación de Apego', 0)
    UMBRAL = 18  # punto medio 3.5 × 5 ítems = 17.5 → redondeado a 18
    if ansiedad <= UMBRAL and evitacion <= UMBRAL:
        estilo = "Apego Seguro"
    elif ansiedad > UMBRAL and evitacion <= UMBRAL:
        estilo = "Apego Ansioso-Preocupado"
    elif ansiedad <= UMBRAL and evitacion > UMBRAL:
        estilo = "Apego Evitativo-Descartante"
    else:
        estilo = "Apego Temeroso-Evitativo (Desorganizado)"

    conclusion = (f"Basado en tus coordenadas, tu estilo predominante es {estilo}. "
                  "El apego es la estrategia de supervivencia que tu sistema nervioso infantil desarrolló para mantener cerca a tus cuidadores. "
                  "No es un rasgo inmutable. Reconocer tu estilo te permite hackearlo: si eres ansioso, aprende a auto-regular tu sistema; "
                  "si eres evitativo, aprende a tolerar la vulnerabilidad de la cercanía.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# HERIDAS DE LA INFANCIA (Bourbeau, 2003)
# Escala: 1-5 (likert5) | 4 ítems por herida | Max = 20 por herida
# NOTA: Instrumento no validado psicométricamente. Modelo terapéutico de Lise Bourbeau.
# ─────────────────────────────────────────────────────────────────────

def _eval_heridas(details):
    MAX_PER_DIM = 5  # 5 ítems × 1 (binary)

    INFO = {
        'Abandono': {
            'mascara': 'El Dependiente',
            'cuerpo': 'Postura blanda, busca contacto, se "derrumba" ante el abandono.',
            'sintomas_fisicos': 'Espalda baja, rodillas, riñones, tristeza crónica.',
            'descripcion': 'Miedo profundo a la soledad y a no ser sostenido/a. Aguanta relaciones dañinas por no quedarse solo/a.',
            'frases': ['Soy valioso/a.', 'Puedo cuidar de mí mismo/a.', 'Pongo límites sanos.', 'Tengo identidad propia.', 'Puedo tener relaciones libres.'],
        },
        'Rechazo': {
            'mascara': 'El Huidizo',
            'cuerpo': 'Cuerpo pequeño, delgado, tiende a hacerse invisible.',
            'sintomas_fisicos': 'Vías respiratorias (asma, rinitis), piel (eczema, psoriasis), pulmones.',
            'descripcion': 'La herida más profunda: afecta el derecho a existir. Se aísla antes de arriesgarse a ser rechazado/a.',
            'frases': ['Soy capaz y puedo hacerlo.', 'Soy aceptado/a y parte de.', 'Soy importante.', 'Yo pertenezco y me hago presente.'],
        },
        'Humillación': {
            'mascara': 'El Masoquista',
            'cuerpo': 'Redondo, sobrepeso, se protege con volumen.',
            'sintomas_fisicos': 'Sobrepeso, problemas digestivos, colon, tiroides lenta.',
            'descripcion': 'Vergüenza de sí mismo/a, del cuerpo y de sus necesidades. Se sacrifica por los demás anulándose.',
            'frases': ['Primero lo que yo necesito.', 'Respeto y acepto mi cuerpo.', 'Me siento orgulloso/a de…', 'Expreso lo que siento y necesito.'],
        },
        'Injusticia': {
            'mascara': 'El Rígido',
            'cuerpo': 'Erguido, rígido, perfectamente presentado.',
            'sintomas_fisicos': 'Espalda alta, columna, contracturas, piel (rigidez, frialdad).',
            'descripcion': 'No se reconoció su individualidad. Perfeccionismo y rigidez como escudo contra el dolor.',
            'frases': ['Me permito ser flexible y espontáneo/a.', 'Puedo equivocarme y respetarme.', 'Disfruto lo que hago.', 'Mis emociones las permito y cultivo.'],
        },
        'Traición': {
            'mascara': 'El Controlador',
            'cuerpo': 'Fuerte, hombros expansivos, proyecta poder.',
            'sintomas_fisicos': 'Estómago, hígado, vesícula, contracturas de hombros, tensión crónica.',
            'descripcion': 'Alguien prometió y no cumplió. Controla el entorno para no volver a ser traicionado/a.',
            'frases': ['Yo elijo en quién confiar y suelto.', 'Controlo mi mente, no la vida de otros.', 'Tengo expectativas flexibles y realistas.', 'Sé recibir y a veces me equivoco.'],
        },
    }

    dimensiones = []
    herida_dominante = None
    max_score = -1

    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        if score >= 4:
            nivel = "Herida Activa"
        elif score >= 2:
            nivel = "Herida en Proceso"
        else:
            nivel = "Herida Latente"
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        info = INFO.get(dim, {})
        analisis = (
            f"Máscara: {info.get('mascara','—')}. "
            f"Cuerpo: {info.get('cuerpo','—')} "
            f"Síntomas físicos frecuentes: {info.get('sintomas_fisicos','—')}"
        )
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': info.get('descripcion', ''),
            'analisis': analisis,
            'frases_sanadoras': info.get('frases', []),
        })
        if score > max_score:
            max_score = score
            herida_dominante = dim

    conclusion = (
        f"Tu herida más activa es la de {herida_dominante}. "
        "Las heridas de infancia son adaptaciones ante el dolor — decisiones que tomaste para dejar de sentir algo insoportable. "
        "Hoy esa defensa opera automáticamente aunque ya no la necesites. "
        "El camino no es eliminarla sino reconocerla: cuando la ves actuar, ya no eres ella. "
        "⚠️ Modelo de Lise Bourbeau — orientativo, no diagnóstico."
    )
    return {"dimensiones": dimensiones, "conclusion": conclusion, "herida_dominante": herida_dominante}


# ─────────────────────────────────────────────────────────────────────
# IBI — Inventario de Creencias Irracionales (Ellis)
# Escala: 1-5 | Max por dimensión: 2 ítems → 10; 1 ítem → 5
# ─────────────────────────────────────────────────────────────────────

def _eval_ibi(details):
    # max real según ítems en seed
    max_por_dim = {
        'Necesidad de Aprobación':      10,  # 2 ítems × 5
        'Perfeccionismo':               10,  # 2 ítems × 5
        'Culpa y Condena':               5,  # 1 ítem × 5
        'Intolerancia a la Frustración':10,  # 2 ítems × 5
        'Irresponsabilidad Emocional':   5,  # 1 ítem × 5
        'Ansiedad Ansiosa':              5,  # 1 ítem × 5
        'Evitación':                     5,  # 1 ítem × 5
    }
    dimensiones = []
    worst_dim, worst_pct = None, -1
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        if pct <= 40:
            nivel, txt = "Racional", "No exhibes fijación irracional dominante aquí."
        elif pct <= 70:
            nivel, txt = "Tendencia", "Esta creencia aparece bajo presión."
        else:
            nivel, txt = "Dogma Irracional", "Regla cognitiva que contamina fuertemente tu psique."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': f"Creencia irracional: {dim.lower()}.", 'analisis': txt
        })
        if pct > worst_pct:
            worst_pct = pct
            worst_dim = dim
    conclusion = (f"La terapia racional-emotiva de Ellis postula que el sufrimiento no viene de lo que te pasa, "
                  f"sino de las demandas absolutas ('debos' y 'tengos') que le exiges a la realidad. "
                  f"Tu mayor rigidez es '{worst_dim}'. El objetivo es cazar estos dogmas en tu discurso diario e inyectarles flexibilidad radical.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# AUTOSABOTAJE — Instrumento personalizado (no validado psicométricamente)
# Escala: 1-5 | Procrastinación: 3 ítems → max 15; otros 2 ítems → max 10
# ─────────────────────────────────────────────────────────────────────

def _eval_autosabotaje(details):
    max_por_dim = {
        'Procrastinación':            15,  # 3 ítems × 5
        'Perfeccionismo Paralizante':  10,  # 2 ítems × 5
        'Miedo al Éxito':             10,  # 2 ítems × 5
        'Síndrome del Impostor':      10,  # 2 ítems × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 10)
        pct = min((score / max_s) * 100, 100)
        if pct <= 33:
            nivel, txt = "Ausente", "Afrontamiento saludable."
        elif pct <= 66:
            nivel, txt = "Ocasional", "Este mecanismo aparece como respuesta al estrés elevado."
        else:
            nivel, txt = "Patrón Crónico", "Este es un freno estructural que detiene tu progreso."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': f"Patrón de autosabotaje: {dim.lower()}.", 'analisis': txt
        })
    conclusion = ("El autosabotaje no es falta de 'disciplina'; es tu sistema psíquico protegiéndote de un dolor percibido mayor. "
                  "La resistencia que encuentras en tu avance no es tu enemigo — es tu propio mecanismo de defensa aterrado. "
                  "Para avanzar, debes negociar con estas partes asustadas, no ir a la guerra contra ti mismo.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# DIRTY DOZEN — Tríada Oscura (Jonason & Webster, 2010)
# Escala: 1-5 acuerdo (likert5a) | 4 ítems por factor | Max = 20 por factor
# Instrumento validado de 12 ítems. Validado en múltiples idiomas.
# ─────────────────────────────────────────────────────────────────────

def _eval_dirty_dozen(details):
    MAX_PER_DIM = 20  # 4 ítems × 5
    descripciones = {
        'Maquiavelismo': 'Tendencia al cinismo manipulador, pensamiento estratégico frío y explotación interpersonal.',
        'Narcisismo': 'Grandiosidad subclínica, necesidad de admiración, entitlement y búsqueda de estatus.',
        'Psicopatía': 'Insensibilidad emocional, baja empatía, ausencia de remordimiento y cinismo.'
    }
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        if pct <= 40:
            nivel, txt = "Sombra Integrada", "No presentas rasgos dominantes. Capacidad de empatía sana."
        elif pct <= 70:
            nivel, txt = "Sombra Activada", "Uso instrumental y situacional de estos rasgos."
        else:
            nivel, txt = "Sombra Dominante", "Rasgos predominantes que estructuran tu forma de relacionarte."
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''), 'analisis': txt
        })
    conclusion = ("Nadie está compuesto puramente de luz. La Tríada Oscura evalúa los mecanismos evolutivos de supervivencia predatoria "
                  "que todos poseemos en algún grado. La verdadera bondad es un logro consciente — reconocer los dientes que tienes "
                  "y decidir no usarlos. Dirty Dozen (Jonason & Webster, 2010): 4 ítems × 3 factores.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# TAS-20 — Toronto Alexithymia Scale (Bagby, Parker & Taylor, 1994)
# Escala: 1-5 acuerdo (likert5a) | 20 ítems | 3 subescalas
# DIF (Dificultad Identificar): 7 ítems → max 35
# DDF (Dificultad Describir):   5 ítems → max 25
# EOT (Pensamiento Externo):    8 ítems → max 40  (4 invertidos)
# Total: 20-100 | Cortes: ≤51 sin alexitimia, 52-60 posible, ≥61 alexitimia
# Validado en español: Martínez-Sánchez (1996)
# ─────────────────────────────────────────────────────────────────────

def _eval_tas20(details):
    max_por_dim = {
        'Identificación':     35,  # 7 ítems × 5 (DIF)
        'Descripción':        25,  # 5 ítems × 5 (DDF)
        'Pensamiento Externo':40,  # 8 ítems × 5 (EOT)
    }
    descripciones = {
        'Identificación': 'Dificultad para identificar y distinguir sentimientos de sensaciones corporales (DIF). 7 ítems.',
        'Descripción': 'Dificultad para comunicar y describir sentimientos a otras personas (DDF). 5 ítems.',
        'Pensamiento Externo': 'Tendencia a centrarse en estímulos externos en lugar de la experiencia subjetiva interna (EOT). 8 ítems.'
    }
    dimensiones = []
    total_score = sum(details.values())
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 25)
        pct = min((score / max_s) * 100, 100)
        if pct > 70:
            nivel = "Alto"
        elif pct > 40:
            nivel = "Moderado"
        else:
            nivel = "Bajo"
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''),
            'analisis': f"Nivel de dificultad en {dim.lower()}."
        })
    if total_score <= 51:
        nivel_total = "Sin alexitimia"
    elif total_score <= 60:
        nivel_total = "Posible alexitimia"
    else:
        nivel_total = "Alexitimia"
    conclusion = (f"Puntuación total TAS-20: {total_score}/100 — {nivel_total} (Bagby et al., 1994; cortes: ≤51 / 52-60 / ≥61). "
                  "La alexitimia no es la falta de emociones, sino la falta de conexión con ellas. "
                  "Es un 'muro cognitivo' que impide que el sentimiento llegue al lenguaje. "
                  "Si no puedes 'nombrar' lo que sientes, empieza por localizar dónde vibra en tu cuerpo antes de buscar la palabra.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# DERS — Dificultades en Regulación Emocional (Gratz & Roemer, 2004)
# Escala: 1-5 | ítems variables por subscala
# NOTA: DERS original tiene 36 ítems. Esta adaptación tiene 8 ítems.
# Max real: Claridad=5, Atención=5, No-aceptación=5, Interferencia=5, Impulsividad=10, Estrategias=10
# ─────────────────────────────────────────────────────────────────────

def _eval_ders(details):
    max_por_dim = {
        'Claridad':      5,   # 1 ítem × 5 (reverse)
        'Atención':      5,   # 1 ítem × 5 (reverse)
        'No-aceptación': 5,   # 1 ítem × 5
        'Interferencia': 5,   # 1 ítem × 5
        'Impulsividad': 10,   # 2 ítems × 5
        'Estrategias':  10,   # 2 ítems × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=True)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Saludable" if pct < 40 else "Dificultad",
            'descripcion': f"Dificultad de {dim.lower()} emocional.",
            'analisis': "Análisis de regulación emocional."
        })
    conclusion = ("La regulación emocional es la capacidad de surfear la ola del sentimiento sin ser arrastrado por ella. "
                  "No se trata de no sentir, sino de no ser esclavo de lo que sientes. ⚠️ Adaptación de 8 ítems del DERS (36 ítems originales).")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# CHAKRAS — Instrumento personalizado (no validado psicométricamente)
# Escala: 1-5 | 2 ítems por chakra | max = 10 por chakra
# ─────────────────────────────────────────────────────────────────────

def _eval_chakras(details):
    MAX_PER_DIM = 10  # 2 ítems × 5
    descripciones = {
        'Muladhara (Raíz)': 'Supervivencia, seguridad, enraizamiento.',
        'Svadhisthana (Sacro)': 'Placer, sexualidad, fluidez emocional.',
        'Manipura (Plexo Solar)': 'Poder personal, voluntad, digestión.',
        'Anahata (Corazón)': 'Amor, compasión, integración.',
        'Vishuddha (Garganta)': 'Comunicación, expresión, verdad.',
        'Ajna (Tercer Ojo)': 'Intuición, visión, sabiduría.',
        'Sahasrara (Corona)': 'Conexión espiritual, trascendencia.'
    }
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        nivel = "Fuerte" if pct > 75 else "Equilibrado" if pct > 50 else "Débil"
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': nivel, 'descripcion': descripciones.get(dim, ''),
            'analisis': "Flujo de energía en este centro."
        })
    conclusion = ("El sistema de chakras es un mapa de la consciencia humana. Un chakra 'bloqueado' es simplemente una parte de tu experiencia vital "
                  "que no está recibiendo suficiente atención. ⚠️ Instrumento no validado psicométricamente.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# SWB — Spiritual Well-Being Scale (Paloutzian & Ellison, 1982)
# Escala: 1-5 (likert5) | 4 ítems por subscala | max = 20 por subscala
# NOTA: SWBS original usa escala 1-6 y 20 ítems. Adaptación de 8 ítems con 1-5.
# ─────────────────────────────────────────────────────────────────────

def _eval_swb(details):
    MAX_PER_DIM = 20  # 4 ítems × 5
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Alto" if pct > 75 else "Medio" if pct > 40 else "Bajo",
            'descripcion': f"Mide tu {dim.lower()}.",
            'analisis': "Indicador de bienestar."
        })
    conclusion = ("El bienestar espiritual es el equilibrio entre tu conexión con lo sagrado y tu propósito en la tierra. "
                  "No requiere creencia religiosa — requiere sentido. ⚠️ Adaptación de 8 ítems de la SWBS (20 ítems originales).")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# CLONINGER — Autotrascendencia del TCI-R (Cloninger, 1994)
# Escala: 1-5 | Absorción: 2 ítems → 10; Identificación: 2 → 10; Aceptación: 1 → 5
# NOTA: TCI-R completo tiene 240 ítems. Esta es una adaptación de 5 ítems.
# ─────────────────────────────────────────────────────────────────────

def _eval_cloninger(details):
    max_por_dim = {
        'Absorción Transpersonal':  10,  # 2 ítems × 5
        'Identificación Mística':   10,  # 2 ítems × 5
        'Aceptación Espiritual':     5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 10)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Alto" if pct > 70 else "Moderado",
            'descripcion': f"Capacidad de {dim.lower()}.",
            'analisis': "Rasgo de autotrascendencia."
        })
    conclusion = ("La autotrascendencia es la capacidad de disolver las fronteras del ego y sentirse parte de una totalidad mayor. "
                  "⚠️ Adaptación de 5 ítems — orientativa.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# LOGO-TEST (Lukas, 1986 — adaptación)
# Escala: 1-5 | Sentido: 2 ítems → 10; Vacío: 2 ítems → 10 (reverse); Resiliencia: 1 → 5
# NOTA: Logo-Test original de Lukas tiene 14 ítems y formato diferente.
# ─────────────────────────────────────────────────────────────────────

def _eval_logotest(details):
    max_por_dim = {
        'Sentido':               10,  # 2 ítems × 5
        'Vacío Existencial':     10,  # 2 ítems × 5 (reverse)
        'Resiliencia de Sentido': 5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Fuerte" if pct > 60 else "Vulnerable",
            'descripcion': f"Mide {dim.lower()}.",
            'analisis': "Indicador logoterapéutico."
        })
    conclusion = ("La voluntad de sentido es la motivación primaria del ser humano (Frankl). "
                  "El Logo-Test identifica si estamos viviendo en un vacío existencial o si hemos encontrado el 'para qué'. ⚠️ Adaptación de 5 ítems.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# DRI — Dream Recall Index (adaptación)
# Escala: 1-5 | 1 ítem por subscala | max = 5 por subscala
# ─────────────────────────────────────────────────────────────────────

def _eval_dri_das(details):
    dimensiones = []
    for dim, score in details.items():
        max_s = 5  # 1 ítem × 5
        pct = min((score / max_s) * 100, 100)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'nivel': "Alto" if pct > 60 else "Bajo",
            'descripcion': f"Medición de {dim.lower()}.",
            'analisis': "Frecuencia y calidad onírica."
        })
    conclusion = ("Tu relación con tus sueños es un puente hacia tu inconsciente. "
                  "Aumentar el recuerdo onírico es el primer paso para integrar el material nocturno en tu proceso de individuación.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# DLQ — Dream Lucidity Questionnaire (adaptación de Stumbrys et al., 2014)
# Escala: 1-5 | 1 ítem por subscala | max = 5 por subscala
# NOTA: DLQ original tiene 4 ítems. Esta adaptación tiene 3.
# ─────────────────────────────────────────────────────────────────────

def _eval_lucidez(details):
    dimensiones = []
    for dim, score in details.items():
        max_s = 5  # 1 ítem × 5
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Potencial alto" if pct > 50 else "Inicial",
            'descripcion': f"Capacidad de {dim.lower()} onírico.",
            'analisis': "Indicador de lucidez en sueños."
        })
    conclusion = ("La lucidez onírica es el arte de despertar dentro del sueño. Expande la consciencia y permite "
                  "usar la noche como campo de entrenamiento para la vigilia plena.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# VIA — Values in Action Inventory (Peterson & Seligman, 2004)
# Escala: 1-5 | Virtudes con diferente nº de ítems
# Max: Sabiduría=15 (3ít), Valor=10 (2ít), Humanidad=10, Justicia=10, Templanza=10, Trascendencia=10
# NOTA: VIA completo tiene 240 ítems. Esta es una versión de 13 ítems de screening.
# ─────────────────────────────────────────────────────────────────────

def _eval_via(details):
    max_por_virtud = {
        'Sabiduría':    15,  # 3 ítems × 5
        'Valor':        10,  # 2 ítems × 5
        'Humanidad':    10,  # 2 ítems × 5
        'Justicia':     10,  # 2 ítems × 5
        'Templanza':    10,  # 2 ítems × 5
        'Trascendencia':10,  # 2 ítems × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_virtud.get(dim, 10)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Fortaleza Firma" if pct >= 80 else "En desarrollo",
            'descripcion': f"Virtud de {dim.lower()}.",
            'analisis': "Fortaleza de carácter según VIA."
        })
    conclusion = ("Tus fortalezas de carácter son tus 'herramientas de fábrica'. Usarlas conscientemente es el predictor "
                  "más fuerte de satisfacción y resiliencia. No trates de arreglar tus debilidades — potencia tus fortalezas firma. "
                  "⚠️ Screening de 13 ítems — VIA completo tiene 240 ítems.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# RIASEC — Holland (1985) — adaptación de 12 ítems
# Escala: 1-5 | 2 ítems por tipo | max = 10 por tipo
# ─────────────────────────────────────────────────────────────────────

def _eval_riasec(details):
    MAX_PER_DIM = 10  # 2 ítems × 5
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Interés Alto" if pct > 70 else "Medio",
            'descripcion': f"Perfil {dim.lower()}.",
            'analisis': "Orientación vocacional."
        })
    conclusion = ("El modelo RIASEC sugiere que prosperamos en entornos que coinciden con nuestra personalidad vocacional. "
                  "Tu perfil indica dónde te sentirás más natural y efectivo trabajando.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# MWQ — Work as Meaning Inventory (adaptado de Steger et al., 2012)
# Escala: 1-5 | 4 ítems | max = 20
# ─────────────────────────────────────────────────────────────────────

def _eval_mwq(details):
    score = sum(details.values())
    max_s = 20  # 4 ítems × 5
    pct = min((score / max_s) * 100, 100)
    pol, msg, acc = _get_polarity('Sentido', pct, es_interferencia=False)
    dimensiones = [{
        'nombre': 'Sentido del Trabajo', 'puntos': score, 'max': max_s, 'pct': pct,
        'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
        'nivel': "Alineado" if pct > 75 else "En transición",
        'descripcion': "Grado de significado y propósito en la labor profesional (WAMI, Steger et al., 2012).",
        'analisis': "Nivel de coherencia vocacional."
    }]
    conclusion = ("El trabajo deja de ser una carga cuando se convierte en una vía de expresión de tus valores. "
                  "Si tu puntaje es bajo, no significa que debas renunciar — sino encontrar cómo inyectar sentido en tus tareas actuales.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# KOLB — Learning Style Inventory (Kolb, 1984) — adaptación de 6 ítems
# Escala: 1-5 | EC=2 ítems→10, OR=2→10, CA=1→5, EA=1→5
# ─────────────────────────────────────────────────────────────────────

def _eval_kolb(details):
    max_por_dim = {
        'Experiencia Concreta':        10,  # 2 ítems × 5
        'Observación Reflexiva':       10,  # 2 ítems × 5
        'Conceptualización Abstracta':  5,  # 1 ítem × 5
        'Experimentación Activa':       5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Preferencial" if pct >= 80 else "Secundario",
            'descripcion': f"Modo de {dim.lower()}.",
            'analisis': "Estilo de aprendizaje experiencial."
        })
    conclusion = ("Aprender a aprender es la habilidad maestra. Tu estilo de Kolb te dice cómo procesas mejor la realidad: "
                  "¿viviéndola, pensando sobre ella, teorizando o probando? ⚠️ Adaptación de 6 ítems — orientativa.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# CEQ — Epistemic Curiosity Questionnaire (adaptación)
# Escala: 1-5 | Curiosidad Epistémica=3 ítems→15, Tolerancia Ambigüedad=1→5, Pensamiento Crítico=1→5
# ─────────────────────────────────────────────────────────────────────

def _eval_ceq(details):
    max_por_dim = {
        'Curiosidad Epistémica':       15,  # 3 ítems × 5
        'Tolerancia a la Ambigüedad':   5,  # 1 ítem × 5 (reverse)
        'Pensamiento Crítico':           5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Hambre intelectual alta" if pct > 70 else "Estándar",
            'descripcion': f"Capacidad de {dim.lower()}.",
            'analisis': "Apertura mental al conocimiento."
        })
    conclusion = ("La curiosidad es el motor de la expansión. Mantener el 'hambre de saber' mantiene la mente joven y plástica. "
                  "Busca siempre temas que desafíen tus modelos mentales actuales.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# MOS-SSS — Medical Outcomes Study Social Support Survey (Sherbourne & Stewart, 1991)
# Escala: 1-5 | Emocional=3 ítems→15; Informacional=2→10; Instrumental=2→10; Compañía=1→5
# NOTA: MOS-SSS completo tiene 20 ítems. Adaptación de 8 ítems.
# ─────────────────────────────────────────────────────────────────────

def _eval_comunidad(details):
    max_por_dim = {
        'Apoyo Emocional':      15,  # 3 ítems × 5
        'Apoyo Informacional':  10,  # 2 ítems × 5
        'Apoyo Instrumental':   10,  # 2 ítems × 5
        'Apoyo de Compañía':     5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 10)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Saludable" if pct > 60 else "Riesgo de Aislamiento",
            'descripcion': f"Apoyo percibido: {dim.lower()}.",
            'analisis': "Salud de la red social."
        })
    conclusion = ("Somos seres tribales. Tu salud biológica y mental está íntimamente ligada a la calidad de tu red social. "
                  "No se trata de tener muchos contactos, sino de tener provisiones sociales claras: apego, integración y valor social. ⚠️ Adaptación de 8 ítems del MOS-SSS (20 ítems originales).")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# FORTALEZAS PROSOCIALES — Instrumento personalizado
# Escala: 1-5 | Asertividad=2 ítems→10; otros 1 ítem→5
# ─────────────────────────────────────────────────────────────────────

def _eval_comunicacion(details):
    max_por_dim = {
        'Asertividad':               10,  # 2 ítems × 5 (ítem 1 + ítem 5 reverse)
        'Escucha Activa':             5,  # 1 ítem × 5
        'Empatía':                    5,  # 1 ítem × 5
        'Resolución Colaborativa':    5,  # 1 ítem × 5
        'Expresión Emocional':        5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Predominante" if pct > 70 else "En desarrollo",
            'descripcion': f"Fortaleza de {dim.lower()}.",
            'analisis': "Patrón comunicativo prosocial."
        })
    conclusion = ("La asertividad es la capacidad de honrar tu verdad sin deshonrar la del otro. "
                  "La comunicación consciente es el puente hacia la intimidad real.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# MAQ — Money Attitudes Questionnaire (instrumento personalizado)
# Escala: 1-5 | Creencias Limitantes=2 ítems→10; otros 1 ítem→5
# ─────────────────────────────────────────────────────────────────────

def _eval_maq(details):
    max_por_dim = {
        'Creencias Limitantes': 10,  # 2 ítems × 5
        'Merecimiento':          5,  # 1 ítem × 5
        'Claridad Financiera':   5,  # 1 ítem × 5
        'Flujo':                 5,  # 1 ítem × 5
        'Mentalidad de Escasez': 5,  # 1 ítem × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        es_interferencia = dim in ('Creencias Limitantes', 'Mentalidad de Escasez')
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=es_interferencia)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Alto" if pct > 70 else "Bajo",
            'descripcion': f"Actitud financiera: {dim.lower()}.",
            'analisis': "Relación con los recursos económicos."
        })
    conclusion = ("Tu relación con el dinero es un espejo de tu relación con la vida. "
                  "La abundancia no es acumulación, es flujo. Identificar tus arquetipos financieros te permite "
                  "usar el dinero como herramienta de libertad en vez de mecanismo de defensa.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# FSS — Financial Stress Scale (instrumento personalizado)
# Escala: 1-5 | Estrés=2 ítems→10; Control=1→5; Conducta=2→10
# ─────────────────────────────────────────────────────────────────────

def _eval_fss(details):
    max_por_dim = {
        'Estrés Financiero':   10,  # 2 ítems × 5
        'Control Percibido':    5,  # 1 ítem × 5 (reverse)
        'Conducta Financiera': 10,  # 2 ítems × 5
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 5)
        es_interferencia = dim != 'Control Percibido'
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=es_interferencia)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Alto" if pct > 70 else "Bajo",
            'descripcion': f"Dimensión financiera: {dim.lower()}.",
            'analisis': "Impacto del estrés financiero."
        })
    conclusion = ("Las finanzas estresadas revelan la relación con la abundancia, el merecimiento y el control. "
                  "La luz es la conciencia financiera; la sombra es el piloto automático económico.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# CIQ — Creative Identity Questionnaire (instrumento personalizado)
# Escala: 1-5 | 2 ítems por dimensión | max = 10
# ─────────────────────────────────────────────────────────────────────

def _eval_creatividad(details):
    MAX_PER_DIM = 10  # 2 ítems × 5
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Fuego Creador" if pct > 75 else "En incubación",
            'descripcion': f"Dimensión {dim.lower()}.",
            'analisis': "Potencial expresivo creativo."
        })
    conclusion = ("La creatividad no es una habilidad, es una forma de ver. Cuando integras tu identidad creativa, "
                  "dejas de ser un consumidor de la realidad para convertirte en un co-creador de ella.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# RUEDA DE LA VIDA — Instrumento de coaching (no validado psicométricamente)
# Escala: 1-5 | 1 ítem por área | max = 5 por área
# ─────────────────────────────────────────────────────────────────────

def _eval_integracion(details):
    MAX_PER_DIM = 5  # 1 ítem × 5
    dimensiones = []
    for dim, score in details.items():
        pct = min((score / MAX_PER_DIM) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': MAX_PER_DIM, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Integrado" if pct >= 80 else "En proceso",
            'descripcion': f"Área vital: {dim.lower()}.",
            'analisis': "Satisfacción en esta área de vida."
        })
    conclusion = ("La integración no es perfección en todas las áreas — es la capacidad de moverte conscientemente entre ellas. "
                  "La rueda nunca será perfectamente redonda: lo importante es que ruede.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# SOC-29 — Sense of Coherence (Antonovsky, 1987) — adaptación de 7 ítems
# Escala: 1-7 (likert7) | Manejabilidad: 2 ítems → 14; Significatividad: 3 → 21; Comprensibilidad: 2 → 14
# NOTA: SOC-29 original tiene 29 ítems en escala 1-7. SOC-13 es la versión corta.
# ─────────────────────────────────────────────────────────────────────

def _eval_soc29(details):
    max_por_dim = {
        'Manejabilidad':    14,  # 2 ítems × 7
        'Significatividad': 21,  # 3 ítems × 7
        'Comprensibilidad': 14,  # 2 ítems × 7
    }
    dimensiones = []
    for dim, score in details.items():
        max_s = max_por_dim.get(dim, 14)
        pct = min((score / max_s) * 100, 100)
        pol, msg, acc = _get_polarity(dim, pct, es_interferencia=False)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s, 'pct': pct,
            'polaridad': pol, 'mensaje_polaridad': msg, 'accion_sugerida': acc,
            'nivel': "Fuerte" if pct > 70 else "Frágil",
            'descripcion': f"Sentido de coherencia: {dim.lower()}.",
            'analisis': "Capacidad de navegar el caos con sentido."
        })
    conclusion = ("El Sentido de Coherencia (Antonovsky) es lo que te permite navegar el caos sin perder el centro. "
                  "Comprensibilidad (¿entiendo lo que me pasa?), manejabilidad (¿tengo recursos?) y significatividad (¿vale la pena?) "
                  "forman el triángulo de la resiliencia. ⚠️ Adaptación de 7 ítems del SOC-29.")
    return {"dimensiones": dimensiones, "conclusion": conclusion}


# ─────────────────────────────────────────────────────────────────────
# FALLBACK GENÉRICO
# ─────────────────────────────────────────────────────────────────────

def _eval_generic(details):
    dimensiones = []
    for dim, score in details.items():
        max_s = max(score * 1.5, 10)
        pct = min((score / max_s) * 100, 100)
        dimensiones.append({
            'nombre': dim, 'puntos': score, 'max': max_s,
            'pct': pct, 'nivel': "Calculado",
            'analisis': "Análisis en desarrollo."
        })
    return {"dimensiones": dimensiones, "conclusion": "Continúa tu viaje de auto-exploración integrando los resultados en tu día a día."}
