import logging
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def brevo_subscribe(request):
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()
    source = request.POST.get('source', '')

    if not email or '@' not in email:
        return JsonResponse({'ok': False, 'error': 'Email inválido'}, status=400)

    from crm.models import Subscriber, EmailList, Subscription, EmailSequence, SentEmail, SequenceStep
    from django.template import Template, Context

    try:
        # Crear o actualizar suscriptor
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        if name and not subscriber.name:
            subscriber.name = name
            subscriber.save()

        # Obtener la lista por slug
        list_slug = request.POST.get('list_slug', '')
        email_list = EmailList.objects.filter(slug=list_slug).first()
        if not email_list:
            return JsonResponse({'ok': False, 'error': 'Lista no encontrada'}, status=404)

        # Crear suscripción
        subscription, sub_created = Subscription.objects.get_or_create(
            subscriber=subscriber,
            email_list=email_list,
            defaults={'source': source}
        )

        # Enviar email inmediato (delay_days=0) vía SMTP directo, sin post_office.
        # Así no depende del scheduler para el primer email.
        sequence = EmailSequence.objects.filter(email_list=email_list, is_active=True).first()
        if sequence:
            first_step = sequence.steps.filter(delay_days=0).select_related('template', 'sequence').order_by('step_number').first()
            if first_step:
                try:
                    tmpl = first_step.template
                    ctx = Context({'nombre': subscriber.name or 'amigo', 'email': subscriber.email})
                    subject = Template(tmpl.subject).render(ctx)
                    html = Template(tmpl.html_content).render(ctx)
                    from crm.brevo_api import send_via_brevo
                    ok_send, error_msg = send_via_brevo(subject, html, subscriber.email, subscriber.name or "")
                    email_status = 'sent' if ok_send else 'failed'
                    if ok_send:
                        logger.info(f"Email inmediato enviado: {subject} -> {subscriber.email}")
                    else:
                        logger.error(f"FALLO email inmediato {subject} -> {subscriber.email}: {error_msg}")
                    SentEmail.objects.create(
                        subscriber=subscriber,
                        template=tmpl,
                        sequence=first_step.sequence,
                        status=email_status,
                        error_message=error_msg,
                    )
                except Exception as e:
                    logger.error(f"Error enviando email inmediato a {email}: {e}")

        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


def contacto_view(request):
    enviado = request.GET.get('enviado') == '1'
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        if nombre and email and mensaje:
            send_mail(
                subject=f'Contacto endonautas.cl — {nombre}',
                message=f'De: {nombre} <{email}>\n\n{mensaje}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'hola@endonautas.cl'),
                recipient_list=['hola@endonautas.cl'],
                fail_silently=True,
            )
            return redirect('/contacto/?enviado=1')
    return render(request, 'home/contact.html', {'enviado': enviado})
