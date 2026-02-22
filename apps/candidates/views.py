import io
import json
import logging

import pypdfium2 as pdfium
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.services import call_claude, extract_pdf_text
from apps.positions.models import Position

from .forms import CandidateCreateForm, CandidateEditForm
from .models import Candidate
from .prompts import CV_ANALYSIS_SYSTEM_PROMPT, CV_ANALYSIS_USER_PROMPT

logger = logging.getLogger(__name__)

MAX_CV_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_CV_TEXT_LENGTH = 15_000


@require_POST
@login_required
def analyze_cv(request, position_pk):
    """Endpoint AJAX: analizar CV con IA y devolver datos extraídos."""
    position = get_object_or_404(Position, pk=position_pk, company=request.company)

    cv_file = request.FILES.get('cv_file')
    if not cv_file:
        return JsonResponse({'error': 'No se ha enviado ningún archivo.'}, status=400)

    if not cv_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Solo se permiten archivos PDF.'}, status=400)

    if cv_file.size > MAX_CV_SIZE:
        return JsonResponse({'error': 'El archivo excede el tamaño máximo de 10MB.'}, status=400)

    try:
        cv_text = extract_pdf_text(cv_file)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    cv_text_truncated = cv_text[:MAX_CV_TEXT_LENGTH]

    user_prompt = CV_ANALYSIS_USER_PROMPT.format(
        cv_text=cv_text_truncated,
        position_title=position.title,
        position_department=position.department or 'No especificado',
        position_location=position.location or 'No especificada',
        position_description=position.description or 'No disponible',
        position_requirements=position.requirements or 'No disponibles',
    )

    try:
        result = call_claude(CV_ANALYSIS_SYSTEM_PROMPT, user_prompt, json_output=True)

        if isinstance(result, dict):
            result['cv_text_extracted'] = cv_text
            return JsonResponse(result)

        return JsonResponse({
            'error': 'La IA no devolvió un formato válido. Inténtalo de nuevo.',
        }, status=500)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        logger.exception("Error llamando a Claude API para análisis de CV")
        return JsonResponse(
            {'error': 'Error al conectar con la IA. Inténtalo de nuevo.'},
            status=500,
        )


@login_required
def candidate_create(request, position_pk):
    """Crear candidato para una posición."""
    position = get_object_or_404(Position, pk=position_pk, company=request.company)

    if request.method == 'POST':
        form = CandidateCreateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.position = position
            candidate.cv_text_extracted = request.POST.get('cv_text_extracted', '')
            candidate.ai_summary = request.POST.get('ai_summary', '')
            # Parse strengths/weaknesses from hidden fields
            try:
                candidate.ai_strengths = json.loads(request.POST.get('ai_strengths', '[]'))
            except (json.JSONDecodeError, TypeError):
                candidate.ai_strengths = []
            try:
                candidate.ai_weaknesses = json.loads(request.POST.get('ai_weaknesses', '[]'))
            except (json.JSONDecodeError, TypeError):
                candidate.ai_weaknesses = []
            try:
                candidate.ai_fit_score = int(request.POST.get('ai_fit_score', 0)) or None
            except (ValueError, TypeError):
                candidate.ai_fit_score = None
            candidate.save()
            messages.success(request, f'Candidato {candidate.full_name} añadido correctamente.')
            return redirect('candidates:candidate_detail', pk=candidate.pk)
    else:
        form = CandidateCreateForm()

    return render(request, 'candidates/candidate_form.html', {
        'form': form,
        'position': position,
        'title': 'Nuevo candidato',
    })


@login_required
def candidate_edit(request, pk):
    """Editar datos del candidato."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)

    if request.method == 'POST':
        form = CandidateEditForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidato actualizado correctamente.')
            return redirect('candidates:candidate_detail', pk=candidate.pk)
    else:
        form = CandidateEditForm(instance=candidate)

    return render(request, 'candidates/candidate_edit.html', {
        'form': form,
        'candidate': candidate,
        'title': f'Editar: {candidate.full_name}',
    })


@login_required
def candidate_detail(request, pk):
    """Vista detalle del candidato — pantalla clave del sistema."""
    candidate = get_object_or_404(
        Candidate.objects.select_related('position', 'position__company'),
        pk=pk,
        position__company=request.company,
    )

    interviews = candidate.interviews.select_related('interviewer').order_by('-scheduled_at')
    case_studies = candidate.case_studies.select_related('case_study').order_by('-created_at')
    evaluations = candidate.evaluations.order_by('-generated_at')

    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate,
        'position': candidate.position,
        'interviews': interviews,
        'case_studies': case_studies,
        'evaluations': evaluations,
        'status_choices': Candidate.Status.choices,
    })


@login_required
def candidate_status(request, pk):
    """Cambiar estado del candidato (pipeline)."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Candidate.Status.choices):
            candidate.status = new_status
            candidate.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Estado actualizado a "{candidate.get_status_display()}".')

            # Cerrar la posición automáticamente al contratar
            if new_status == Candidate.Status.HIRED:
                position = candidate.position
                if position.status != Position.Status.CLOSED:
                    from django.utils import timezone
                    position.status = Position.Status.CLOSED
                    position.closed_at = timezone.now()
                    position.save(update_fields=['status', 'closed_at', 'updated_at'])
                    messages.info(request, f'La posición "{position.title}" se ha cerrado automáticamente.')
    return redirect('candidates:candidate_detail', pk=candidate.pk)


