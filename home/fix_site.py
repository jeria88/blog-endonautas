"""
Fix Mascara page slug and remove temp endpoints.
Run once: visit /fix-site/?key=fix-site-once-2026
Then REMOVE fix_site.py and the /fix-site/ URL from urls.py
"""
from django.http import HttpResponse
from wagtail.models import Site, Page


def fix_wagtail_site_view(request):
    """Fix Wagtail Site config and clean up page slugs."""
    secret = request.GET.get('key', '')
    if secret != 'fix-site-once-2026':
        return HttpResponse('Unauthorized', status=403)

    lines = []

    # 1. Fix Mascara page slug (remove accent)
    mascara_page = Page.objects.filter(title='Máscara').first()
    if mascara_page:
        old_slug = mascara_page.slug
        mascara_page.slug = 'mascara'
        mascara_page.save()
        lines.append(f"Mascara slug fixed: '{old_slug}' → 'mascara'")
    else:
        lines.append("WARNING: Mascara page not found")

    # 2. Verify site
    site = Site.objects.filter(is_default_site=True).first()
    if site:
        lines.append(f"Site OK: {site.hostname}, root={site.root_page.title}")
    else:
        lines.append("WARNING: No default site found")

    # 3. List all child pages with URLs
    home = Page.objects.filter(depth=2).first()
    if home:
        children = home.get_children()
        lines.append(f"\nAll child pages of '{home.title}':")
        for child in children:
            lines.append(f"  - {child.title}: slug='{child.slug}' url='{child.url}' live={child.live}")

    lines.append("\nDONE.")
    return HttpResponse("\n".join(lines), content_type="text/plain")
