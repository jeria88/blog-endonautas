import json
import logging
import os
import threading

logger = logging.getLogger(__name__)

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .evaluator import evaluate_test
from .models import Question, Test, TestResult


def _generate_ai_insight(test_name, instrument_type, evaluation):
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return ""
    tipo_label = {
        "clinical": "instrumento clínico validado",
        "adapted":  "adaptación orientativa",
        "custom":   "herramienta de reflexión endonauta",
    }.get(instrument_type, "herramienta")
    ev_texto = json.dumps(evaluation, ensure_ascii=False, indent=2)
    prompt = (
        f'Eres el Espejo Endonauta. El usuario acaba de completar "{test_name}" '
        f'({tipo_label}).\n\nResultados:\n{ev_texto}\n\n'
        "Escribe una lectura endonauta de 3-4 párrafos: sin diagnosticar, "
        "devolviendo la conciencia al interior del usuario, terminando con una "
        "pregunta de exploración. Tono cálido, curioso, empoderador. En español."
    )
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.75,
                "max_tokens": 600,
            },
            timeout=25,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning("_generate_ai_insight failed: %s", e)
        return ""


def _run_insight_thread(result_pk, user_pk, test_name, instrument_type, evaluation):
    from django.contrib.auth import get_user_model
    from tokens.service import spend
    insight = _generate_ai_insight(test_name, instrument_type, evaluation)
    if insight:
        User = get_user_model()
        try:
            spend(User.objects.get(pk=user_pk), 'ai_insight')
        except Exception as e:
            logger.warning("insight spend failed for user %s: %s", user_pk, e)
        TestResult.objects.filter(pk=result_pk).update(ai_insight=insight)
    else:
        TestResult.objects.filter(pk=result_pk).update(ai_insight="—")


@login_required
def test_list(request):
    tests = Test.objects.filter(active=True)
    by_dimension = {}
    for test in tests:
        key = (test.dimension, test.get_dimension_display())
        by_dimension.setdefault(key, []).append(test)
    completed_ids = set(
        TestResult.objects.filter(user=request.user).values_list("test_id", flat=True)
    )
    return render(request, "psychometrics/test_list.html", {
        "by_dimension": by_dimension,
        "completed_ids": completed_ids,
    })


@login_required
def test_take(request, slug):
    test = get_object_or_404(Test, slug=slug, active=True)
    questions = test.questions.all()
    return render(request, "psychometrics/test_take.html", {
        "test": test,
        "questions": questions,
    })


@login_required
def test_submit(request, slug):
    if request.method != "POST":
        return redirect("psychometrics:test_take", slug=slug)

    test = get_object_or_404(Test, slug=slug, active=True)
    questions = test.questions.all()

    raw_scores = {}
    for q in questions:
        val = request.POST.get(f"q_{q.id}")
        if val is None:
            continue
        try:
            score = int(val)
        except ValueError:
            continue

        if q.reverse_scored:
            if q.scale in ("likert5", "likert5a"):
                score = 6 - score
            elif q.scale == "likert4":
                score = 4 - score
            elif q.scale == "likert3":
                score = 3 - score
            elif q.scale == "likert7":
                score = 8 - score
            elif q.scale == "binary":
                score = 1 - score

        dim_key = q.dimension_key or test.dimension
        raw_scores[dim_key] = raw_scores.get(dim_key, 0) + score

    evaluation = evaluate_test(test.name, raw_scores)

    result = TestResult.objects.create(
        user=request.user,
        test=test,
        raw_scores=raw_scores,
        evaluation=evaluation,
        ai_insight="",
    )

    return redirect("psychometrics:test_result", pk=result.pk)


@login_required
def test_result(request, pk):
    result = get_object_or_404(TestResult, pk=pk, user=request.user)
    return render(request, "psychometrics/test_result.html", {"result": result})


@login_required
def my_results(request):
    results = TestResult.objects.filter(user=request.user).select_related("test")
    return render(request, "psychometrics/my_results.html", {"results": results})


@login_required
def result_status(request, pk):
    result = get_object_or_404(TestResult, pk=pk, user=request.user)
    if result.ai_insight in ("", "processing"):
        return JsonResponse({"status": "processing"})
    insight = "" if result.ai_insight == "—" else result.ai_insight
    return JsonResponse({"status": "complete", "insight": insight})


@login_required
def insight_view(request, pk):
    result = get_object_or_404(TestResult, pk=pk, user=request.user)
    return render(request, "psychometrics/insight_view.html", {"result": result})


@login_required
def insight_reveal(request, pk):
    if request.method != "POST":
        return redirect("psychometrics:insight_view", pk=pk)
    result = get_object_or_404(TestResult, pk=pk, user=request.user)

    if result.ai_insight and result.ai_insight not in ("", "—"):
        return redirect("psychometrics:insight_view", pk=pk)

    from tokens.service import has_balance
    if not has_balance(request.user, 'ai_insight'):
        from django.contrib import messages
        messages.error(request, "Fractones insuficientes para generar el insight.")
        return redirect("psychometrics:insight_view", pk=pk)

    TestResult.objects.filter(pk=pk).update(ai_insight="processing")
    threading.Thread(
        target=_run_insight_thread,
        args=(result.pk, request.user.pk, result.test.name, result.test.instrument_type, result.evaluation),
        daemon=True,
    ).start()
    return redirect("psychometrics:insight_view", pk=pk)
