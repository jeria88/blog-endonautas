from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_sequence_email(subscriber_id, step_id):
    """Renderiza y encola un email de secuencia vía post_office."""
    from post_office import mail as po_mail
    from django.template import Template, Context
    from .models import Subscriber, SequenceStep, SentEmail

    try:
        subscriber = Subscriber.objects.get(id=subscriber_id, is_active=True)
        step = SequenceStep.objects.select_related("template", "sequence").get(id=step_id)

        already_sent = SentEmail.objects.filter(
            subscriber=subscriber,
            template=step.template,
            sequence=step.sequence,
            status="sent",
        ).exists()
        if already_sent:
            return f"Ya enviado: {step.template} → {subscriber.email}"

        context = Context({
            "nombre": subscriber.name or "amigo",
            "email": subscriber.email,
        })
        subject = Template(step.template.subject).render(context)
        html = Template(step.template.html_content).render(context)
        plain = Template(step.template.plain_text_content).render(context) if step.template.plain_text_content else ""

        po_mail.send(
            recipients=[subscriber.email],
            subject=subject,
            html_message=html,
            message=plain,
        )

        SentEmail.objects.create(
            subscriber=subscriber,
            template=step.template,
            sequence=step.sequence,
            status="sent",
        )
        logger.info(f"Encolado: {subject} → {subscriber.email}")
        return f"ok: {subscriber.email}"

    except Exception as e:
        logger.error(f"Error encolando email: {e}")
        try:
            from .models import Subscriber, SequenceStep, SentEmail
            sub = Subscriber.objects.get(id=subscriber_id)
            step = SequenceStep.objects.select_related("template", "sequence").get(id=step_id)
            SentEmail.objects.create(
                subscriber=sub,
                template=step.template,
                sequence=step.sequence,
                status="failed",
                error_message=str(e),
            )
        except Exception:
            pass
        raise


@shared_task
def process_sequence_steps():
    """
    Cron principal del flywheel. Corre cada hora.
    Para cada suscripción activa revisa qué pasos de secuencia están vencidos
    y los encola si no se enviaron ya.
    """
    from .models import Subscription, EmailSequence, SentEmail

    now = timezone.now()
    processed = 0

    subscriptions = (
        Subscription.objects
        .filter(subscriber__is_active=True)
        .select_related("subscriber", "email_list")
    )

    for subscription in subscriptions:
        sequences = EmailSequence.objects.filter(
            email_list=subscription.email_list,
            is_active=True,
        ).prefetch_related("steps__template")

        for sequence in sequences:
            for step in sequence.steps.order_by("step_number"):
                due_at = subscription.subscribed_at + timedelta(days=step.delay_days)
                if now < due_at:
                    continue

                already = SentEmail.objects.filter(
                    subscriber=subscription.subscriber,
                    template=step.template,
                    sequence=sequence,
                    status="sent",
                ).exists()
                if already:
                    continue

                send_sequence_email.delay(subscription.subscriber_id, step.id)
                processed += 1

    logger.info(f"process_sequence_steps: {processed} emails encolados")
    return f"Encolados: {processed}"


@shared_task
def trigger_sequence_for_subscriber(subscriber_id, sequence_id):
    """Gatilla una secuencia completa para un suscriptor (uso manual/testing)."""
    from .models import EmailSequence

    sequence = EmailSequence.objects.get(id=sequence_id, is_active=True)
    for step in sequence.steps.order_by("step_number"):
        if step.delay_days == 0:
            send_sequence_email.delay(subscriber_id, step.id)
        else:
            eta = timezone.now() + timedelta(days=step.delay_days)
            send_sequence_email.apply_async(args=[subscriber_id, step.id], eta=eta)

    return f"Secuencia '{sequence.name}' iniciada para suscriptor {subscriber_id}"
