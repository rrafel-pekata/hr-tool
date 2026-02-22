from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.candidates.models import Candidate

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
            form.save()
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
