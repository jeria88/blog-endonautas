"""
birth/calculators.py — Pure chart calculation functions.

Each function takes a BirthProfile instance and returns a dict of chart_data.
No HTTP, no DB writes, no AI prompts. Safe to call from views, management
commands, or tests.

Approach per system:
  Astral  — local time + tz_str → kerykeion handles the UTC conversion internally.
  HD      — convert to UTC first (needed for solar-arc date arithmetic), then
            pass tz_str='UTC'. Both approaches give identical planet positions;
            the explicit UTC step is required here so the 88° arc search works
            on a clean UTC timeline.
  Saju    — true solar time correction via longitude offset; no kerykeion.
"""

from datetime import timedelta

from .models import SIGN_ES, HOUSE_NUM

# ── Astral chart ──────────────────────────────────────────────────────────────

def calculate_astral_chart(bp):
    """Return chart_data dict for a western tropical natal chart (Placidus)."""
    from kerykeion import AstrologicalSubject

    hour   = bp.birth_time.hour   if bp.birth_time else 12
    minute = bp.birth_time.minute if bp.birth_time else 0
    lat    = bp.latitude  or 0.0
    lng    = bp.longitude or 0.0
    tz     = bp.timezone_str or 'UTC'

    # Pass local time + local timezone — kerykeion converts to UTC internally.
    subject = AstrologicalSubject(
        name=str(bp.user.pk),
        year=bp.birth_date.year, month=bp.birth_date.month, day=bp.birth_date.day,
        hour=hour, minute=minute,
        lat=lat, lng=lng,
        tz_str=tz,
        zodiac_type='Tropical',
    )

    planet_keys = [
        ('sun',     'Sol'),     ('moon',    'Luna'),    ('mercury', 'Mercurio'),
        ('venus',   'Venus'),   ('mars',    'Marte'),   ('jupiter', 'Júpiter'),
        ('saturn',  'Saturno'), ('uranus',  'Urano'),   ('neptune', 'Neptuno'),
        ('pluto',   'Plutón'),
    ]

    planets = []
    for attr, label in planet_keys:
        p = getattr(subject, attr)
        planets.append({
            'key':        attr,
            'label':      label,
            'sign':       SIGN_ES.get(p.sign, p.sign),
            'degree':     round(float(p.position), 2),
            'house':      HOUSE_NUM.get(p.house, 0),
            'retrograde': bool(p.retrograde),
        })

    return {
        'planets': planets,
        'ascendant': {
            'sign':   SIGN_ES.get(subject.first_house.sign, subject.first_house.sign),
            'degree': round(float(subject.first_house.position), 2),
        },
        'midheaven': {
            'sign':   SIGN_ES.get(subject.tenth_house.sign, subject.tenth_house.sign),
            'degree': round(float(subject.tenth_house.position), 2),
        },
        'birth_time_known': bp.birth_time is not None,
    }


# ── Human Design ──────────────────────────────────────────────────────────────

HD_WHEEL_START = 302.0

HD_GATES = [
    41,19,13,49,30,55,37,63,22,36,25,17,21,51,42, 3,
    27,24, 2,23, 8,20,16,35,45,12,15,52,39,53,62,56,
    31,33, 7, 4,29,59,40,64,47, 6,46,18,48,57,32,50,
    28,44, 1,43,14,34, 9, 5,26,11,10,58,38,54,61,60,
]

