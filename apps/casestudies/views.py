import json
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.candidates.models import Candidate
from apps.core.services import call_claude
from apps.positions.models import Position

from apps.notifications.services import notify_company

from .forms import CaseStudyForm
from .models import CandidateCaseStudy, CaseStudy
from .prompts import GENERATE_CASE_STUDY_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

MAX_CV_TEXT_FOR_PROMPT = 10_000


def _send_casestudy_email(request, candidate, ccs):
    """Enviar email al candidato con el enlace al portal."""
    company = candidate.position.company
    portal_url = request.build_absolute_uri(
        f'/portal/case/{candidate.portal_token}/'
    )
    deadline_str = ccs.deadline.strftime('%d/%m/%Y a las %H:%M') if ccs.deadline else None

    html_content = render_to_string('emails/casestudy_sent.html', {
        'company_name': company.name,
        'candidate_name': candidate.first_name,
        'position_title': candidate.position.title,
        'casestudy_title': ccs.case_study.title,
        'deadline': deadline_str,
        'portal_url': portal_url,
    })

    try:
        send_mail(
            subject=f'Caso práctico — {candidate.position.title} — {company.name}',
            message=f'Hola {candidate.first_name}, tienes un caso práctico pendiente. Accede aquí: {portal_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Error enviando email de case study a %s", candidate.email)
        return False


@login_required
def casestudy_create(request, position_pk):
    """Crear case study para una posición."""
    position = get_object_or_404(Position, pk=position_pk, company=request.company)

    if request.method == 'POST':
        form = CaseStudyForm(request.POST)
        if form.is_valid():
            cs = form.save(commit=False)
            cs.position = position
            if request.POST.get('ai_generated') == 'true':
                cs.ai_generated = True
            cs.save()
            messages.success(request, f'Case study "{cs.title}" creado correctamente.')
            return redirect('positions:position_detail', pk=position.pk)
    else:
        form = CaseStudyForm()

    return render(request, 'casestudies/casestudy_form.html', {
        'form': form,
        'position': position,
        'title': 'Nuevo Case Study',
    })


@login_required
def casestudy_generate(request, candidate_pk):
    """Generar caso práctico con IA para un candidato."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk, position__company=request.company)
    position = candidate.position

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        full_content = request.POST.get('full_content', '').strip()
        evaluation_criteria = request.POST.get('evaluation_criteria', '').strip()
        deadline_days = int(request.POST.get('deadline_days', 7))

        if not title or not full_content:
            messages.error(request, 'El caso práctico debe tener título y contenido.')
            return redirect('casestudies:casestudy_generate', candidate_pk=candidate.pk)

        cs = CaseStudy.objects.create(
            position=position,
            title=title,
            brief_description=f'Caso práctico generado con IA para {candidate.full_name}',
            full_content=full_content,
            evaluation_criteria=evaluation_criteria,
            ai_generated=True,
            deadline_days=deadline_days,
        )

        ccs = CandidateCaseStudy.objects.create(
            candidate=candidate,
            case_study=cs,
            sent_at=timezone.now(),
            deadline=timezone.now() + timedelta(days=deadline_days),
        )

        candidate.status = 'case_sent'
        candidate.save(update_fields=['status', 'updated_at'])
        notify_company(
            company=position.company,
            title='Caso práctico enviado',
            message=f'"{cs.title}" enviado a {candidate.full_name}.',
            link=f'/candidates/{candidate.pk}/',
            notification_type='case_study',
            exclude_user=request.user,
        )

        # Send email
        if candidate.email:
            sent = _send_casestudy_email(request, candidate, ccs)
            if sent:
                messages.success(request, f'Caso práctico creado y enviado por email a {candidate.email}.')
            else:
                messages.warning(request, 'Caso práctico creado, pero hubo un error al enviar el email. Puedes reenviarlo.')
        else:
            messages.success(request, 'Caso práctico creado. El candidato no tiene email, no se pudo enviar.')

        return redirect('candidates:candidate_detail', pk=candidate.pk)

    return render(request, 'casestudies/casestudy_generate.html', {
        'candidate': candidate,
        'position': position,
        'title': f'Caso práctico para {candidate.full_name}',
    })


@login_required
def casestudy_edit(request, ccs_pk):
    """Editar un caso práctico asignado a un candidato."""
    ccs = get_object_or_404(
        CandidateCaseStudy.objects.select_related('case_study', 'candidate', 'candidate__position'),
        pk=ccs_pk,
        candidate__position__company=request.company,
    )
    cs = ccs.case_study
    candidate = ccs.candidate

    if request.method == 'POST':
        cs.title = request.POST.get('title', cs.title).strip()
        cs.full_content = request.POST.get('full_content', cs.full_content).strip()
        cs.evaluation_criteria = request.POST.get('evaluation_criteria', cs.evaluation_criteria).strip()
        cs.deadline_days = int(request.POST.get('deadline_days', cs.deadline_days))
        cs.save()

        messages.success(request, 'Caso práctico actualizado.')
        return redirect('candidates:candidate_detail', pk=candidate.pk)

    return render(request, 'casestudies/casestudy_edit.html', {
        'ccs': ccs,
        'case_study': cs,
        'candidate': candidate,
        'position': candidate.position,
        'title': f'Editar: {cs.title}',
    })


@login_required
def casestudy_resend(request, ccs_pk):
    """Reenviar email del caso práctico al candidato."""
    ccs = get_object_or_404(
        CandidateCaseStudy.objects.select_related('case_study', 'candidate', 'candidate__position'),
        pk=ccs_pk,
        candidate__position__company=request.company,
    )
    candidate = ccs.candidate

    if request.method == 'POST' and candidate.email:
        sent = _send_casestudy_email(request, candidate, ccs)
        if sent:
            messages.success(request, f'Email reenviado a {candidate.email}.')
        else:
            messages.error(request, 'Error al enviar el email.')

    return redirect('candidates:candidate_detail', pk=candidate.pk)


@login_required
def casestudy_detail(request, ccs_pk):
    """Ver el caso práctico completo + subir respuesta manualmente."""
    ccs = get_object_or_404(
        CandidateCaseStudy.objects.select_related('case_study', 'candidate', 'candidate__position'),
        pk=ccs_pk,
        candidate__position__company=request.company,
    )

    if request.method == 'POST':
        submission_text = request.POST.get('submission_text', '').strip()
        submission_file = request.FILES.get('submission_file')

        if not submission_text and not submission_file:
            messages.error(request, 'Debes escribir una respuesta o adjuntar un archivo.')
            return redirect('casestudies:casestudy_detail', ccs_pk=ccs.pk)

        if submission_file:
            ccs.submission_file = submission_file
        if submission_text:
            ccs.submission_text = submission_text
        ccs.submission_notes = request.POST.get('submission_notes', '').strip()
        ccs.submitted_at = timezone.now()
        ccs.save()

        ccs.candidate.status = 'case_submitted'
        ccs.candidate.save(update_fields=['status', 'updated_at'])
        notify_company(
            company=ccs.candidate.position.company,
            title='Caso práctico entregado',
            message=f'{ccs.candidate.full_name} ha entregado "{ccs.case_study.title}".',
            link=f'/candidates/{ccs.candidate.pk}/',
            notification_type='case_study',
            exclude_user=request.user,
        )

        messages.success(request, f'Respuesta registrada para {ccs.candidate.full_name}.')
        return redirect('candidates:candidate_detail', pk=ccs.candidate.pk)

    return render(request, 'casestudies/casestudy_detail.html', {
        'ccs': ccs,
        'case_study': ccs.case_study,
        'candidate': ccs.candidate,
        'position': ccs.candidate.position,
        'title': ccs.case_study.title,
    })


@require_POST
@login_required
def casestudy_ai_generate(request, candidate_pk):
    """Endpoint AJAX: generar caso práctico con IA basado en candidato + posición."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk, position__company=request.company)
    position = candidate.position
    company = request.company

    cv_text = (candidate.cv_text_extracted or '')[:MAX_CV_TEXT_FOR_PROMPT]

    user_prompt = GENERATE_CASE_STUDY_PROMPT.format(
        position_title=position.title,
        position_department=position.department or 'No especificado',
        position_description=position.description or 'No disponible',
        position_requirements=position.requirements or 'No disponibles',
        company_name=company.name,
        company_description=company.description or 'No disponible',
        candidate_name=candidate.full_name,
        candidate_summary=candidate.ai_summary or 'No disponible',
        candidate_cv_text=cv_text or 'No disponible',
    )

    try:
        result = call_claude(SYSTEM_PROMPT, user_prompt, json_output=True)
        if isinstance(result, dict):
            return JsonResponse(result)
        return JsonResponse({
            'error': 'La IA no devolvió un formato válido. Inténtalo de nuevo.',
        }, status=500)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        logger.exception("Error llamando a Claude API para case study")
        return JsonResponse(
            {'error': 'Error al conectar con la IA. Inténtalo de nuevo.'},
            status=500,
        )


@login_required
def casestudy_send(request, candidate_pk):
    """Enviar case study existente a un candidato."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk, position__company=request.company)
    case_studies = CaseStudy.objects.filter(position=candidate.position)

    if request.method == 'POST':
        cs_id = request.POST.get('case_study')
        cs = get_object_or_404(CaseStudy, pk=cs_id, position=candidate.position)

        ccs, created = CandidateCaseStudy.objects.get_or_create(
            candidate=candidate,
            case_study=cs,
            defaults={
                'sent_at': timezone.now(),
                'deadline': timezone.now() + timedelta(days=cs.deadline_days),
            }
        )
        if created:
            candidate.status = 'case_sent'
            candidate.save(update_fields=['status'])
            notify_company(
                company=candidate.position.company,
                title='Caso práctico enviado',
                message=f'"{cs.title}" enviado a {candidate.full_name}.',
                link=f'/candidates/{candidate.pk}/',
                notification_type='case_study',
                exclude_user=request.user,
            )

            if candidate.email:
                _send_casestudy_email(request, candidate, ccs)

            messages.success(request, f'Case study enviado a {candidate.full_name}.')
        else:
            messages.info(request, 'Este case study ya fue enviado a este candidato.')

        return redirect('candidates:candidate_detail', pk=candidate.pk)

    return render(request, 'casestudies/casestudy_send.html', {
        'candidate': candidate,
        'case_studies': case_studies,
        'title': 'Enviar Case Study',
    })
