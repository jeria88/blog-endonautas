@staff_member_required
def crm_campaigns(request):
    """Dashboard de campañas con estado de cada secuencia."""
    from django.db.models import Count, Q, Max, Min

    lists = EmailList.objects.annotate(
        sub_count=Count("subscribers", filter=Q(subscribers__subscriber__is_active=True), distinct=True),
    ).prefetch_related("sequences__steps__template").order_by("name")

    campaigns = []
    for lst in lists:
        for seq in lst.sequences.all():
            steps_data = []
            for step in seq.steps.order_by("step_number"):
                sent_count = SentEmail.objects.filter(
                    sequence=seq, template=step.template, status="sent"
                ).count()
                pending_count = SentEmail.objects.filter(
                    sequence=seq, template=step.template, status="pending"
                ).count()
                failed_count = SentEmail.objects.filter(
                    sequence=seq, template=step.template, status="failed"
                ).count()
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

    now = timezone.now()
    context = {
        "campaigns": campaigns,
        "total_subscribers": Subscriber.objects.filter(is_active=True).count(),
        "total_sent": SentEmail.objects.filter(status="sent").count(),
        "total_pending": SentEmail.objects.filter(status="pending").count(),
        "total_failed": SentEmail.objects.filter(status="failed").count(),
        "now": now,
    }
    return render(request, "crm/campaigns.html", context)


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
        "subscriptions__email_list", "sent_emails__template", "sent_emails__sequence"
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
        return redirect("crm:subscriber_detail", subscriber_id=subscriber.id)

    return render(request, "crm/subscriber_detail.html", {
        "subscriber": subscriber,
        "sent_emails": subscriber.sent_emails.order_by("-sent_at"),
        "subscriptions": subscriber.subscriptions.select_related("email_list").all(),
        "lists": EmailList.objects.all(),
    })