HD_GATE_NAMES = {
     1:'Expresión Creativa',      2:'La Dirección',         3:'El Orden',
     4:'Formulación',             5:'Ritmos Fijos',          6:'La Fricción',
     7:'El Rol del Yo',           8:'Contribución',          9:'Foco',
    10:'El Amor Propio',         11:'Ideas',                12:'La Cautela',
    13:'El Escucha',             14:'Poder y Habilidades',  15:'La Modestia',
    16:'El Entusiasmo',          17:'Opiniones',            18:'La Corrección',
    19:'El Querer',              20:'El Presente',          21:'Control',
    22:'Apertura',               23:'Asimilación',          24:'La Reflexión',
    25:'La Inocencia',           26:'El Egoísta',           27:'El Cuidado',
    28:'El Jugador',             29:'La Perseverancia',     30:'Los Deseos',
    31:'El Líder',               32:'La Continuidad',       33:'La Retirada',
    34:'El Poder',               35:'El Cambio',            36:'La Crisis',
    37:'La Amistad',             38:'El Luchador',          39:'La Provocación',
    40:'La Soledad',             41:'La Contracción',       42:'El Crecimiento',
    43:'La Intuición',           44:'La Alerta',            45:'El Recolector',
    46:'La Determinación',       47:'La Realización',       48:'La Profundidad',
    49:'Los Principios',         50:'Los Valores',          51:'El Choque',
    52:'La Quietud',             53:'Los Comienzos',        54:'La Ambición',
    55:'El Espíritu',            56:'El Estímulo',          57:'La Claridad Intuitiva',
    58:'La Vitalidad',           59:'La Sexualidad',        60:'La Aceptación',
    61:'La Verdad Interior',     62:'Los Detalles',         63:'La Duda',
    64:'La Confusión',
}

HD_PROFILES = {
    (1,1):'1/1 — Investigador/Investigador',   (1,2):'1/2 — Investigador/Ermitaño',
    (1,3):'1/3 — Investigador/Mártir',         (1,4):'1/4 — Investigador/Oportunista',
    (2,1):'2/1 — Ermitaño/Investigador',       (2,2):'2/2 — Ermitaño/Ermitaño',
    (2,3):'2/3 — Ermitaño/Mártir',             (2,4):'2/4 — Ermitaño/Oportunista',
    (3,1):'3/1 — Mártir/Investigador',         (3,2):'3/2 — Mártir/Ermitaño',
    (3,3):'3/3 — Mártir/Mártir',               (3,4):'3/4 — Mártir/Oportunista',
    (4,1):'4/1 — Oportunista/Investigador',    (4,2):'4/2 — Oportunista/Ermitaño',
    (4,3):'4/3 — Oportunista/Mártir',          (4,4):'4/4 — Oportunista/Oportunista',
    (5,1):'5/1 — Hereje/Investigador',         (5,2):'5/2 — Hereje/Ermitaño',
    (5,3):'5/3 — Hereje/Mártir',               (5,4):'5/4 — Hereje/Oportunista',
    (6,1):'6/1 — Modelo de Rol/Investigador',  (6,2):'6/2 — Modelo de Rol/Ermitaño',
    (6,3):'6/3 — Modelo de Rol/Mártir',        (6,4):'6/4 — Modelo de Rol/Oportunista',
}

_LEFT_ANGLE_PROFILES  = {(5,1),(5,2),(6,2),(6,3)}
_RIGHT_ANGLE_PROFILES = {(1,3),(1,4),(2,4),(2,5),(3,5),(4,6)}

HD_CROSS_THEMES = {
     1:'del Amor Propio',        2:'del Retorno',           3:'de la Mutación',
     4:'de la Formulación',      5:'del Tiempo',            6:'de la Fricción',
     7:'de la Esfinge',          8:'del Contagio',          9:'del Foco',
    10:'del Comportamiento',    11:'de la Curiosidad',     12:'de la Articulación',
    13:'de la Esfinge',         14:'del Gran Candelabro',  15:'de las Ondas Cruzadas',
    16:'de las Habilidades',    17:'de las Preguntas',     18:'de la Corrección',
    19:'de la Necesidad',       20:'del Ahora',            21:'del Control',
    22:'de la Gracia',          23:'de la Asimilación',    24:'de los Cuatro Caminos',
    25:'de la Inocencia',       26:'del Gran Engañador',   27:'de la Preservación',
    28:'del Fatalismo',         29:'del Compromiso',       30:'del Destino',
    31:'del Liderazgo',         32:'de la Transformación', 33:'del Retiro',
    34:'del Gran Poder',        35:'del Cambio',           36:'de los Ciclos',
    37:'de los Pactos',         38:'de la Oposición',      39:'de la Provocación',
    40:'de la Abnegación',      41:'del Deseo',            42:'del Madurar',
    43:'de la Penetración',     44:'de la Alerta',         45:'del Dominio',
    46:'del Descubrimiento',    47:'de la Realización',    48:'de la Polaridad',
    49:'del Principio',         50:'de los Valores',       51:'de la Iniciación',
    52:'de la Quietud',         53:'del Comienzo',         54:'de la Ambición',
    55:'de la Abundancia',      56:'del Estímulo',         57:'de la Claridad',
    58:'de la Vitalidad',       59:'de la Intimidad',      60:'de la Aceptación',
    61:'del Misterio',          62:'de los Detalles',      63:'de las Preguntas',
    64:'de la Confusión',
}

