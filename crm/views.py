from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
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
