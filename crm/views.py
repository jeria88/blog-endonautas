from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django import forms
from .models import Subscriber, EmailList, EmailSequence, SentEmail, Subscription, EmailTemplate, PipelineStage, PipelineLog, ContactNote, Segment, Tag, ContactTag, Broadcast, EmailEvent

import logging

logger = logging.getLogger(__name__)


@staff_member_required
def crm_dashboard(request):
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    total_sequences = EmailSequence.objects.filter(is_active=True).count()
    total_templates = EmailTemplate.objects.count()
    recent_emails = SentEmail.objects.select_related("subscriber", "template", "sequence").order_by("-sent_at")[:20]

    lists = EmailList.objects.prefetch_related("sequences").all()
    lists_data = []
    for lst in lists:
        lists_data.append({
            "list": lst,
            "count": lst.subscribers.filter(subscriber__is_active=True).count(),
            "sequences": lst.sequences.filter(is_active=True),
        })

    sent_total = SentEmail.objects.filter(status="sent").count()
    failed_total = SentEmail.objects.filter(status="failed").count()

    # Métricas de engagement (Capa 3) — últimos 30 días
    from django.utils import timezone
    from datetime import timedelta
    engagement = None
    try:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_events = EmailEvent.objects.filter(occurred_at__gte=thirty_days_ago)
        total_opens = recent_events.filter(event_type="opened").count()
        total_clicks = recent_events.filter(event_type="clicked").count()
        total_bounces = recent_events.filter(event_type="bounced").count()
        total_unsubscribes = recent_events.filter(event_type="unsubscribed").count()
        recent_sent = SentEmail.objects.filter(sent_at__gte=thirty_days_ago, status="sent").count()
        engagement = {
            "total_opens": total_opens,
            "total_clicks": total_clicks,
            "total_bounces": total_bounces,
            "total_unsubscribes": total_unsubscribes,
            "open_rate": round((total_opens / recent_sent) * 100, 1) if recent_sent > 0 else None,
            "click_rate": round((total_clicks / recent_sent) * 100, 1) if recent_sent > 0 else None,
        }
    except Exception:
        pass

    return render(request, "crm/dashboard.html", {
        "total_subscribers": total_subscribers,
        "total_sequences": total_sequences,
        "total_templates": total_templates,
        "sent_total": sent_total,
        "failed_total": failed_total,
        "lists_data": lists_data,
        "recent_emails": recent_emails,
        "engagement": engagement,
    })


@staff_member_required
def crm_subscribers(request):
    list_slug = request.GET.get("list")
    tag_id = request.GET.get("tag")
    search = request.GET.get("q", "").strip()

    qs = Subscriber.objects.prefetch_related("subscriptions__email_list", "contact_tags__tag").order_by("-created_at")
    if list_slug:
        qs = qs.filter(subscriptions__email_list__slug=list_slug)
    if tag_id:
        qs = qs.filter(contact_tags__tag_id=tag_id)
    if search:
        qs = qs.filter(email__icontains=search)

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page"))
    lists = EmailList.objects.all()
    all_tags = Tag.objects.order_by("name")

    return render(request, "crm/subscribers.html", {
        "subscribers": page,
        "total": paginator.count,
        "lists": lists,
        "all_tags": all_tags,
        "current_list": list_slug,
        "current_tag": tag_id,
        "search": search,
    })


@staff_member_required
def crm_sequences(request):
    sequences = (
        EmailSequence.objects
        .select_related("email_list")
        .prefetch_related("steps__template")
        .order_by("name")
    )
    return render(request, "crm/sequences.html", {"sequences": sequences})


# ── CRUD de Listas ──────────────────────────────────────────────────────────


@staff_member_required
def crm_lists(request):
    """Listado de listas con opciones de gestión."""
    lists = EmailList.objects.annotate(
        sub_count=models.Count(
            "subscribers",
            filter=models.Q(subscribers__subscriber__is_active=True),
            distinct=True,
        )
    ).prefetch_related("sequences").order_by("name")
    return render(request, "crm/lists.html", {"lists": lists})


@staff_member_required
def crm_list_create(request):
    """Crear una nueva lista."""
    if request.method == "POST":
        form = ListForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lista '{form.cleaned_data['name']}' creada.")
            return redirect("crm:lists")
    else:
        form = ListForm()
    return render(request, "crm/list_form.html", {"form": form, "title": "Crear lista"})