HD_CENTER_GATES = {
    'Cabeza':     [64, 61, 63],
    'Ajna':       [47, 24,  4, 17, 43, 11],
    'Garganta':   [62, 23, 56, 35, 12, 45, 33,  8, 31, 20, 16],
    'Identidad':  [13, 25, 46,  2,  1, 15, 10,  7],
    'Corazón':    [21, 40, 26, 51],
    'Plexo Solar':[30, 55, 49, 37, 22, 36,  6],
    'Sacral':     [ 5, 14, 29, 59,  9,  3, 42, 27, 34],
    'Bazo':       [48, 57, 44, 50, 32, 28, 18],
    'Raíz':       [53, 60, 52, 19, 39, 41, 58, 38, 54],
}

HD_CHANNELS = [
    (64,47),(61,24),(63,4),
    (17,62),(43,23),(11,56),
    (31,7),(8,1),(33,13),(20,10),
    (20,34),(21,45),(16,48),(12,22),(35,36),
    (2,14),(5,15),(29,46),(25,51),
    (26,44),(37,40),
    (59,6),(19,49),(30,41),(39,55),
    (27,50),(34,57),(3,60),(9,52),(42,53),
    (18,58),(28,38),(32,54),
]


def _lon_to_gate_line(lon):
    gate_size = 360.0 / 64
    wheel_pos = (lon - HD_WHEEL_START + 360) % 360
    idx       = int(wheel_pos / gate_size) % 64
    gate      = HD_GATES[idx]
    line      = int((wheel_pos % gate_size) / (gate_size / 6)) + 1
    return gate, min(line, 6)


