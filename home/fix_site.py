"""
Temporary endpoint to fix Wagtail Site config.
DELETE AFTER USE: remove from urls.py after running once.
"""
from django.http import HttpResponse
from wagtail.models import Site, Page


def fix_wagtail_site_view(request):
    """One-time fix: create/update Wagtail Site so pages have URLs."""
    # Security: only allow with secret key
    secret = request.GET.get('key', '')
    if secret != 'fix-site-once-2026':
        return HttpResponse('Unauthorized', status=403)

    lines = []

    # Find home page
    home = Page.objects.filter(depth=2).first()
    if not home:
        return HttpResponse('ERROR: No home page found (depth=2)', status=500)

    lines.append(f"Home page: '{home.title}' (id={home.id}, slug={home.slug})")

    # Check/create site
    site = Site.objects.filter(is_default_site=True).first()

    if site:
        old_root = str(site.root_page)
        site.root_page = home
        site.hostname = "endonautas.cl"
        site.port = 443
        site.site_name = "Endonautas"
        site.save()
        lines.append(f"Site UPDATED: hostname={site.hostname}, root: {old_root} → '{home.title}'")
    else:
        site = Site.objects.create(
            hostname="endonautas.cl",
            port=443,
            root_page=home,
            site_name="Endonautas",
            is_default_site=True,
        )
        lines.append(f"Site CREATED: hostname={site.hostname}, root='{home.title}'")

    # Verify children
    children = home.get_children().live()
    lines.append(f"\nChild pages of '{home.title}':")
    for child in children:
        lines.append(f"  - {child.title}: {child.url}")

    lines.append("\nDONE. Pages should now have URLs.")
    return HttpResponse("\n".join(lines), content_type="text/plain")