@login_required
def candidate_notes(request, pk):
    """Guardar notas rápidas del reclutador (AJAX-friendly)."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)
    if request.method == 'POST':
        candidate.recruiter_notes = request.POST.get('recruiter_notes', '')
        candidate.save(update_fields=['recruiter_notes', 'updated_at'])
        messages.success(request, 'Notas guardadas.')
    return redirect('candidates:candidate_detail', pk=candidate.pk)


@login_required
def candidate_rating(request, pk):
    """Guardar valoración manual."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            if 1 <= rating <= 5:
                candidate.rating = rating
                candidate.save(update_fields=['rating', 'updated_at'])
                messages.success(request, f'Valoración actualizada: {rating}/5.')
        except (ValueError, TypeError):
            pass
    return redirect('candidates:candidate_detail', pk=candidate.pk)


@login_required
def candidate_cv_preview(request, pk):
    """Genera una imagen PNG de la primera página del CV."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)

    if not candidate.cv_file:
        return HttpResponse(status=404)

    try:
        candidate.cv_file.seek(0)
        pdf_bytes = candidate.cv_file.read()
        pdf = pdfium.PdfDocument(pdf_bytes)
        page = pdf[0]
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()
        pdf.close()

        buf = io.BytesIO()
        pil_image.save(buf, format='PNG', optimize=True)
        buf.seek(0)

        response = HttpResponse(buf.getvalue(), content_type='image/png')
        response['Cache-Control'] = 'private, max-age=3600'
        return response
    except Exception:
        logger.exception("Error generando preview del CV")
        return HttpResponse(status=500)


@require_POST
@login_required
def candidate_upload_cv(request, pk):
    """Subir CV a un candidato existente y analizarlo con IA."""
    candidate = get_object_or_404(Candidate, pk=pk, position__company=request.company)
    position = candidate.position

    cv_file = request.FILES.get('cv_file')
    if not cv_file:
        return JsonResponse({'error': 'No se ha enviado ningún archivo.'}, status=400)

    if not cv_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Solo se permiten archivos PDF.'}, status=400)

    if cv_file.size > MAX_CV_SIZE:
        return JsonResponse({'error': 'El archivo excede el tamaño máximo de 10MB.'}, status=400)

    # Save the file to the candidate
    candidate.cv_file.save(cv_file.name, cv_file, save=True)

    # Extract text from PDF
    try:
        candidate.cv_file.seek(0)
        cv_text = extract_pdf_text(candidate.cv_file)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    candidate.cv_text_extracted = cv_text
    candidate.save(update_fields=['cv_text_extracted', 'updated_at'])

    cv_text_truncated = cv_text[:MAX_CV_TEXT_LENGTH]

    # Call Claude for AI analysis
    user_prompt = CV_ANALYSIS_USER_PROMPT.format(
        cv_text=cv_text_truncated,
        position_title=position.title,
        position_department=position.department or 'No especificado',
        position_location=position.location or 'No especificada',
        position_description=position.description or 'No disponible',
        position_requirements=position.requirements or 'No disponibles',
    )

    try:
        result = call_claude(CV_ANALYSIS_SYSTEM_PROMPT, user_prompt, json_output=True)

        if isinstance(result, dict):
            strengths = result.get('strengths', [])
            weaknesses = result.get('weaknesses', [])
            fit_score = int(result.get('fit_score', 0)) if result.get('fit_score') else None

            candidate.ai_summary = result.get('summary', '')
            candidate.ai_strengths = strengths if isinstance(strengths, list) else []
            candidate.ai_weaknesses = weaknesses if isinstance(weaknesses, list) else []
            candidate.ai_fit_score = fit_score
            candidate.save(update_fields=[
                'ai_summary', 'ai_strengths', 'ai_weaknesses', 'ai_fit_score', 'updated_at',
            ])

            return JsonResponse({
                'success': True,
                'summary': result.get('summary', ''),
                'strengths': candidate.ai_strengths,
                'weaknesses': candidate.ai_weaknesses,
                'fit_score': fit_score or 0,
                'cv_url': candidate.cv_file.url,
            })

        return JsonResponse({
            'success': True,
            'summary': '',
            'strengths': [],
            'weaknesses': [],
            'fit_score': 0,
            'cv_url': candidate.cv_file.url,
        })

    except Exception:
        logger.exception("Error llamando a Claude API para análisis de CV")
        # CV was saved even if AI fails
        return JsonResponse({
            'success': True,
            'ai_error': 'CV subido correctamente, pero hubo un error al analizar con IA.',
            'cv_url': candidate.cv_file.url,
        })