def calculate_hd_chart(bp):
    """Return chart_data dict for a Human Design natal chart."""
    from kerykeion import AstrologicalSubject
    import pytz
    from datetime import datetime as _dt
    from collections import deque

    hour   = bp.birth_time.hour   if bp.birth_time else 12
    minute = bp.birth_time.minute if bp.birth_time else 0
    lat    = bp.latitude  or 0.0
    lng    = bp.longitude or 0.0
    tz     = bp.timezone_str or 'UTC'

    # Convert to UTC first — required for accurate solar-arc date arithmetic.
    tz_obj      = pytz.timezone(tz)
    birth_naive = _dt(bp.birth_date.year, bp.birth_date.month, bp.birth_date.day, hour, minute)
    birth_aware = tz_obj.localize(birth_naive)
    birth_utc   = birth_aware.astimezone(pytz.UTC)

    p = AstrologicalSubject('p',
        birth_utc.year, birth_utc.month, birth_utc.day,
        birth_utc.hour, birth_utc.minute,
        lat=lat, lng=lng, tz_str='UTC', zodiac_type='Tropical')

    # Design date: moment when sun was exactly 88° before birth sun (solar arc,
    # not calendar days — difference is ~11 hours). Iterative convergence.
    _target_lon = (p.sun.abs_pos - 88.0 + 360) % 360
    design_utc  = birth_utc - timedelta(days=89)
    for _ in range(10):
        _ds   = AstrologicalSubject('_ds',
            design_utc.year, design_utc.month, design_utc.day,
            design_utc.hour, design_utc.minute,
            lat=lat, lng=lng, tz_str='UTC', zodiac_type='Tropical')
        _diff = ((_ds.sun.abs_pos - _target_lon) + 180) % 360 - 180
        if abs(_diff) < 0.001:
            break
        design_utc -= timedelta(hours=_diff * 24.0)
    d = AstrologicalSubject('d',
        design_utc.year, design_utc.month, design_utc.day,
        design_utc.hour, design_utc.minute,
        lat=lat, lng=lng, tz_str='UTC', zodiac_type='Tropical')

    def make_planet(label, symbol, lon):
        g, l = _lon_to_gate_line(lon)
        return {'label': label, 'symbol': symbol, 'gate': g, 'line': l,
                'name': HD_GATE_NAMES.get(g, '')}

    personality_planets = [
        make_planet('Sol',        '⊙', p.sun.abs_pos),
        make_planet('Tierra',     '⊕', (p.sun.abs_pos + 180) % 360),
        make_planet('Luna',       '☽', p.moon.abs_pos),
        make_planet('Nodo Norte', '☊', p.true_north_lunar_node.abs_pos),
        make_planet('Nodo Sur',   '☋', p.true_south_lunar_node.abs_pos),
        make_planet('Mercurio',   '☿', p.mercury.abs_pos),
        make_planet('Venus',      '♀', p.venus.abs_pos),
        make_planet('Marte',      '♂', p.mars.abs_pos),
        make_planet('Júpiter',    '♃', p.jupiter.abs_pos),
        make_planet('Saturno',    '♄', p.saturn.abs_pos),
        make_planet('Urano',      '♅', p.uranus.abs_pos),
        make_planet('Neptuno',    '♆', p.neptune.abs_pos),
        make_planet('Plutón',     '♇', p.pluto.abs_pos),
    ]
    design_planets = [
        make_planet('Sol',        '⊙', d.sun.abs_pos),
        make_planet('Tierra',     '⊕', (d.sun.abs_pos + 180) % 360),
        make_planet('Luna',       '☽', d.moon.abs_pos),
        make_planet('Nodo Norte', '☊', d.true_north_lunar_node.abs_pos),
        make_planet('Nodo Sur',   '☋', d.true_south_lunar_node.abs_pos),
        make_planet('Mercurio',   '☿', d.mercury.abs_pos),
        make_planet('Venus',      '♀', d.venus.abs_pos),
        make_planet('Marte',      '♂', d.mars.abs_pos),
        make_planet('Júpiter',    '♃', d.jupiter.abs_pos),
        make_planet('Saturno',    '♄', d.saturn.abs_pos),
        make_planet('Urano',      '♅', d.uranus.abs_pos),
        make_planet('Neptuno',    '♆', d.neptune.abs_pos),
        make_planet('Plutón',     '♇', d.pluto.abs_pos),
    ]

    p_sun_g,   p_sun_l   = personality_planets[0]['gate'], personality_planets[0]['line']
    p_earth_g, p_earth_l = personality_planets[1]['gate'], personality_planets[1]['line']
    d_sun_g,   d_sun_l   = design_planets[0]['gate'],      design_planets[0]['line']
    d_earth_g, d_earth_l = design_planets[1]['gate'],      design_planets[1]['line']

    active_gates = {pl['gate'] for pl in personality_planets + design_planets}

    gate_to_center = {}
    for center, gates in HD_CENTER_GATES.items():
        for g in gates:
            gate_to_center[g] = center

    defined_centers = set()
    center_adj      = {}
    defined_channels = []
    for g_a, g_b in HD_CHANNELS:
        if g_a in active_gates and g_b in active_gates:
            ctr_a = gate_to_center.get(g_a)
            ctr_b = gate_to_center.get(g_b)
            if ctr_a:
                defined_centers.add(ctr_a)
            if ctr_b:
                defined_centers.add(ctr_b)
            if ctr_a and ctr_b and ctr_a != ctr_b:
                center_adj.setdefault(ctr_a, set()).add(ctr_b)
                center_adj.setdefault(ctr_b, set()).add(ctr_a)
                defined_channels.append({
                    'gates': f'{g_a}–{g_b}',
                    'name':  f'{HD_GATE_NAMES.get(g_a,"")} / {HD_GATE_NAMES.get(g_b,"")}',
                })

    reachable_from_throat = set()
    if 'Garganta' in center_adj:
        queue   = deque(['Garganta'])
        visited = {'Garganta'}
        while queue:
            c = queue.popleft()
            for nb in center_adj.get(c, []):
                if nb not in visited:
                    visited.add(nb)
                    reachable_from_throat.add(nb)
                    queue.append(nb)

    sacral_defined    = 'Sacral' in defined_centers
    motor_centers     = {'Corazón', 'Plexo Solar', 'Raíz', 'Sacral'}
    motors_from_throat = reachable_from_throat & motor_centers

    if sacral_defined and motors_from_throat:
        hd_type, strategy = 'Generador Manifestante', 'Responder y luego informar antes de actuar'
        not_self, signature = 'Frustración / Ira', 'Paz y satisfacción'
    elif sacral_defined:
        hd_type, strategy = 'Generador', 'Responder (esperar una señal del entorno)'
        not_self, signature = 'Frustración', 'Satisfacción'
    elif motors_from_throat:
        hd_type, strategy = 'Manifestador', 'Informar antes de actuar'
        not_self, signature = 'Ira', 'Paz'
    elif defined_centers:
        hd_type, strategy = 'Proyector', 'Esperar la invitación'
        not_self, signature = 'Amargura', 'Éxito'
    else:
        hd_type, strategy = 'Reflector', 'Esperar un ciclo lunar completo (29 días)'
        not_self, signature = 'Decepción', 'Sorpresa'

    profile    = HD_PROFILES.get((p_sun_l, d_sun_l), f'{p_sun_l}/{d_sun_l}')
    if 'Plexo Solar'  in defined_centers: authority = 'Emocional — Plexo Solar'
    elif 'Sacral'     in defined_centers: authority = 'Sacral'
    elif 'Bazo'       in defined_centers: authority = 'Esplénico — Bazo'
    elif 'Corazón'    in defined_centers: authority = 'Ego — Corazón'
    elif 'Identidad'  in defined_centers: authority = 'Identidad — G'
    elif hd_type == 'Reflector':          authority = 'Lunar — 29 días'
    else:                                 authority = 'Mental — Externo'

    visited_def = set()
    components  = 0
    for center in defined_centers:
        if center not in visited_def:
            components += 1
            q = deque([center])
            visited_def.add(center)
            while q:
                c = q.popleft()
                for nb in center_adj.get(c, []):
                    if nb in defined_centers and nb not in visited_def:
                        visited_def.add(nb)
                        q.append(nb)
    definition = {0:'Indefinido', 1:'Definición Simple', 2:'Definición Partida',
                  3:'Definición Partida Triple'}.get(components, 'Definición Cuádruple')

    _profile_key = (p_sun_l, d_sun_l)
    _cross_type  = ('Yuxtaposición' if _profile_key == (4,1)
                    else 'Ángulo Izquierdo' if _profile_key in _LEFT_ANGLE_PROFILES
                    else 'Ángulo Derecho')
    _theme     = HD_CROSS_THEMES.get(p_sun_g, '')
    cross_name = f'Cruz de {_cross_type} {_theme} ({p_sun_g}/{p_earth_g} | {d_sun_g}/{d_earth_g})'.strip()

    return {
        'type':             hd_type,
        'strategy':         strategy,
        'not_self_theme':   not_self,
        'signature':        signature,
        'profile':          profile,
        'authority':        authority,
        'definition':       definition,
        'defined_centers':  sorted(defined_centers),
        'active_gates':     sorted(active_gates),
        'defined_channels': defined_channels,
        'cross_gates': [
            {'gate': p_sun_g,   'name': HD_GATE_NAMES.get(p_sun_g,   ''), 'role': 'P ☉'},
            {'gate': p_earth_g, 'name': HD_GATE_NAMES.get(p_earth_g, ''), 'role': 'P ⊕'},
            {'gate': d_sun_g,   'name': HD_GATE_NAMES.get(d_sun_g,   ''), 'role': 'D ☉'},
            {'gate': d_earth_g, 'name': HD_GATE_NAMES.get(d_earth_g, ''), 'role': 'D ⊕'},
        ],
        'cross_str':      f'{p_sun_g}/{p_earth_g} | {d_sun_g}/{d_earth_g}',
        'cross_name':     cross_name,
        'design_date':    design_utc.strftime('%Y-%m-%d'),
        'planets_paired': [{'p': pp, 'd': dp} for pp, dp in zip(personality_planets, design_planets)],
        'personality': {
            'sun':   {'gate': p_sun_g,   'line': p_sun_l,   'name': HD_GATE_NAMES.get(p_sun_g,   '')},
            'earth': {'gate': p_earth_g, 'line': p_earth_l, 'name': HD_GATE_NAMES.get(p_earth_g, '')},
        },
        'design': {
            'sun':   {'gate': d_sun_g,   'line': d_sun_l,   'name': HD_GATE_NAMES.get(d_sun_g,   '')},
            'earth': {'gate': d_earth_g, 'line': d_earth_l, 'name': HD_GATE_NAMES.get(d_earth_g, '')},
        },
    }


