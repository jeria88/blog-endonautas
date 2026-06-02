import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
@require_POST
def brevo_subscribe(request):
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()
    list_id = int(request.POST.get('list_id', getattr(settings, 'BREVO_DEFAULT_LIST_ID', 3)))
    if not email or '@' not in email:
        return JsonResponse({'ok': False, 'error': 'Email inválido'}, status=400)

    api_key = getattr(settings, 'BREVO_API_KEY', '')
    if not api_key:
        return JsonResponse({'ok': False, 'error': 'Servicio no configurado'}, status=503)

    try:
        payload = {
            'email': email,
            'listIds': [list_id],
            'updateEnabled': True,
        }
        if name:
            payload['attributes'] = {'FIRSTNAME': name}

        resp = requests.post(
            'https://api.brevo.com/v3/contacts',
            json=payload,
            headers={
                'api-key': api_key,
                'content-type': 'application/json',
                'accept': 'application/json',
            },
            timeout=8,
        )
        if resp.status_code in (200, 201, 204):
            return JsonResponse({'ok': True})
        if resp.status_code == 400 and 'already' in resp.text.lower():
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'No se pudo suscribir'}, status=502)
    except requests.RequestException:
        return JsonResponse({'ok': False, 'error': 'Error de conexión'}, status=502)


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
