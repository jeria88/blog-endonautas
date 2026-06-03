from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django import forms
from .models import Subscriber, EmailList, EmailSequence, SentEmail, Subscription, EmailTemplate


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

    return render(request, "crm/dashboard.html", {
        "total_subscribers": total_subscribers,
        "total_sequences": total_sequences,
        "total_templates": total_templates,
        "sent_total": sent_total,
        "failed_total": failed_total,
        "lists_data": lists_data,
        "recent_emails": recent_emails,
    })


@staff_member_required
def crm_subscribers(request):
    list_slug = request.GET.get("list")
    search = request.GET.get("q", "").strip()

    qs = Subscriber.objects.prefetch_related("subscriptions__email_list").order_by("-created_at")
    if list_slug:
        qs = qs.filter(subscriptions__email_list__slug=list_slug)
    if search:
        qs = qs.filter(email__icontains=search)

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page"))
    lists = EmailList.objects.all()

    return render(request, "crm/subscribers.html", {
        "subscribers": page,
        "total": paginator.count,
        "lists": lists,
        "current_list": list_slug,
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