# ── Saju ──────────────────────────────────────────────────────────────────────

TIANGAN    = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI      = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
TIAN_ROM   = ['Jiǎ','Yǐ','Bǐng','Dīng','Wù','Jǐ','Gēng','Xīn','Rén','Guǐ']
TIAN_ES    = ['Madera Yang','Madera Yin','Fuego Yang','Fuego Yin','Tierra Yang',
              'Tierra Yin','Metal Yang','Metal Yin','Agua Yang','Agua Yin']
DI_ROM     = ['Zǐ','Chǒu','Yín','Mǎo','Chén','Sì','Wǔ','Wèi','Shēn','Yǒu','Xū','Hài']
DI_ANIMAL  = ['Rata','Buey','Tigre','Conejo','Dragón','Serpiente',
              'Caballo','Cabra','Mono','Gallo','Perro','Cerdo']
DI_ELEM    = ['Agua','Tierra','Madera','Madera','Tierra','Fuego',
              'Fuego','Tierra','Metal','Metal','Tierra','Agua']
ELEMENTS_ES = ['Madera','Fuego','Tierra','Metal','Agua']


def _true_solar_hour_minute(bp):
    if not bp.birth_time or bp.longitude is None or not bp.timezone_str:
        return None, None, 0
    try:
        import pytz
        from datetime import datetime as _dt, timedelta as _td
        tz     = pytz.timezone(bp.timezone_str)
        naive  = _dt(bp.birth_date.year, bp.birth_date.month, bp.birth_date.day,
                     bp.birth_time.hour, bp.birth_time.minute)
        aware  = tz.localize(naive)
        utc_offset_h  = aware.utcoffset().total_seconds() / 3600
        std_meridian  = utc_offset_h * 15
        correction    = (bp.longitude - std_meridian) * 4
        corrected     = naive + _td(minutes=correction)
        return corrected.hour, corrected.minute, round(correction)
    except Exception:
        return bp.birth_time.hour, bp.birth_time.minute, 0


