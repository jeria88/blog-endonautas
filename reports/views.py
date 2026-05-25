from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from psychometrics.models import TestResult
from mirror.models import ConflictSession


@login_required
def dashboard(request):
    results = TestResult.objects.filter(user=request.user).select_related("test")
    mirror_sessions = ConflictSession.objects.filter(
        user=request.user
    ).exclude(status="archived").count()

    by_dimension = {}
    for r in results:
        dim = r.test.get_dimension_display()
        by_dimension.setdefault(dim, []).append(r)

    dimension_summary = [
        {"nombre": dim, "total": len(rs), "ultimo": rs[0].completed_at}
        for dim, rs in sorted(by_dimension.items(), key=lambda x: -len(x[1]))
    ]

    return render(request, "reports/dashboard.html", {
        "total_tests": results.count(),
        "mirror_sessions": mirror_sessions,
        "dimension_summary": dimension_summary,
        "recent_results": results[:5],
    })
