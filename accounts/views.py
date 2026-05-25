import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django import forms
from .models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre', max_length=60)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=form.cleaned_data['first_name'],
            password=form.cleaned_data['password'],
        )
        login(request, user)
        return redirect('onboarding_viaje')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    error = None
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'].lower(),
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        error = 'Correo o contraseña incorrectos.'
    return render(request, 'accounts/login.html', {'form': form, 'error': error})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    try:
        if not request.user.profile.map_aesthetic:
            return redirect('onboarding_mapa')
    except Exception:
        return redirect('onboarding_mapa')

    from psychometrics.models import TestResult, Test
    from tokens.models import TokenBalance
    recent_results = TestResult.objects.filter(user=request.user).select_related('test')[:5]
    try:
        token_balance = request.user.token_balance
    except Exception:
        token_balance = None
    total_tests = Test.objects.filter(active=True).count()
    completed_tests = (
        TestResult.objects.filter(user=request.user).values('test').distinct().count()
    )
    map_pct = round(completed_tests / total_tests * 100) if total_tests else 0
    return render(request, 'dashboard.html', {
        'recent_results': recent_results,
        'token_balance': token_balance,
        'map_aesthetic': request.user.profile.map_aesthetic,
        'map_pct': map_pct,
        'completed_tests': completed_tests,
        'total_tests': total_tests,
    })


_VALID_AESTHETICS = {'cosmos', 'mandala', 'psychedelic'}

@login_required
def onboarding_mapa(request):
    try:
        profile = request.user.profile
    except Exception:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)

    cambiar = request.GET.get('cambiar') == '1'
    if profile.map_aesthetic and not cambiar:
        return redirect('dashboard')

    if request.method == 'POST':
        choice = request.POST.get('map_aesthetic', '')
        if choice in _VALID_AESTHETICS:
            profile.map_aesthetic = choice
            profile.save(update_fields=['map_aesthetic'])
            return redirect('onboarding_tests')

    return render(request, 'accounts/onboarding_mapa.html')


def bienvenido(request):
    if request.user.is_authenticated:
        from tokens.service import credit_mission
        credit_mission(request.user, 'onboarding')
    return render(request, 'bienvenido.html')