def _calculate_daewoon(bp, mo_tg, mo_dz, yr_tg):
    import sxtwl
    import datetime

    gender = getattr(bp, 'gender', '') or ''
    if not gender:
        return None

    is_yang_year = (yr_tg % 2 == 0)
    is_male      = (gender == 'M')
    forward      = (is_yang_year == is_male)

    birth_date   = bp.birth_date
    birth_d      = sxtwl.fromSolar(birth_date.year, birth_date.month, birth_date.day)
    birth_mo_tg  = birth_d.getMonthGZ().tg
    birth_mo_dz  = birth_d.getMonthGZ().dz

    if not forward:
        for i in range(1, 45):
            check  = birth_date - timedelta(days=i)
            chk_mo = sxtwl.fromSolar(check.year, check.month, check.day).getMonthGZ()
            if chk_mo.tg != birth_mo_tg or chk_mo.dz != birth_mo_dz:
                jie_date  = check + timedelta(days=1)
                days_diff = (birth_date - jie_date).days
                break
        else:
            return None
    else:
        for i in range(1, 45):
            check  = birth_date + timedelta(days=i)
            chk_mo = sxtwl.fromSolar(check.year, check.month, check.day).getMonthGZ()
            if chk_mo.tg != birth_mo_tg or chk_mo.dz != birth_mo_dz:
                jie_date  = check
                days_diff = (jie_date - birth_date).days
                break
        else:
            return None

    start_age   = round(days_diff / 3)
    step        = 1 if forward else -1
    current_age = datetime.date.today().year - birth_date.year

    cycles = []
    tg, dz = mo_tg, mo_dz
    for i in range(9):
        tg = (tg + step) % 10
        dz = (dz + step) % 12
        age_start = start_age + i * 10
        age_end   = age_start + 9
        cycles.append({
            'stem':        TIANGAN[tg],
            'branch':      DIZHI[dz],
            'rom_stem':    TIAN_ROM[tg],
            'rom_branch':  DI_ROM[dz],
            'elem_stem':   TIAN_ES[tg],
            'elem_branch': DI_ELEM[dz],
            'animal':      DI_ANIMAL[dz],
            'age_start':   age_start,
            'age_end':     age_end,
            'year_start':  birth_date.year + age_start,
            'year_end':    birth_date.year + age_end,
            'is_current':  age_start <= current_age <= age_end,
        })

    current_cycle = next((c for c in cycles if c['is_current']), None)
    return {
        'cycles':        cycles,
        'start_age':     start_age,
        'direction':     'forward' if forward else 'backward',
        'current_cycle': current_cycle,
    }


