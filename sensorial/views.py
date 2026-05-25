import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render
from .models import BreathSession


PATTERNS = {
    'coherencia': {
        'name': 'Coherencia Cardíaca',
        'desc': 'Sincroniza tu corazón y sistema nervioso con el ritmo de 5.5 segundos.',
        'phases': [
            {'label': 'Inhala', 'seconds': 5.5, 'color': '#4ecdc4'},
            {'label': 'Exhala', 'seconds': 5.5, 'color': '#7c6dfa'},
        ],
        'total_cycle': 11,
        'recommended_cycles': 18,
        'note': '3 minutos · Ideal antes de tomar decisiones',
    },
    'caja': {
        'name': 'Respiración en Caja',
        'desc': 'Cuatro fases iguales para calmar el sistema nervioso y centrar la atención.',
        'phases': [
            {'label': 'Inhala', 'seconds': 4, 'color': '#4ecdc4'},
            {'label': 'Sostén', 'seconds': 4, 'color': '#c8a855'},
            {'label': 'Exhala', 'seconds': 4, 'color': '#7c6dfa'},
            {'label': 'Sostén', 'seconds': 4, 'color': '#f4a035'},
        ],
        'total_cycle': 16,
        'recommended_cycles': 5,
        'note': '~1.5 minutos · Ideal para el estrés agudo',
    },
    'relax': {
        'name': 'Relajación 4-7-8',
        'desc': 'Activa el nervio vago y lleva al cuerpo hacia el descanso profundo.',
        'phases': [
            {'label': 'Inhala', 'seconds': 4, 'color': '#4ecdc4'},
            {'label': 'Sostén', 'seconds': 7, 'color': '#c8a855'},
            {'label': 'Exhala', 'seconds': 8, 'color': '#7c6dfa'},
        ],
        'total_cycle': 19,
        'recommended_cycles': 4,
        'note': '~1.5 minutos · Ideal para dormir o soltar tensión',
    },
}


@login_required
def sensorial_home(request):
    recent = BreathSession.objects.filter(user=request.user).order_by('-started_at')[:5]
    return render(request, 'sensorial/home.html', {
        'patterns': PATTERNS,
        'recent': recent,
    })


@login_required
def breath_session(request, pattern):
    if pattern not in PATTERNS:
        from django.shortcuts import redirect
        return redirect('sensorial:home')
    p = PATTERNS[pattern]
    return render(request, 'sensorial/breath.html', {
        'pattern_key': pattern,
        'pattern': p,
        'phases_json': json.dumps(p['phases']),
    })


@login_required
@require_POST
def log_session(request):
    try:
        data = json.loads(request.body)
        pattern = data.get('pattern', '')
        cycles = int(data.get('cycles', 0))
        duration = int(data.get('duration', 0))
        if pattern in PATTERNS and cycles > 0:
            BreathSession.objects.create(
                user=request.user,
                pattern=pattern,
                cycles_completed=cycles,
                duration_seconds=duration,
            )
        return JsonResponse({'ok': True})
    except Exception:
        return JsonResponse({'ok': False}, status=400)