@login_required
def perfil(request):
    if request.method == 'GET':
        return redirect('community:perfil_propio')
    try:
        profile = request.user.profile
    except Exception:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)

    saved = False
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        bio = request.POST.get('bio', '').strip()
        profession = request.POST.get('profession', '').strip()
        if first_name:
            request.user.first_name = first_name
            request.user.save(update_fields=['first_name'])
        profile.bio = bio
        profile.profession = profession

        # Onboarding editable
        profile.onboarding_question = request.POST.get('onboarding_question', '').strip()
        entry_point = request.POST.get('onboarding_entry_point', '').strip()
        if entry_point == 'otro':
            entry_point = request.POST.get('onboarding_entry_point_texto', '').strip()
        profile.onboarding_entry_point = entry_point
        noise_area = request.POST.get('onboarding_noise_area', '').strip()
        if noise_area == 'otro':
            noise_area = request.POST.get('onboarding_noise_area_texto', '').strip()
        profile.onboarding_noise_area = noise_area
        prior = request.POST.getlist('onboarding_prior_exploration')
        profile.onboarding_prior_exploration = ','.join(prior) if prior else ''

        _NUCLEO_KEYS = ['transcendencia', 'cambio', 'merecimiento', 'perdon', 'sentido_dolor']
        nucleo = {k: request.POST.get(f'nucleo_{k}', '') for k in _NUCLEO_KEYS}
        profile.onboarding_nucleo = {k: v for k, v in nucleo.items() if v}

        aesthetic = request.POST.get('map_aesthetic', '').strip()
        valid_aesthetics = [c[0] for c in profile.MAP_AESTHETIC_CHOICES]
        if aesthetic in valid_aesthetics:
            profile.map_aesthetic = aesthetic

        # Avatar
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        # Social links
        social_keys = ['instagram', 'x', 'linkedin', 'web']
        profile.social_links = {
            k: request.POST.get(f'social_{k}', '').strip()
            for k in social_keys
            if request.POST.get(f'social_{k}', '').strip()
        }

        update_fields = [
            'bio', 'profession', 'map_aesthetic', 'social_links',
            'onboarding_question', 'onboarding_entry_point',
            'onboarding_noise_area', 'onboarding_prior_exploration',
            'onboarding_nucleo',
        ]
        if 'avatar' in request.FILES:
            update_fields.append('avatar')
        profile.save(update_fields=update_fields)
        try:
            from mirror.views import _reseed_brain
            _reseed_brain(request.user)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("_reseed_brain failed: %s", e)
        saved = True

    _KNOWN_ENTRY_POINTS = {'cambio', 'ciclos', 'busqueda', 'algo-mas', 'entenderme'}
    _KNOWN_NOISE_AREAS  = {'trabajo', 'relaciones', 'cuerpo', 'identidad', 'proposito', 'todo'}
    _PILL_OPTS = [('si', 'Sí'), ('a-veces', 'A veces'), ('no', 'No')]
    raw_nucleo = profile.onboarding_nucleo
    nucleo = raw_nucleo if isinstance(raw_nucleo, dict) else {}
    nucleo_fields = [
        ('transcendencia', '¿Crees en algo más grande que tú?',   _PILL_OPTS, nucleo.get('transcendencia', '')),
        ('cambio',         '¿Crees que puedes cambiar de verdad?', _PILL_OPTS, nucleo.get('cambio', '')),
        ('merecimiento',   '¿Crees que mereces lo que deseas?',    _PILL_OPTS, nucleo.get('merecimiento', '')),
        ('perdon',         '¿Te perdonas?',                        _PILL_OPTS, nucleo.get('perdon', '')),
        ('sentido_dolor',  '¿Tu dolor tiene algún sentido?',       _PILL_OPTS, nucleo.get('sentido_dolor', '')),
    ]
    prior_opts = [
        ('terapia',      'Terapia o psicología'),
        ('meditacion',   'Meditación o práctica contemplativa'),
        ('astrologia',   'Astrología u otros sistemas'),
        ('coaching',     'Coaching o desarrollo personal'),
        ('primera-vez',  'Primera vez'),
    ]

    entry_is_custom = bool(profile.onboarding_entry_point and profile.onboarding_entry_point not in _KNOWN_ENTRY_POINTS)
    noise_is_custom = bool(profile.onboarding_noise_area  and profile.onboarding_noise_area  not in _KNOWN_NOISE_AREAS)
    return render(request, 'accounts/perfil.html', {
        'profile': profile,
        'saved': saved,
        'nucleo_fields': nucleo_fields,
        'prior_opts': prior_opts,
        'entry_is_custom': entry_is_custom,
        'noise_is_custom': noise_is_custom,
    })


_DIMENSION_LABELS = {
    'identidad':      'Identidad',
    'emociones':      'Emociones',
    'sombra':         'Sombra',
    'cuerpo':         'Cuerpo',
    'mente':          'Mente',
    'proposito':      'Propósito',
    'espiritualidad': 'Espiritualidad',
    'vinculos':       'Vínculos',
    'creatividad':    'Creatividad',
    'comunidad':      'Comunidad',
    'suenos':         'Sueños',
    'abundancia':     'Abundancia',
}