@staff_member_required
def crm_list_edit(request, list_id):
    """Editar una lista existente."""
    lst = get_object_or_404(EmailList, id=list_id)
    if request.method == "POST":
        form = ListForm(request.POST, instance=lst)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lista '{form.cleaned_data['name']}' actualizada.")
            return redirect("crm:lists")
    else:
        form = ListForm(instance=lst)
    return render(request, "crm/list_form.html", {"form": form, "title": "Editar lista", "list_obj": lst})


@staff_member_required
def crm_list_delete(request, list_id):
    """Eliminar una lista."""
    lst = get_object_or_404(EmailList, id=list_id)
    if request.method == "POST":
        name = lst.name
        lst.delete()
        messages.success(request, f"Lista '{name}' eliminada.")
        return redirect("crm:lists")
    return render(request, "crm/list_confirm_delete.html", {"list_obj": lst})


@staff_member_required
def crm_list_detail(request, list_id):
    """Detalle de lista con suscriptores y secuencias."""
    lst = get_object_or_404(EmailList.objects.prefetch_related("sequences__steps__template"), id=list_id)
    subscribers = (
        Subscriber.objects
        .filter(subscriptions__email_list=lst, is_active=True)
        .annotate(
            email_count=models.Count(
                "sent_emails",
                filter=models.Q(sent_emails__status="sent"),
            ),
            last_sent=models.Max("sent_emails__sent_at"),
        )
        .order_by("-created_at")
    )
    paginator = Paginator(subscribers, 50)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "crm/list_detail.html", {
        "list_obj": lst,
        "subscribers": page,
        "total": paginator.count,
    })


@staff_member_required
def crm_templates(request):
    templates = EmailTemplate.objects.order_by("name")
    return render(request, "crm/templates_list.html", {"templates": templates})


@staff_member_required
def crm_template_preview(request, template_id):
    tmpl = get_object_or_404(EmailTemplate, id=template_id)
    return render(request, "crm/template_preview.html", {"tmpl": tmpl})


@staff_member_required
def crm_sequence_run(request, sequence_id):
    from .tasks import trigger_sequence_for_subscriber
    sequence = get_object_or_404(EmailSequence, id=sequence_id)
    subscriber_id = request.GET.get("subscriber_id")
    if not subscriber_id:
        return JsonResponse({"status": "error", "message": "Falta subscriber_id"}, status=400)
    trigger_sequence_for_subscriber.delay(int(subscriber_id), sequence.id)
    return JsonResponse({"status": "ok", "message": f"Secuencia '{sequence.name}' iniciada"})




# ── Campañas ────────────────────────────────────────────────────────────────────


@staff_member_required
def crm_campaigns(request):
    """Dashboard de campañas con estado de cada secuencia."""
    from django.db.models import Q

    lists = EmailList.objects.annotate(
        sub_count=Count("subscribers", filter=Q(subscribers__subscriber__is_active=True), distinct=True),
    ).prefetch_related("sequences__steps__template").order_by("name")

    campaigns = []
    for lst in lists:
        for seq in lst.sequences.all():
            steps_data = []
            for step in seq.steps.order_by("step_number"):
                sent_count = SentEmail.objects.filter(sequence=seq, template=step.template, status="sent").count()
                pending_count = SentEmail.objects.filter(sequence=seq, template=step.template, status="pending").count()
                failed_count = SentEmail.objects.filter(sequence=seq, template=step.template, status="failed").count()
                steps_data.append({
                    "step": step,
                    "sent": sent_count,
                    "pending": pending_count,
                    "failed": failed_count,
                    "total": sent_count + pending_count + failed_count,
                })
            campaigns.append({
                "list": lst,
                "sequence": seq,
                "steps": steps_data,
                "total_sent": sum(s["sent"] for s in steps_data),
                "total_pending": sum(s["pending"] for s in steps_data),
                "total_failed": sum(s["failed"] for s in steps_data),
            })

    return render(request, "crm/campaigns.html", {
        "campaigns": campaigns,
        "total_subscribers": Subscriber.objects.filter(is_active=True).count(),
        "total_sent": SentEmail.objects.filter(status="sent").count(),
        "total_pending": SentEmail.objects.filter(status="pending").count(),
        "total_failed": SentEmail.objects.filter(status="failed").count(),
    })


@staff_member_required
def crm_run_scheduler(request):
    """Ejecuta el flywheel manualmente."""
    from .tasks import _process_sequence_steps
    try:
        result = _process_sequence_steps()
        messages.success(request, f"Scheduler ejecutado: {result}")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("crm:dashboard")


