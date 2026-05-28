import json
import calendar
from datetime import date, timedelta, datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import IdeaCongelada, MetricaSemana, PostContenido, SesionRegistro, SetupItem, Tarea

ETAPA_LABELS = {
    '0': 'Etapa 0',
    '1': 'Etapa 1',
    '2': 'Etapa 2',
    'backlog': 'Backlog',
}

ETAPA_COLORS = {
    '0': '#4ecdc4',
    '1': '#EAB308',
    '2': '#a78bfa',
    'backlog': '#52525b',
}

MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _setup_progress():
    total = SetupItem.objects.count()
    done = SetupItem.objects.filter(completado=True).count()
    pct = int(done / total * 100) if total else 0
    return total, done, pct


def _etapa_progress(etapa_key):
    total = Tarea.objects.filter(etapa=etapa_key).count()
    done = Tarea.objects.filter(etapa=etapa_key, estado='listo').count()
    pct = int(done / total * 100) if total else 0
    return total, done, pct


@staff_member_required(login_url='/django-admin/login/')
def index(request):
    today = date.today()
    weekday = today.weekday()  # 0=Monday … 6=Sunday

    setup_total, setup_done, setup_pct = _setup_progress()
    e0_total, e0_done, e0_pct = _etapa_progress('0')

    tareas_urgentes = Tarea.objects.filter(estado='en_curso').order_by('etapa', 'orden')[:5]

    sugerencia = None
    if weekday == 0:
        sugerencia = {
            'tipo': 'semanal',
            'emoji': '◎',
            'texto': 'Hoy es lunes — ¿hacemos el chequeo semanal? (10 min)',
            'url': 'chequeo',
            'label': 'Ir al chequeo',
        }
    elif weekday == 5:
        sugerencia = {
            'tipo': 'quincenal',
            'emoji': '✦',
            'texto': 'Hoy es sábado — ¿es sesión quincenal?',
            'url': 'quincenal',
            'label': 'Iniciar sesión',
        }

    ideas_count = IdeaCongelada.objects.filter(revisada=False).count()
    ultima_sesion = SesionRegistro.objects.first()

    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    return render(request, 'centro/index.html', {
        'today': today,
        'dia_semana': dias_semana[weekday],
        'setup_total': setup_total,
        'setup_done': setup_done,
        'setup_pct': setup_pct,
        'e0_total': e0_total,
        'e0_done': e0_done,
        'e0_pct': e0_pct,
        'tareas_urgentes': tareas_urgentes,
        'sugerencia': sugerencia,
        'ideas_count': ideas_count,
        'ultima_sesion': ultima_sesion,
    })


