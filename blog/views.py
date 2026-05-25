from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django import forms

from .models import BlogSubmission


@login_required
def submission_picker(request):
    """Muestra todo el contenido del usuario para que elija de dónde postular."""
    from mirror.models import ConflictSession
    from psychometrics.models import TestResult
    from birth.models import BirthReport

    context = {
        'espejo_sessions': ConflictSession.objects.filter(
            user=request.user, status='completed'
        ).order_by('-updated_at'),
        'test_results': TestResult.objects.filter(
            user=request.user
        ).select_related('test').order_by('-completed_at'),
        'birth_reports': BirthReport.objects.filter(
            user=request.user, status='complete'
        ).order_by('-created_at'),
    }
    return render(request, 'blog/submission_picker.html', context)


class SubmissionForm(forms.Form):
    title = forms.CharField(
        label='Título',
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Dale un nombre a tu texto…'}),
    )
    body = forms.CharField(
        label='Tu texto',
        widget=forms.Textarea(attrs={
            'rows': 18,
            'placeholder': 'Escribe libremente. Puedes editar el contenido antes de enviarlo.',
        }),
    )


def _prefill_from_source(source_type, source_id, user):
    """Returns (title, body, espejo_session, test_result, birth_report) or raises 404."""
    from django.shortcuts import get_object_or_404

    espejo_session = test_result = birth_report = None
    title = body = ''

    if source_type == BlogSubmission.SOURCE_ESPEJO and source_id:
        from mirror.models import ConflictSession
        s = get_object_or_404(ConflictSession, pk=source_id, user=user)
        espejo_session = s
        title = s.title or s.conflict_description[:80]
        parts = [s.conflict_description]
        if s.pattern_revealed:
            parts.append(f'\n\nPatrón revelado:\n{s.pattern_revealed}')
        if s.pregunta_cierre:
            parts.append(f'\n\nPregunta de cierre:\n{s.pregunta_cierre}')
        body = ''.join(parts)

    elif source_type == BlogSubmission.SOURCE_TEST and source_id:
        from psychometrics.models import TestResult
        r = get_object_or_404(TestResult, pk=source_id, user=user)
        test_result = r
        title = f'Mi experiencia con {r.test.name}'
        body = r.ai_insight or ''

    elif source_type == BlogSubmission.SOURCE_BIRTH and source_id:
        from birth.models import BirthReport
        r = get_object_or_404(BirthReport, pk=source_id, user=user)
        birth_report = r
        title = f'Mi {r.get_report_type_display()}'
        body = r.interpretation or ''

    return title, body, espejo_session, test_result, birth_report


@login_required
def submission_list(request):
    submissions = BlogSubmission.objects.filter(user=request.user)
    return render(request, 'blog/submission_list.html', {'submissions': submissions})


@login_required
def submission_create(request, source_type='free', source_id=None):
    title, body, espejo_session, test_result, birth_report = _prefill_from_source(
        source_type, source_id, request.user
    )

    form = SubmissionForm(request.POST or None, initial={'title': title, 'body': body})

    if request.method == 'POST' and form.is_valid():
        status = (
            BlogSubmission.STATUS_SUBMITTED
            if 'enviar' in request.POST
            else BlogSubmission.STATUS_DRAFT
        )
        BlogSubmission.objects.create(
            user=request.user,
            title=form.cleaned_data['title'],
            body=form.cleaned_data['body'],
            source_type=source_type,
            espejo_session=espejo_session,
            test_result=test_result,
            birth_report=birth_report,
            status=status,
        )
        return redirect('submission_list')

    return render(request, 'blog/submission_edit.html', {
        'form': form,
        'source_type': source_type,
        'is_new': True,
    })


@login_required
def submission_edit(request, pk):
    sub = get_object_or_404(BlogSubmission, pk=pk, user=request.user)

    if not sub.is_editable:
        return redirect('submission_list')

    form = SubmissionForm(request.POST or None, initial={'title': sub.title, 'body': sub.body})

    if request.method == 'POST' and form.is_valid():
        sub.title = form.cleaned_data['title']
        sub.body  = form.cleaned_data['body']
        sub.status = (
            BlogSubmission.STATUS_SUBMITTED
            if 'enviar' in request.POST
            else BlogSubmission.STATUS_DRAFT
        )
        sub.save()
        return redirect('submission_list')

    return render(request, 'blog/submission_edit.html', {
        'form': form,
        'submission': sub,
        'is_new': False,
    })


@login_required
@require_POST
def submission_delete(request, pk):
    sub = get_object_or_404(BlogSubmission, pk=pk, user=request.user)
    if sub.status == BlogSubmission.STATUS_DRAFT:
        sub.delete()
    return redirect('submission_list')