@staff_member_required
def crm_subscriber_detail(request, subscriber_id):
    """Detalle de un suscriptor con historial completo."""
    subscriber = get_object_or_404(Subscriber.objects.prefetch_related(
        "subscriptions__email_list", "sent_emails__template", "sent_emails__sequence",
        "contact_tags__tag", "notes", "pipeline_logs__stage"
    ), id=subscriber_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle_active":
            subscriber.is_active = not subscriber.is_active
            subscriber.save()
            messages.success(request, f"Suscriptor {'activado' if subscriber.is_active else 'desactivado'}.")
        elif action == "update_name":
            subscriber.name = request.POST.get("name", "").strip()
            subscriber.save()
            messages.success(request, "Nombre actualizado.")
        elif action == "remove_list":
            list_id = request.POST.get("list_id")
            Subscription.objects.filter(subscriber=subscriber, email_list_id=list_id).delete()
            messages.success(request, "Suscripción eliminada.")
        elif action == "add_tag":
            tag_id = request.POST.get("tag_id")
            if tag_id:
                ContactTag.objects.get_or_create(subscriber=subscriber, tag_id=tag_id)
                messages.success(request, "Tag agregado.")
        elif action == "remove_tag":
            tag_id = request.POST.get("tag_id")
            ContactTag.objects.filter(subscriber=subscriber, tag_id=tag_id).delete()
            messages.success(request, "Tag eliminado.")
        return redirect("crm:subscriber_detail", subscriber_id=subscriber.id)

    all_tags = Tag.objects.order_by("name")
    subscriber_tag_ids = set(subscriber.contact_tags.values_list("tag_id", flat=True))

    return render(request, "crm/subscriber_detail.html", {
        "subscriber": subscriber,
        "sent_emails": subscriber.sent_emails.order_by("-sent_at"),
        "subscriptions": subscriber.subscriptions.select_related("email_list").all(),
        "lists": EmailList.objects.all(),
        "all_tags": all_tags,
        "subscriber_tag_ids": subscriber_tag_ids,
        "pipeline_logs": subscriber.pipeline_logs.select_related("stage").order_by("-entered_at")[:10],
        "email_events": subscriber.email_events.select_related("sent_email__template").order_by("-occurred_at")[:50],
    })


# ── Diagnóstico SMTP ─────────────────────────────────────────────────────────

@staff_member_required
def crm_test_smtp(request):
    """Diagnostico: prueba la API de Brevo (sin restriccion de IP)."""
    from django.conf import settings
    import requests

    results = []
    api_key = settings.BREVO_API_KEY
    results.append(("BREVO_API_KEY", api_key[:15] + "..." if api_key else "NO CONFIGURADA"))
    results.append(("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL))

    # Probar API key con GET account
    if api_key:
        try:
            resp = requests.get(
                "https://api.brevo.com/v3/account",
                headers={"api-key": api_key},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get("email", "?")
                results.append(("Conexion API Brevo", f"OK - Cuenta: {email}"))
            else:
                results.append(("Conexion API Brevo", f"FALLO: {resp.status_code} {resp.text[:100]}"))
        except Exception as e:
            results.append(("Conexion API Brevo", f"FALLO: {e}"))
    else:
        results.append(("Conexion API Brevo", "Saltado: sin API key"))

    # Probar envio real via API
    if api_key:
        try:
            from crm.brevo_api import send_via_brevo
            ok, err = send_via_brevo(
                subject="[Diagnostico] Prueba API Brevo",
                html_content="<p>Si ves esto, la API de Brevo funciona.</p>",
                to_email=settings.DEFAULT_FROM_EMAIL,
                to_name="Test",
            )
            if ok:
                results.append(("Envio de prueba", f"OK -> {settings.DEFAULT_FROM_EMAIL}"))
            else:
                results.append(("Envio de prueba", f"FALLO: {err}"))
        except Exception as e:
            results.append(("Envio de prueba", f"FALLO: {e}"))

    return render(request, "crm/smtp_diag.html", {"results": results})



# ── Pipeline ─────────────────────────────────────────────────────────────────


@staff_member_required
def crm_pipeline(request):
    """Vista del pipeline con suscriptores por etapa."""
    stages = PipelineStage.objects.all().order_by("order")
    stages_data = []
    for stage in stages:
        subscriber_ids = PipelineLog.objects.filter(stage=stage).values_list("subscriber", flat=True).distinct()
        subscribers = Subscriber.objects.filter(id__in=subscriber_ids, is_active=True).order_by("-created_at")
        stages_data.append({
            "stage": stage,
            "subscribers": subscribers,
            "count": subscribers.count(),
        })
    return render(request, "crm/pipeline.html", {"stages": stages_data})


@staff_member_required
def crm_pipeline_move(request, subscriber_id, stage_slug):
    """Mueve un suscriptor a una etapa del pipeline."""
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    stage = get_object_or_404(PipelineStage, slug=stage_slug)
    PipelineLog.objects.create(subscriber=subscriber, stage=stage)
    messages.success(request, f"{subscriber.email} movido a {stage.name}")
    return redirect(request.META.get("HTTP_REFERER", "crm:pipeline"))


# ── Notas ────────────────────────────────────────────────────────────────────


@staff_member_required
def crm_add_note(request, subscriber_id):
    """Agrega una nota a un suscriptor."""
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            ContactNote.objects.create(
                subscriber=subscriber,
                content=content,
                created_by=request.user.get_full_name() or request.user.username,
            )
            messages.success(request, "Nota agregada.")
    return redirect("crm:subscriber_detail", subscriber_id=subscriber.id)


# ── Segmentos ────────────────────────────────────────────────────────────────


@staff_member_required
def crm_segments(request):
    """Listado de segmentos con conteo."""
    segments = Segment.objects.annotate(
        sub_count=Count("id")  # placeholder, lo reemplazamos con get_subscribers
    ).order_by("name")
    # Agregamos conteo real
    for seg in segments:
        seg.real_count = seg.get_subscribers().count()
    return render(request, "crm/segments.html", {"segments": segments})


# ── Formularios ──────────────────────────────────────────────────────────────


class ListForm(forms.ModelForm):
    class Meta:
        model = EmailList
        fields = ["name", "slug", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Ej: Endonautas - Newsletter"}),
            "slug": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Ej: newsletter"}),
            "description": forms.Textarea(attrs={"class": "crm-input", "rows": 3, "placeholder": "Descripción opcional"}),
        }
        help_texts = {
            "slug": "Identificador único para URLs. Solo letras, números y guiones.",
        }


class TemplateEditForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ["subject", "html_content", "plain_text_content"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Asunto del email"}),
            "html_content": forms.Textarea(attrs={"class": "crm-input crm-code", "rows": 20, "wrap": "off"}),
            "plain_text_content": forms.Textarea(attrs={"class": "crm-input", "rows": 6}),
        }
        help_texts = {
            "html_content": "Usa <code>{{ nombre }}</code> para personalizar. El resto de marcadores se inyectan automáticamente.",
        }


@staff_member_required
def crm_template_edit(request, template_id):
    tmpl = get_object_or_404(EmailTemplate, id=template_id)
    if request.method == "POST":
        form = TemplateEditForm(request.POST, instance=tmpl)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plantilla '{tmpl.name}' actualizada.")
            return redirect("crm:templates")
    else:
        form = TemplateEditForm(instance=tmpl)
    return render(request, "crm/template_edit.html", {"form": form, "tmpl": tmpl})


# ── Tags ──────────────────────────────────────────────────────────────────────


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "slug", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Ej: Interesado"}),
            "slug": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Ej: interesado"}),
            "color": forms.TextInput(attrs={"class": "crm-input", "type": "color", "style": "width:80px;height:36px;padding:2px;"}),
        }


@staff_member_required
def crm_tags(request):
    tags = Tag.objects.annotate(sub_count=Count("contact_tags")).order_by("name")
    return render(request, "crm/tags.html", {"tags": tags})


@staff_member_required
def crm_tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tag '{form.cleaned_data['name']}' creado.")
            return redirect("crm:tags")
    else:
        form = TagForm()
    return render(request, "crm/tag_form.html", {"form": form, "action": "Crear"})


@staff_member_required
def crm_tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tag '{tag.name}' actualizado.")
            return redirect("crm:tags")
    else:
        form = TagForm(instance=tag)
    return render(request, "crm/tag_form.html", {"form": form, "action": "Editar", "tag": tag})


@staff_member_required
def crm_tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == "POST":
        tag.delete()
        messages.success(request, f"Tag '{tag.name}' eliminado.")
        return redirect("crm:tags")
    return render(request, "crm/tag_confirm_delete.html", {"tag": tag})


# ── Broadcasts ────────────────────────────────────────────────────────────────


class BroadcastForm(forms.ModelForm):
    class Meta:
        model = Broadcast
        fields = ["name", "subject", "html_content", "plain_text_content", "target_list", "target_segment"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Ej: Newsletter semanal #5"}),
            "subject": forms.TextInput(attrs={"class": "crm-input", "placeholder": "Asunto del email"}),
            "html_content": forms.Textarea(attrs={"class": "crm-input crm-code", "rows": 16, "wrap": "off"}),
            "plain_text_content": forms.Textarea(attrs={"class": "crm-input", "rows": 4}),
            "target_list": forms.Select(attrs={"class": "crm-select"}),
            "target_segment": forms.Select(attrs={"class": "crm-select"}),
        }
        help_texts = {
            "target_list": "Elige una lista O un segmento. Si eliges ambos, se usa la lista.",
            "target_segment": "Segmento de suscriptores al que enviar.",
        }


@staff_member_required
def crm_broadcasts(request):
    broadcasts = Broadcast.objects.select_related("target_list", "target_segment").order_by("-created_at")
    return render(request, "crm/broadcasts.html", {"broadcasts": broadcasts})


@staff_member_required
def crm_broadcast_create(request):
    if request.method == "POST":
        form = BroadcastForm(request.POST)
        if form.is_valid():
            broadcast = form.save(commit=False)
            broadcast.status = "draft"
            broadcast.save()
            messages.success(request, f"Borrador '{broadcast.name}' guardado.")
            return redirect("crm:broadcast_detail", broadcast_id=broadcast.id)
    else:
        form = BroadcastForm()
    return render(request, "crm/broadcast_form.html", {"form": form, "action": "Crear"})


@staff_member_required
def crm_broadcast_detail(request, broadcast_id):
    broadcast = get_object_or_404(
        Broadcast.objects.select_related("target_list", "target_segment"),
        id=broadcast_id,
    )
    sent_emails = SentEmail.objects.filter(
        template__isnull=True,  # broadcast emails don't have a template FK in current model
    ).order_by("-sent_at")[:50]

    # Get recipient count
    recipient_count = 0
    if broadcast.target_list:
        recipient_count = broadcast.target_list.subscribers.filter(subscriber__is_active=True).count()
    elif broadcast.target_segment:
        recipient_count = broadcast.target_segment.get_subscribers().count()

    return render(request, "crm/broadcast_detail.html", {
        "broadcast": broadcast,
        "recipient_count": recipient_count,
    })


@staff_member_required
def crm_broadcast_send(request, broadcast_id):
    """Envía el broadcast a todos los destinatarios."""
    broadcast = get_object_or_404(Broadcast, id=broadcast_id)

    if broadcast.status not in ("draft", "failed"):
        messages.error(request, "Este broadcast ya fue enviado o está en proceso.")
        return redirect("crm:broadcast_detail", broadcast_id=broadcast.id)

    # Obtener destinatarios
    if broadcast.target_list:
        recipients = Subscriber.objects.filter(
            subscriptions__email_list=broadcast.target_list,
            is_active=True,
        ).distinct()
    elif broadcast.target_segment:
        recipients = broadcast.target_segment.get_subscribers()
    else:
        messages.error(request, "No hay destinatarios configurados.")
        return redirect("crm:broadcast_detail", broadcast_id=broadcast.id)

    broadcast.status = "sending"
    broadcast.total_recipients = recipients.count()
    broadcast.total_sent = 0
    broadcast.total_failed = 0
    broadcast.save(update_fields=["status", "total_recipients", "total_sent", "total_failed"])

    from django.template import Template, Context
    from .brevo_api import send_via_brevo
    from django.utils import timezone

    sent_count = 0
    failed_count = 0

    for subscriber in recipients:
        context = Context({
            "nombre": subscriber.name or "amigo",
            "email": subscriber.email,
        })
        subject = Template(broadcast.subject).render(context)
        html = Template(broadcast.html_content).render(context)
        plain = Template(broadcast.plain_text_content).render(context) if broadcast.plain_text_content else ""

        ok, error_msg = send_via_brevo(subject, html, subscriber.email, subscriber.name or "", plain)
        if ok:
            sent_count += 1
        else:
            failed_count += 1
            logger.error(f"Broadcast {broadcast.id} fallo -> {subscriber.email}: {error_msg}")

    broadcast.total_sent = sent_count
    broadcast.total_failed = failed_count
    broadcast.status = "sent" if failed_count == 0 else "sent"
    broadcast.sent_at = timezone.now()
    broadcast.save(update_fields=["total_sent", "total_failed", "status", "sent_at"])

    messages.success(
        request,
        f"Broadcast enviado: {sent_count} exitosos, {failed_count} fallidos de {recipients.count()} destinatarios."
    )
    return redirect("crm:broadcast_detail", broadcast_id=broadcast.id)
