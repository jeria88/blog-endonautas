from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User, UserProfile
from .models import TemporaryProfile


def _is_practicante(user):
    try:
        return user.profile.is_practicante
    except Exception:
        return False


@login_required
def perfil_lista(request):
    if not _is_practicante(request.user):
        return HttpResponseForbidden("Esta función requiere el plan Practicante o Empresa.")
    profiles = TemporaryProfile.objects.filter(
        created_by=request.user, active=True
    ).order_by("-created_at")
    return render(request, "practitioners/lista.html", {"profiles": profiles})


@login_required
@require_POST
def perfil_crear(request):
    if not _is_practicante(request.user):
        return HttpResponseForbidden("Esta función requiere el plan Practicante o Empresa.")
    alias = request.POST.get("alias", "").strip()
    notes = request.POST.get("notes", "").strip()
    allocation = int(request.POST.get("token_allocation", 150))
    if alias:
        TemporaryProfile.objects.create(
            created_by=request.user,
            alias=alias,
            notes=notes,
            token_allocation=allocation,
        )
    return redirect("practitioners:lista")


@login_required
def perfil_detalle(request, pk):
    if not _is_practicante(request.user):
        return HttpResponseForbidden("Esta función requiere el plan Practicante o Empresa.")
    profile = get_object_or_404(TemporaryProfile, pk=pk, created_by=request.user)
    results = profile.test_results.select_related("test").order_by("-completed_at")
    share_url = request.build_absolute_uri(f"/practicantes/acceso/{profile.access_code}/")
    return render(request, "practitioners/detalle.html", {
        "profile": profile,
        "results": results,
        "share_url": share_url,
    })


def perfil_acceso(request, access_code):
    """Vista pública: el cliente abre el link del facilitador."""
    temp = get_object_or_404(TemporaryProfile, access_code=access_code, active=True)

    # Si ya tiene cuenta vinculada, redirigir al dashboard
    if temp.claimed_by:
        if request.user == temp.claimed_by:
            return redirect('dashboard')
        # otra persona autenticada viendo el link — mostrar info básica
        return render(request, "practitioners/acceso.html", {
            "temp": temp, "facilitador": temp.created_by,
            "already_claimed": True,
        })

    # Usuario ya autenticado sin vinculación → vincular directamente
    if request.user.is_authenticated:
        temp.claimed_by = request.user
        temp.save(update_fields=["claimed_by"])
        return redirect('dashboard')

    error = None
    if request.method == "POST":
        nombre   = request.POST.get("nombre", "").strip()
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not nombre or not email or len(password) < 6:
            error = "Completa todos los campos. La contraseña debe tener al menos 6 caracteres."
        elif User.objects.filter(email=email).exists():
            error = "Ya existe una cuenta con ese email. Inicia sesión para vincular tu perfil."
        else:
            username = email.split("@")[0]
            base = username
            n = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{n}"
                n += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
            )
            UserProfile.objects.create(user=user, plan="free")
            temp.claimed_by = user
            temp.save(update_fields=["claimed_by"])
            login(request, user)
            return redirect('dashboard')

    return render(request, "practitioners/acceso.html", {
        "temp": temp,
        "facilitador": temp.created_by,
        "already_claimed": False,
        "error": error,
    })


@login_required
@require_POST
def perfil_archivar(request, pk):
    if not _is_practicante(request.user):
        return HttpResponseForbidden("Esta función requiere el plan Practicante o Empresa.")
    profile = get_object_or_404(TemporaryProfile, pk=pk, created_by=request.user)
    profile.active = False
    profile.save(update_fields=["active"])
    return redirect("practitioners:lista")
