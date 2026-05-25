import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import TokenBalance, TokenTransaction

logger = logging.getLogger(__name__)


@login_required
def balance(request):
    balance_obj, _ = TokenBalance.objects.get_or_create(
        user=request.user, defaults={"balance": 0}
    )
    transactions = TokenTransaction.objects.filter(user=request.user)[:30]
    try:
        profile = request.user.profile
    except Exception:
        profile = None
    return render(request, "tokens/balance.html", {
        "balance": balance_obj,
        "transactions": transactions,
        "profile": profile,
    })


@login_required
def planes(request):
    try:
        profile = request.user.profile
    except Exception:
        profile = None
    return render(request, "tokens/planes.html", {
        "profile": profile,
        "hotmart_urls": settings.HOTMART_CHECKOUT_URLS,
    })


@csrf_exempt
@require_POST
def hotmart_webhook(request):
    # Verify webhook token (hottok query param OR X-Hotmart-Webhook-Token header)
    expected = settings.HOTMART_WEBHOOK_TOKEN
    if expected:
        received = (
            request.GET.get("hottok")
            or request.headers.get("X-Hotmart-Webhook-Token", "")
        )
        if received != expected:
            logger.warning("[Hotmart] webhook token mismatch")
            return HttpResponse("Unauthorized", status=401)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Bad JSON", status=400)

    from tokens.hotmart import process_webhook
    ok, msg = process_webhook(payload)

    logger.info(f"[Hotmart] webhook processed: {msg}")
    return JsonResponse({"ok": ok, "msg": msg}, status=200 if ok else 422)