@staff_member_required(login_url='/django-admin/login/')
def hoja_de_ruta(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        etapa = request.POST.get('etapa', '0')
        descripcion = request.POST.get('descripcion', '').strip()
        if titulo:
            from django.db.models import Max
            max_orden = Tarea.objects.filter(etapa=etapa, estado='pendiente').aggregate(Max('orden'))['orden__max'] or 0
            Tarea.objects.create(titulo=titulo, etapa=etapa, descripcion=descripcion, orden=max_orden + 1)
        return redirect('centro:hoja_de_ruta')

    pendientes = list(Tarea.objects.filter(estado='pendiente').order_by('etapa', 'orden'))
    en_curso = list(Tarea.objects.filter(estado='en_curso').order_by('etapa', 'orden'))
    listas = list(Tarea.objects.filter(estado='listo').order_by('etapa', '-creada_en')[:20])

    # Build etapa progress for header
    etapas_progress = []
    for key in ['0', '1', '2', 'backlog']:
        t, d, p = _etapa_progress(key)
        etapas_progress.append({
            'key': key,
            'label': ETAPA_LABELS[key],
            'color': ETAPA_COLORS[key],
            'total': t,
            'done': d,
            'pct': p,
        })

    return render(request, 'centro/hoja_de_ruta.html', {
        'pendientes': pendientes,
        'en_curso': en_curso,
        'listas': listas,
        'etapa_choices': Tarea.ETAPA_CHOICES,
        'etapa_labels': ETAPA_LABELS,
        'etapa_colors': ETAPA_COLORS,
        'etapas_progress': etapas_progress,
    })


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def tarea_mover(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    data = json.loads(request.body)
    estado = data.get('estado')
    etapa = data.get('etapa')
    if estado in dict(Tarea.ESTADO_CHOICES):
        tarea.estado = estado
    if etapa and etapa in dict(Tarea.ETAPA_CHOICES):
        tarea.etapa = etapa
    tarea.save()
    return JsonResponse({'ok': True})


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def tarea_eliminar(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    tarea.delete()
    return JsonResponse({'ok': True})


@staff_member_required(login_url='/django-admin/login/')
def setup(request):
    items = SetupItem.objects.all()
    by_cat = {}
    for item in items:
        cat_key = item.categoria
        cat_label = item.get_categoria_display()
        if cat_key not in by_cat:
            by_cat[cat_key] = {'label': cat_label, 'items': []}
        by_cat[cat_key]['items'].append(item)

    total, done, pct = _setup_progress()

    return render(request, 'centro/setup.html', {
        'by_cat': by_cat,
        'total': total,
        'done': done,
        'pct': pct,
    })


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def setup_toggle(request, item_id):
    item = get_object_or_404(SetupItem, pk=item_id)
    item.toggle()
    total, done, pct = _setup_progress()
    return JsonResponse({'ok': True, 'completado': item.completado, 'pct': pct, 'done': done})


@staff_member_required(login_url='/django-admin/login/')
def chequeo_semanal(request):
    if request.method == 'POST':
        notas = request.POST.get('notas', '')
        seguidores = int(request.POST.get('seguidores_nuevos', 0) or 0)
        saves = int(request.POST.get('saves_carrusel', 0) or 0)
        comentarios = int(request.POST.get('comentarios_activos', 0) or 0)

        SesionRegistro.objects.create(tipo='semanal', fecha=date.today(), notas=notas)

        semana_lunes = date.today() - timedelta(days=date.today().weekday())
        MetricaSemana.objects.update_or_create(
            semana=semana_lunes,
            defaults={
                'seguidores_nuevos': seguidores,
                'saves_carrusel': saves,
                'comentarios_activos': comentarios,
                'notas': notas,
            }
        )
        return redirect('centro:index')

    return render(request, 'centro/chequeo_semanal.html', {})


@staff_member_required(login_url='/django-admin/login/')
def sesion_quincenal(request):
    if request.method == 'POST':
        notas = request.POST.get('notas', '')
        SesionRegistro.objects.create(tipo='quincenal', fecha=date.today(), notas=notas)
        return redirect('centro:index')

    proximo_post = PostContenido.objects.filter(estado='generado').order_by('fecha_programada').first()

    return render(request, 'centro/sesion_quincenal.html', {
        'proximo_post': proximo_post,
    })


@staff_member_required(login_url='/django-admin/login/')
def metricas(request):
    if request.method == 'POST':
        semana_str = request.POST.get('semana', '')
        try:
            semana = datetime.strptime(semana_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            semana = date.today() - timedelta(days=date.today().weekday())

        MetricaSemana.objects.update_or_create(
            semana=semana,
            defaults={
                'seguidores_nuevos': int(request.POST.get('seguidores_nuevos', 0) or 0),
                'saves_carrusel': int(request.POST.get('saves_carrusel', 0) or 0),
                'comentarios_activos': int(request.POST.get('comentarios_activos', 0) or 0),
                'pdfs_enviados': int(request.POST.get('pdfs_enviados', 0) or 0),
                'emails_abiertos_pct': int(request.POST.get('emails_abiertos_pct', 0) or 0),
                'registros_app': int(request.POST.get('registros_app', 0) or 0),
                'notas': request.POST.get('notas', ''),
            }
        )
        return redirect('centro:metricas')

    metricas_list = list(MetricaSemana.objects.all()[:12])

    # Build JSON for charts
    labels = [str(m.semana) for m in reversed(metricas_list)]
    seguidores_data = [m.seguidores_nuevos for m in reversed(metricas_list)]
    saves_data = [m.saves_carrusel for m in reversed(metricas_list)]
    registros_data = [m.registros_app for m in reversed(metricas_list)]

    hoy_lunes = date.today() - timedelta(days=date.today().weekday())

    return render(request, 'centro/metricas.html', {
        'metricas': metricas_list,
        'chart_labels': json.dumps(labels),
        'chart_seguidores': json.dumps(seguidores_data),
        'chart_saves': json.dumps(saves_data),
        'chart_registros': json.dumps(registros_data),
        'hoy_lunes': hoy_lunes,
    })


@staff_member_required(login_url='/django-admin/login/')
def ideas(request):
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            IdeaCongelada.objects.create(texto=texto)
        return redirect('centro:ideas')

    ideas_list = IdeaCongelada.objects.all()
    sin_revisar = ideas_list.filter(revisada=False).count()
    return render(request, 'centro/ideas.html', {
        'ideas': ideas_list,
        'sin_revisar': sin_revisar,
    })


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def idea_revisar(request, idea_id):
    idea = get_object_or_404(IdeaCongelada, pk=idea_id)
    idea.revisada = not idea.revisada
    idea.save()
    return JsonResponse({'ok': True, 'revisada': idea.revisada})


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def idea_eliminar(request, idea_id):
    idea = get_object_or_404(IdeaCongelada, pk=idea_id)
    idea.delete()
    return JsonResponse({'ok': True})


@staff_member_required(login_url='/django-admin/login/')
def calendario(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    if month < 1:
        month = 12
        year -= 1
    if month > 12:
        month = 1
        year += 1

    posts = PostContenido.objects.filter(
        fecha_programada__year=year,
        fecha_programada__month=month,
    ).order_by('fecha_programada')

    posts_by_day = {}
    for post in posts:
        day = post.fecha_programada.day
        posts_by_day.setdefault(day, []).append(post)

    cal = calendar.monthcalendar(year, month)
    weeks = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': None, 'posts': [], 'is_today': False})
            else:
                week_data.append({
                    'day': day,
                    'is_today': (date(year, month, day) == today),
                    'posts': posts_by_day.get(day, []),
                })
        weeks.append(week_data)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = (month % 12) + 1
    next_year = year + 1 if month == 12 else year

    return render(request, 'centro/calendario.html', {
        'weeks': weeks,
        'year': year,
        'month': month,
        'month_name': MESES[month],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'post_estado_choices': PostContenido.ESTADO_CHOICES,
        'post_tipo_choices': PostContenido.TIPO_CHOICES,
    })


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def post_crear(request):
    fecha_str = request.POST.get('fecha_programada', '')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha = None

    PostContenido.objects.create(
        codigo=request.POST.get('codigo', '').strip(),
        titulo=request.POST.get('titulo', '').strip(),
        tipo=request.POST.get('tipo', 'texto'),
        estado=request.POST.get('estado', 'generado'),
        fecha_programada=fecha,
        cta_tipo=request.POST.get('cta_tipo', '').strip(),
        notas=request.POST.get('notas', '').strip(),
    )

    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('centro:calendario')


@staff_member_required(login_url='/django-admin/login/')
@require_POST
def post_estado(request, post_id):
    post = get_object_or_404(PostContenido, pk=post_id)
    data = json.loads(request.body)
    estado = data.get('estado')
    if estado in dict(PostContenido.ESTADO_CHOICES):
        post.estado = estado
        if estado == 'publicado' and not post.fecha_publicada:
            post.fecha_publicada = date.today()
        post.save()
    return JsonResponse({'ok': True, 'estado': post.estado})
