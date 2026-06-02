from celery import shared_task
from django.core.mail import send_mail
from django.template import Template, Context
from django.conf import settings
from .models import EmailSequence, SequenceStep, Subscriber, SentEmail
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_sequence_email(subscriber_id, step_id):
    """Enviar un email individual de una secuencia."""
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id, is_active=True)
        step = SequenceStep.objects.select_related("template", "sequence").get(id=step_id)

        # Renderizar template con datos del suscriptor
        subject_template = Template(step.template.subject)
        html_template = Template(step.template.html_content)

        context = Context({
            "nombre": subscriber.name or "amigo",
            "email": subscriber.email,
        })

        subject = subject_template.render(context)
        html_content = html_template.render(context)

        # Enviar email
        send_mail(
            subject=subject,
            message="",  # plain text vacío, usamos html
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_content,
            fail_silently=False,
        )

        # Registrar envío exitoso
        SentEmail.objects.create(
            subscriber=subscriber,
            template=step.template,
            sequence=step.sequence,
            status="sent",
        )

        logger.info(f"Email enviado: {subject} → {subscriber.email}")

    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        SentEmail.objects.create(
            subscriber=subscriber,
            template=step.template,
            sequence=step.sequence,
            status="failed",
            error_message=str(e),
        )


@shared_task
def trigger_sequence(subscriber_id, sequence_id):
    """Gatillar una secuencia completa para un suscriptor."""
    try:
        sequence = EmailSequence.objects.get(id=sequence_id, is_active=True)
        steps = sequence.steps.select_related("template").order_by("step_number")

        for step in steps:
            # Programar cada email con su delay
            if step.delay_days == 0:
                # Enviar inmediatamente
                send_sequence_email.delay(subscriber_id, step.id)
            else:
                # Programar para después
                from datetime import timedelta
                send_sequence_email.apply_async(
                    args=[subscriber_id, step.id],
                    countdown=step.delay_days * 86400,  # días a segundos
                )

        logger.info(f"Secuencia '{sequence.name}' iniciada para suscriptor {subscriber_id}")

    except Exception as e:
        logger.error(f"Error gatillando secuencia: {e}")
