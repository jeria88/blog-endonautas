from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings


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