@login_required
def mapa_interior(request):
    import json
    try:
        profile = request.user.profile
    except Exception:
        return redirect('onboarding_mapa')
    if not profile.map_aesthetic:
        return redirect('onboarding_mapa')

    from psychometrics.models import Test, TestResult

    done_slugs = set(
        TestResult.objects.filter(user=request.user)
        .values_list('test__slug', flat=True).distinct()
    )

    dim_data = {}
    for dim, label in _DIMENSION_LABELS.items():
        tests_qs = list(
            Test.objects.filter(dimension=dim, active=True)
            .order_by('order', 'id')
            .values('slug', 'name', 'estimated_minutes')
        )
        for t in tests_qs:
            t['done'] = t['slug'] in done_slugs
        total = len(tests_qs)
        completed = sum(1 for t in tests_qs if t['done'])
        pct = round(completed / total * 100) if total else 0
        dim_data[dim] = {
            'label': label, 'total': total,
            'completed': completed, 'pct': pct,
            'tests': tests_qs,
        }

    total_tests = sum(d['total'] for d in dim_data.values())
    completed_tests = sum(d['completed'] for d in dim_data.values())
    total_pct = round(completed_tests / total_tests * 100) if total_tests else 0

    from mirror.models import ConflictSession
    from birth.models import BirthReport

    recent_results = (
        TestResult.objects.filter(user=request.user)
        .select_related('test')
        .order_by('-completed_at')[:10]
    )
    mirror_count = ConflictSession.objects.filter(user=request.user).count()
    birth_reports = BirthReport.objects.filter(user=request.user, status='complete')

    # Patrones del cerebro activo
    from mirror.models import EspejoMemoria
    import re as _re
    mem = EspejoMemoria.objects.filter(user=request.user, activa=True).first()
    patrones = []
    if mem and mem.contenido:
        m = _re.search(r'## Patrones que he notado(.*?)(?=\n## |\Z)', mem.contenido, _re.DOTALL)
        if m:
            bloque = m.group(1).strip()
            patrones = [
                p.lstrip('-•· ').strip() for p in bloque.split('\n')
                if p.strip() and '(Aún sin' not in p and '(Sin obs' not in p
            ]

    # Resonancias colectivas (últimos 7 días)
    from datetime import timedelta as _td
    from django.utils import timezone as _tz
    import re as _re2
    semana = _tz.now() - _td(days=7)
    descripciones = list(
        ConflictSession.objects.filter(created_at__gte=semana)
        .exclude(conflict_description='')
        .values_list('conflict_description', flat=True)[:300]
    )
    _stop = {'de','la','el','en','un','una','que','es','y','a','los','las','por','para',
             'con','como','su','se','al','del','lo','mi','me','te','no','si','más','pero',
             'hay','tiene','tengo','siento','cuando','porque','todo','nada','algo','muy',
             'bien','mal','quiero','hacer','ser','estoy','este','esta','creo','nunca','siempre'}
    freq = {}
    for d in descripciones:
        for w in _re2.findall(r'\b[a-záéíóúüñ]{5,}\b', d.lower()):
            if w not in _stop:
                freq[w] = freq.get(w, 0) + 1
    resonancias = [{'palabra': w, 'count': c}
                   for w, c in sorted(freq.items(), key=lambda x: -x[1])[:5] if c >= 2]
    total_activos = ConflictSession.objects.filter(created_at__gte=semana).values('user').distinct().count()

    return render(request, 'accounts/mapa_interior.html', {
        'dim_data': dim_data,
        'dim_data_json': json.dumps(dim_data, ensure_ascii=False),
        'aesthetic': profile.map_aesthetic,
        'total_pct': total_pct,
        'completed_tests': completed_tests,
        'total_tests': total_tests,
        'recent_results': recent_results,
        'mirror_count': mirror_count,
        'birth_reports': birth_reports,
        'patrones': patrones,
        'resonancias': resonancias,
        'total_activos': total_activos,
    })


_ONBOARDING_SLUGS = [
    'rueda-de-la-vida-integracion',
    'big-five-inventario-de-personalidad',
    'heridas-de-la-infancia-lise-bourbeau',
]

@login_required
def onboarding_tests(request):
    try:
        profile = request.user.profile
    except Exception:
        return redirect('onboarding_mapa')
    if not profile.map_aesthetic:
        return redirect('onboarding_mapa')

    from psychometrics.models import Test, TestResult

    completed_slugs = set(
        TestResult.objects.filter(user=request.user, test__slug__in=_ONBOARDING_SLUGS)
        .values_list('test__slug', flat=True).distinct()
    )

    if len(completed_slugs) == len(_ONBOARDING_SLUGS):
        return redirect('dashboard')

    tests = []
    for slug in _ONBOARDING_SLUGS:
        try:
            t = Test.objects.get(slug=slug, active=True)
            tests.append({'test': t, 'done': slug in completed_slugs})
        except Test.DoesNotExist:
            pass

    return render(request, 'accounts/onboarding_tests.html', {
        'tests': tests,
        'completed': len(completed_slugs),
        'total': len(_ONBOARDING_SLUGS),
    })


@login_required
def onboarding_viaje(request):
    try:
        profile = request.user.profile
    except Exception:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)

    if profile.onboarding_question and profile.map_aesthetic:
        return redirect('dashboard')

    return render(request, 'accounts/onboarding_viaje.html', {
        'user_name': request.user.first_name,
    })


@login_required
def onboarding_viaje_guardar(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    try:
        profile = request.user.profile
    except Exception:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)

    allowed = {
        'onboarding_entry_point', 'onboarding_noise_area',
        'onboarding_prior_exploration', 'onboarding_question', 'map_aesthetic',
        'onboarding_nucleo',
    }
    updated = [f for f in allowed if f in data]
    for field in updated:
        setattr(profile, field, data[field])
    if updated:
        profile.save(update_fields=updated)

    return JsonResponse({'ok': True})


