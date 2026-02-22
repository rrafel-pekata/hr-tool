from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.candidates.models import Candidate
from apps.notifications.services import notify_company

from .forms import InterviewForm, InterviewNotesForm
from .models import Interview


@login_required
def interview_create(request, candidate_pk):
    """Programar nueva entrevista para un candidato."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk, position__company=request.company)

    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.candidate = candidate
            interview.save()
            notify_company(
                company=candidate.position.company,
                title='Entrevista programada',
                message=f'{candidate.full_name} — {interview.scheduled_at.strftime("%d/%m/%Y %H:%M")}.',
                link=f'/candidates/{candidate.pk}/',
                notification_type='interview',
                exclude_user=request.user,
            )
            messages.success(request, 'Entrevista programada correctamente.')
            return redirect('candidates:candidate_detail', pk=candidate.pk)
    else:
        form = InterviewForm()
        # Filtrar entrevistadores a usuarios de la misma empresa
        form.fields['interviewer'].queryset = form.fields['interviewer'].queryset.filter(
            profile__company=request.company
        )

    return render(request, 'interviews/interview_form.html', {
        'form': form,
        'candidate': candidate,
        'title': 'Programar entrevista',
    })


@login_required
def interview_edit(request, pk):
    """Editar entrevista / añadir notas."""
    interview = get_object_or_404(
        Interview.objects.select_related('candidate', 'candidate__position'),
        pk=pk,
        candidate__position__company=request.company,
    )

    if request.method == 'POST':
        form = InterviewNotesForm(request.POST, instance=interview)
        if form.is_valid():
            old_status = Interview.objects.filter(pk=interview.pk).values_list('status', flat=True).first()
            form.save()
            candidate = interview.candidate
            company = candidate.position.company
            if interview.status != old_status and interview.status == Interview.Status.COMPLETED:
                notify_company(
                    company=company,
                    title='Entrevista completada',
                    message=f'Entrevista con {candidate.full_name} realizada. Puntuación: {interview.overall_score or "—"}/10.',
                    link=f'/candidates/{candidate.pk}/',
                    notification_type='interview',
                    exclude_user=request.user,
                )
            elif interview.status != old_status and interview.status in (Interview.Status.CANCELLED, Interview.Status.NO_SHOW):
                notify_company(
                    company=company,
                    title=f'Entrevista {interview.get_status_display().lower()}',
                    message=f'Entrevista con {candidate.full_name} — {interview.get_status_display()}.',
                    link=f'/candidates/{candidate.pk}/',
                    notification_type='interview',
                    exclude_user=request.user,
                )
            messages.success(request, 'Entrevista actualizada correctamente.')
            return redirect('candidates:candidate_detail', pk=interview.candidate.pk)
    else:
        form = InterviewNotesForm(instance=interview)

    return render(request, 'interviews/interview_edit.html', {
        'form': form,
        'interview': interview,
        'candidate': interview.candidate,
        'title': f'Entrevista: {interview.candidate.full_name}',
    })
