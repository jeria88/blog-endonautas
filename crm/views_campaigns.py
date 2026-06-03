from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Subscriber, EmailList, EmailSequence, SentEmail, Subscription,
    EmailTemplate, PipelineStage, PipelineLog, ContactNote, Segment,
    Tag, ContactTag, Broadcast,
)


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
    })