def calculate_saju_chart(bp):
    """Return chart_data dict for a Saju (Four Pillars) chart.

    Without birth_time: calculates 3 pillars (Year, Month, Day).
    With birth_time:    calculates all 4 pillars.
    """
    import sxtwl

    d  = sxtwl.fromSolar(bp.birth_date.year, bp.birth_date.month, bp.birth_date.day)
    yr = d.getYearGZ(True)
    mo = d.getMonthGZ()
    dy = d.getDayGZ()

    solar_h, solar_m, correction_min = _true_solar_hour_minute(bp)
    if solar_h is not None:
        hour = solar_h
    elif bp.birth_time:
        hour = bp.birth_time.hour
    else:
        hour = None

    hour_known = hour is not None

    def gz_info(gz, label):
        elem_full = TIAN_ES[gz.tg]
        elem_name = elem_full.split()[0]
        return {
            'label':          label,
            'stem':           TIANGAN[gz.tg],
            'branch':         DIZHI[gz.dz],
            'rom_stem':       TIAN_ROM[gz.tg],
            'rom_branch':     DI_ROM[gz.dz],
            'elem_stem':      elem_full,
            'elem_stem_name': elem_name,
            'animal':         DI_ANIMAL[gz.dz],
            'elem_branch':    DI_ELEM[gz.dz],
        }

    pillars = [gz_info(yr, 'Año'), gz_info(mo, 'Mes'), gz_info(dy, 'Día')]
    if hour_known:
        hr_gz = sxtwl.getShiGz(dy.tg, hour)
        pillars.append(gz_info(hr_gz, 'Hora'))

    full_count = {e: 0 for e in ELEMENTS_ES}
    for p in pillars:
        full_count[p['elem_stem_name']] += 1
        full_count[p['elem_branch']]    += 1

    dominant = max(full_count, key=full_count.get)
    min_val  = min(full_count.values())
    weakest_list = [e for e, c in full_count.items() if c == min_val]
    weakest = ' / '.join(weakest_list) if min_val < max(full_count.values()) else None

    daewoon = _calculate_daewoon(bp, mo.tg, mo.dz, yr.tg)

    return {
        'pillars':              pillars,
        'element_count':        full_count,
        'dominant_element':     dominant,
        'weakest_element':      weakest,
        'day_master':           TIAN_ES[dy.tg],
        'hour_known':           hour_known,
        'lunar_year_animal':    DI_ANIMAL[yr.dz],
        'solar_correction_min': correction_min,
        'solar_hour':           solar_h,
        'solar_minute':         solar_m,
        'daewoon':              daewoon,
    }
