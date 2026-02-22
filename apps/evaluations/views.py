import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.candidates.models import Candidate
from apps.core.services import call_claude
from apps.notifications.services import notify_company

from .models import AIEvaluation
from .prompts import EVALUATION_SYSTEM_PROMPT, EVALUATION_USER_PROMPT

logger = logging.getLogger(__name__)

MAX_CV_TEXT = 8_000
MAX_SUBMISSION_TEXT = 5_000


def _build_interviews_text(candidate):
    """Compilar info de entrevistas en texto para el prompt."""
    interviews = candidate.interviews.select_related('interviewer').order_by('scheduled_at')
    if not interviews.exists():
        return "No se han realizado entrevistas."

    parts = []
    for i, interview in enumerate(interviews, 1):
        interviewer = interview.interviewer.get_full_name() if interview.interviewer else 'No asignado'
        lines = [
            f"Entrevista {i}:",
            f"  - Fecha: {interview.scheduled_at.strftime('%d/%m/%Y')}",
            f"  - Entrevistador: {interviewer}",
            f"  - Estado: {interview.get_status_display()}",
        ]
        if interview.overall_score:
            lines.append(f"  - Puntuación: {interview.overall_score}/10")
        if interview.notes:
            lines.append(f"  - Notas: {interview.notes[:2000]}")
        if interview.strengths:
            lines.append(f"  - Puntos fuertes: {interview.strengths[:500]}")
        if interview.weaknesses:
            lines.append(f"  - Puntos débiles: {interview.weaknesses[:500]}")
        parts.append('\n'.join(lines))

    return '\n\n'.join(parts)


def _build_casestudies_text(candidate):
    """Compilar info de casos prácticos en texto para el prompt."""
    case_studies = candidate.case_studies.select_related('case_study').order_by('created_at')
    if not case_studies.exists():
        return "No se han asignado casos prácticos."

    parts = []
    for i, ccs in enumerate(case_studies, 1):
        cs = ccs.case_study
        lines = [
            f"Caso práctico {i}: {cs.title}",
            f"  - Enunciado: {cs.full_content[:2000]}",
        ]
        if ccs.submitted_at:
            lines.append(f"  - Entregado: {ccs.submitted_at.strftime('%d/%m/%Y')}")
            if ccs.submission_text:
                lines.append(f"  - Respuesta del candidato: {ccs.submission_text[:MAX_SUBMISSION_TEXT]}")
            if ccs.submission_notes:
                lines.append(f"  - Notas del candidato: {ccs.submission_notes[:500]}")
            if ccs.score:
                lines.append(f"  - Puntuación: {ccs.score}/10")
        else:
            lines.append("  - No entregado todavía.")

        if cs.evaluation_criteria:
            lines.append(f"  - Criterios de evaluación: {cs.evaluation_criteria[:1000]}")

        parts.append('\n'.join(lines))

    return '\n\n'.join(parts)


@login_required
def evaluate_candidate(request, candidate_pk):
    """Generar / ver evaluación IA de un candidato."""
    candidate = get_object_or_404(
        Candidate.objects.select_related('position', 'position__company'),
        pk=candidate_pk,
        position__company=request.company,
    )

    evaluations = candidate.evaluations.order_by('-generated_at')
    latest = evaluations.first()

    if request.method == 'POST':
        position = candidate.position
        company = request.company

        cv_text = (candidate.cv_text_extracted or '')[:MAX_CV_TEXT]
        interviews_text = _build_interviews_text(candidate)
        casestudies_text = _build_casestudies_text(candidate)

        user_prompt = EVALUATION_USER_PROMPT.format(
            position_title=position.title,
            position_department=position.department or 'No especificado',
            position_description=position.description or 'No disponible',
            position_requirements=position.requirements or 'No disponibles',
            company_name=company.name,
            candidate_name=candidate.full_name,
            candidate_summary=candidate.ai_summary or 'No disponible',
            candidate_cv_text=cv_text or 'No disponible',
            interviews_text=interviews_text,
            casestudies_text=casestudies_text,
            recruiter_notes=candidate.recruiter_notes or 'Sin notas.',
        )

        try:
            result = call_claude(EVALUATION_SYSTEM_PROMPT, user_prompt, json_output=True)

            if isinstance(result, dict):
                strengths = result.get('strengths', [])
                weaknesses = result.get('weaknesses', [])
                evaluation = AIEvaluation.objects.create(
                    candidate=candidate,
                    prompt_used=user_prompt,
                    result=str(result),
                    cv_score=result.get('cv_score'),
                    interview_score=result.get('interview_score'),
                    case_score=result.get('case_score'),
                    overall_score=result.get('overall_score'),
                    recommendation=result.get('recommendation', ''),
                    summary=result.get('summary', ''),
                    strengths=strengths if isinstance(strengths, list) else [],
                    weaknesses=weaknesses if isinstance(weaknesses, list) else [],
                )

                # Update candidate status
                candidate.status = 'evaluation'
                candidate.save(update_fields=['status', 'updated_at'])

                rec_labels = {'hire': 'Contratar', 'hold': 'En espera', 'reject': 'Rechazar'}
                rec = rec_labels.get(evaluation.recommendation, evaluation.recommendation)
                notify_company(
                    company=request.company,
                    title=f'Evaluación IA: {candidate.full_name}',
                    message=f'Puntuación: {evaluation.overall_score}/10 — Recomendación: {rec}.',
                    link=f'/evaluations/{candidate.pk}/',
                    notification_type='evaluation',
                    exclude_user=request.user,
                )

                messages.success(request, 'Evaluación IA generada correctamente.')
            else:
                messages.error(request, 'La IA no devolvió un formato válido. Inténtalo de nuevo.')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            logger.exception("Error llamando a Claude API para evaluación")
            messages.error(request, 'Error al conectar con la IA. Inténtalo de nuevo.')

        return redirect('evaluations:evaluate_candidate', candidate_pk=candidate.pk)

    return render(request, 'evaluations/evaluate.html', {
        'candidate': candidate,
        'latest_evaluation': latest,
        'evaluations': evaluations,
        'title': f'Evaluación IA: {candidate.full_name}',
    })
