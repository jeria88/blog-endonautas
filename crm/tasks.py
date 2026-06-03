from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def _send_sequence_email(subscriber_id, step_id):
    """Lógica pura de envío — llamable sin Celery."""
    from django.template import Template, Context
    from .models import Subscriber, SequenceStep, SentEmail

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

    from .brevo_api import send_via_brevo

    ok, error_msg, message_id = send_via_brevo(subject, html, subscriber.email, subscriber.name or "", plain)
    status = "sent" if ok else "failed"
    if ok:
        logger.info(f"Enviado: {subject} → {subscriber.email}")
    else:
        logger.error(f"FALLO enviando {subject} → {subscriber.email}: {error_msg}")

    SentEmail.objects.create(
        subscriber=subscriber,
        template=step.template,
        sequence=step.sequence,
        status=status,
        error_message=error_msg,
        brevo_message_id=message_id or "",
    )
    return f"{'ok' if status == 'sent' else 'fail'}: {subscriber.email}"


def _process_sequence_steps():
    """
    Lógica pura del flywheel — llamable sin Celery.
    Para cada suscripción activa revisa qué pasos están vencidos y los envía.
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

                try:
                    _send_sequence_email(subscription.subscriber_id, step.id)
                    processed += 1
                except Exception as e:
                    logger.error(f"Error enviando paso {step.id} a {subscription.subscriber.email}: {e}")

    logger.info(f"process_sequence_steps: {processed} emails encolados")
    return f"Encolados: {processed}"


# ── Celery tasks (wrappean las funciones puras) ──────────────────────────────

@shared_task
def send_sequence_email(subscriber_id, step_id):
    return _send_sequence_email(subscriber_id, step_id)


@shared_task
def process_sequence_steps():
    return _process_sequence_steps()


def trigger_sequence_for_subscriber(subscriber_id, sequence_id):
    """Gatilla el email inmediato de una secuencia. Sin Celery."""
    from .models import EmailSequence

    sequence = EmailSequence.objects.get(id=sequence_id, is_active=True)
    count = 0
    for step in sequence.steps.order_by("step_number"):
        if step.delay_days == 0:
            _send_sequence_email(subscriber_id, step.id)
            count += 1
    return f"Secuencia '{sequence.name}': {count} email(es) inmediato(s) enviado(s)"