@login_required
def onboarding_viaje_nacimiento(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    from birth.models import BirthProfile
    from birth.views import _geocode, _get_timezone

    birth_date = request.POST.get('birth_date', '').strip()
    birth_time = request.POST.get('birth_time', '').strip() or None
    birth_place = request.POST.get('birth_place', '').strip()

    if not birth_date or not birth_place:
        return JsonResponse({'error': 'La fecha y el lugar son obligatorios.'}, status=400)

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

    try:
        bp = request.user.birth_profile
        bp.birth_date = birth_date
        bp.birth_time = birth_time
        bp.birth_place = birth_place
        bp.latitude = lat
        bp.longitude = lng
        bp.timezone_str = tz_str
        bp.save()
    except Exception:
        BirthProfile.objects.create(
            user=request.user,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            latitude=lat,
            longitude=lng,
            timezone_str=tz_str,
        )

    return JsonResponse({'ok': True})


# ── Escena inicial según aesthetic ───────────────────────────────────────
_AESTHETIC_SCENE = {'cosmos': 0, 'mandala': 2, 'psychedelic': 1}

@login_required
def vr_home(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    try:
        profile = request.user.profile
    except Exception:
        return redirect('onboarding_mapa')
    if not profile.map_aesthetic:
        return redirect('onboarding_mapa')

    from psychometrics.models import Test, TestResult
    total_tests = Test.objects.filter(active=True).count()
    done_slugs = set(
        TestResult.objects.filter(user=request.user)
        .values_list('test__slug', flat=True).distinct()
    )
    completed_tests = len(done_slugs)
    map_pct = round(completed_tests / total_tests * 100) if total_tests else 0

    # Dimensiones para el panel Hub
    dim_data = {}
    for dim, label in _DIMENSION_LABELS.items():
        total = Test.objects.filter(dimension=dim, active=True).count()
        completed = Test.objects.filter(
            dimension=dim, active=True, slug__in=done_slugs
        ).count()
        dim_data[dim] = {
            'label': label,
            'pct': round(completed / total * 100) if total else 0,
            'completed': completed,
            'total': total,
        }

    # Birth charts generados
    try:
        from birth.models import BirthReport
        birth_types = list(
            BirthReport.objects.filter(user=request.user)
            .values_list('report_type', flat=True).distinct()
        )
    except Exception:
        birth_types = []

    # Patrones de respiración
    from sensorial.views import PATTERNS as BREATH_PATTERNS

    try:
        token_balance = request.user.token_balance.balance
    except Exception:
        token_balance = 0

    import json as _json
    return render(request, 'vr/index.html', {
        'user_name': request.user.first_name or request.user.email.split('@')[0],
        'map_aesthetic': profile.map_aesthetic,
        'map_pct': map_pct,
        'token_balance': token_balance,
        'completed_tests': completed_tests,
        'total_tests': total_tests,
        'initial_scene': _AESTHETIC_SCENE.get(profile.map_aesthetic, 0),
        'onboarding_question': profile.onboarding_question or '',
        'dim_data_json': _json.dumps(dim_data),
        'birth_types_json': _json.dumps(birth_types),
        'breath_patterns_json': _json.dumps([
            {'key': k, 'name': v['name'], 'note': v.get('note', '')}
            for k, v in BREATH_PATTERNS.items()
        ]),
    })


@login_required
def set_aesthetic(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)
    aesthetic = data.get('aesthetic', '').strip()
    if aesthetic not in _VALID_AESTHETICS:
        return JsonResponse({'error': 'invalid'}, status=400)
    try:
        profile = request.user.profile
    except Exception:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
    profile.map_aesthetic = aesthetic
    profile.save(update_fields=['map_aesthetic'])
    return JsonResponse({'ok': True})


_SCALE_OPTIONS = {
    'likert5':  [('1','Nunca'), ('2','Pocas veces'), ('3','A veces'), ('4','Frecuentemente'), ('5','Siempre')],
    'likert5a': [('1','Muy en\ndesacuerdo'), ('2','En\ndesacuerdo'), ('3','Neutral'), ('4','De\nacuerdo'), ('5','Muy de\nacuerdo')],
    'likert4':  [('0','Nunca'), ('1','Rara vez'), ('2','A veces'), ('3','Siempre')],
    'likert3':  [('0','No'), ('1','A veces'), ('2','Sí')],
    'likert7':  [('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5'), ('6','6'), ('7','7')],
    'binary':   [('0','No'), ('1','Sí')],
}

@login_required
def vr_test(request, slug):
    if not request.user.is_staff:
        return redirect('dashboard')
    from psychometrics.models import Test
    from django.shortcuts import get_object_or_404
    test = get_object_or_404(Test, slug=slug, active=True)
    questions = list(test.questions.all().order_by('order', 'id'))

    qs_data = []
    for q in questions:
        opts = _SCALE_OPTIONS.get(q.scale, _SCALE_OPTIONS['likert5'])
        qs_data.append({
            'id': q.id,
            'text': q.text,
            'options': [{'value': v, 'label': l} for v, l in opts],
        })

    try:
        aesthetic = request.user.profile.map_aesthetic or 'cosmos'
    except Exception:
        aesthetic = 'cosmos'

    return render(request, 'vr/test.html', {
        'test': test,
        'questions_json': json.dumps(qs_data, ensure_ascii=False),
        'question_count': len(qs_data),
        'aesthetic': aesthetic,
        'initial_scene': _AESTHETIC_SCENE.get(aesthetic, 0),
    })


@login_required
@login_required
def diario(request):
    from mirror.models import ConflictSession, EspejoMemoria
    from birth.models import BirthReport
    from psychometrics.models import TestResult
    from community.models import SharedInsight
    from django.utils import timezone

    events = []

    for r in TestResult.objects.filter(user=request.user).select_related('test').order_by('-completed_at'):
        events.append({
            'type': 'test', 'date': r.completed_at,
            'title': r.test.name, 'subtitle': r.test.get_dimension_display(),
            'url': f'/psicometria/resultado/{r.pk}/',
            'icon': '◈',
        })

    for s in ConflictSession.objects.filter(user=request.user, status='archived').order_by('-updated_at'):
        events.append({
            'type': 'espejo', 'date': s.updated_at,
            'title': s.title or 'Sesión del Espejo',
            'subtitle': f'{len(s.messages)//2} intercambios',
            'url': None, 'icon': '◎',
        })

    for i in SharedInsight.objects.filter(user=request.user).select_related('test_result__test').order_by('-created_at'):
        events.append({
            'type': 'insight', 'date': i.created_at,
            'title': 'Insight compartido',
            'subtitle': i.source_title, 'url': None, 'icon': '◉',
        })

    for b in BirthReport.objects.filter(user=request.user, status='complete').order_by('-created_at'):
        tipo = {'astral': 'Carta Astral', 'human_design': 'Diseño Humano', 'saju': 'Saju'}.get(b.report_type, b.report_type)
        events.append({
            'type': 'birth', 'date': b.created_at,
            'title': tipo, 'subtitle': None, 'url': None, 'icon': '✦',
        })

    for m in EspejoMemoria.objects.filter(user=request.user).order_by('-created_at'):
        events.append({
            'type': 'cerebro', 'date': m.created_at,
            'title': f'Cerebro v{m.version}',
            'subtitle': {'perfil': 'Desde perfil', 'sesion': 'Desde sesión', 'restauracion': 'Restaurado'}.get(m.fuente, m.fuente),
            'url': '/espejo/cerebro/', 'icon': '◑',
        })

    events.sort(key=lambda e: e['date'] if e['date'] else timezone.now(), reverse=True)

    from itertools import groupby

    def _month_key(e):
        return e['date'].strftime('%Y-%m') if e['date'] else '0000-00'

    grouped = []
    for key, group in groupby(events, key=_month_key):
        grp_list = list(group)
        label = grp_list[0]['date'].strftime('%B %Y').capitalize() if grp_list[0]['date'] else 'Sin fecha'
        grouped.append({'label': label, 'events': grp_list})

    return render(request, 'accounts/diario.html', {'grouped': grouped})


@login_required
@require_POST
def toggle_profile_public(request):
    import json as _json
    try:
        data = _json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'Sin perfil'}, status=400)
    profile.profile_public = bool(data.get('value', False))
    profile.save(update_fields=['profile_public'])
    return JsonResponse({'ok': True, 'profile_public': profile.profile_public})
