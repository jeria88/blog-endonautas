from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from .models import Subscriber, EmailList, EmailSequence, SentEmail, Subscription


@staff_member_required
def crm_dashboard(request):
    """Dashboard principal del CRM."""
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    total_lists = EmailList.objects.count()
    total_sequences = EmailSequence.objects.filter(is_active=True).count()
    recent_emails = SentEmail.objects.select_related("subscriber", "template").order_by("-sent_at")[:20]

    context = {
        "total_subscribers": total_subscribers,
        "total_lists": total_lists,
        "total_sequences": total_sequences,
        "recent_emails": recent_emails,
    }
    return render(request, "crm/dashboard.html", context)


@staff_member_required
def crm_subscribers(request):
    """Listado de suscriptores."""
    subscribers = Subscriber.objects.prefetch_related("subscriptions__email_list").order_by("-created_at")
    paginator = Paginator(subscribers, 50)
    page = request.GET.get("page")
    subscribers_page = paginator.get_page(page)

    context = {
        "subscribers": subscribers_page,
        "total": paginator.count,
    }
    return render(request, "crm/subscribers.html", context)


@staff_member_required
def crm_sequences(request):
    """Listado de secuencias de emails."""
    sequences = EmailSequence.objects.select_related("email_list").prefetch_related("steps__template").order_by("name")

    context = {
        "sequences": sequences,
    }
    return render(request, "crm/sequences.html", context)


@staff_member_required
def crm_sequence_run(request, sequence_id):
    """Ejecutar una secuencia manualmente para testing."""
    from .tasks import run_sequence
    sequence = get_object_or_404(EmailSequence, id=sequence_id)
    run_sequence.delay(sequence.id)
    return JsonResponse({"status": "ok", "message": f"Secuencia '{sequence.name}' iniciada"})
