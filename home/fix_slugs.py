"""
Fix slugs for new pages.
Run once: visit /fix-slugs/?key=fix-slugs-once-2026
Then DELETE this file and remove URL from urls.py.
"""
from django.http import HttpResponse
from home.models import HacksPage, ViajePage


def fix_slugs_view(request):
    """Fix slugs for Hacks and Viaje pages."""
    secret = request.GET.get('key', '')
    if secret != 'fix-slugs-once-2026':
        return HttpResponse('Unauthorized', status=403)

    lines = []

    # Fix Hacks page slug
    hacks = HacksPage.objects.first()
    if hacks:
        old_slug = hacks.slug
        hacks.slug = 'hacks'
        hacks.save()
        lines.append(f"Hacks slug: '{old_slug}' → 'hacks'")
        lines.append(f"Hacks URL: {hacks.url}")
    else:
        lines.append("ERROR: Hacks page not found")

    # Fix Viaje page slug
    viaje = ViajePage.objects.first()
    if viaje:
        old_slug = viaje.slug
        viaje.slug = 'viaje'
        viaje.save()
        lines.append(f"Viaje slug: '{old_slug}' → 'viaje'")
        lines.append(f"Viaje URL: {viaje.url}")
    else:
        lines.append("ERROR: Viaje page not found")

    # Fix Mascara page slug (remove accent if present)
    from home.models import MascaraPage
    mascara = MascaraPage.objects.first()
    if mascara:
        if mascara.slug != 'mascara':
            old_slug = mascara.slug
            mascara.slug = 'mascara'
            mascara.save()
            lines.append(f"Mascara slug: '{old_slug}' → 'mascara'")
        else:
            lines.append(f"Mascara slug OK: {mascara.slug}")

    lines.append("\nDONE.")
    return HttpResponse("\n".join(lines), content_type="text/plain")
