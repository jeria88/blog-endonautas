import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import BlogSubmission


def _check_token(request):
    expected = getattr(settings, 'BLOG_SUBMIT_TOKEN', '')
    if not expected:
        return False
    auth = request.headers.get('Authorization', '')
    return auth == f'Bearer {expected}'


@csrf_exempt
@require_POST
def submit_api(request):
    """
    Recibe postulaciones desde mirrorwork.
    Authorization: Bearer <BLOG_SUBMIT_TOKEN>
    Body JSON: { title, body, author_email, author_name, source_type, source_description }
    """
    if not _check_token(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    title        = data.get('title', '').strip()
    body         = data.get('body', '').strip()
    author_email = data.get('author_email', '').strip()

    if not title or not body or not author_email:
        return JsonResponse({'error': 'title, body y author_email son obligatorios'}, status=400)

    source_type = data.get('source_type', BlogSubmission.SOURCE_FREE)
    valid_types = [t for t, _ in BlogSubmission.SOURCE_CHOICES]
    if source_type not in valid_types:
        source_type = BlogSubmission.SOURCE_FREE

    sub = BlogSubmission.objects.create(
        author_email       = author_email,
        author_name        = data.get('author_name', '').strip(),
        title              = title[:200],
        body               = body,
        source_type        = source_type,
        source_description = data.get('source_description', '').strip(),
        status             = BlogSubmission.STATUS_SUBMITTED,
    )
    return JsonResponse({'ok': True, 'id': sub.pk}, status=201)
