import io
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.core.services import ALL_LANGUAGES, call_claude, translate_fields
from apps.core.tasks import translate_instance_fields
from apps.evaluations.models import AIEvaluation
from apps.notifications.services import notify_company
from apps.tenants.models import Department

from .forms import PositionForm
from .models import Position
from .prompts import GENERATE_POSITION_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@login_required
def position_list(request):
    """Listado de posiciones de la empresa activa."""
    if not request.company:
        return redirect('core:select_company')

    positions = Position.objects.filter(company=request.company).select_related(
        'department'
    ).annotate(
        num_candidates=Count('candidates')
    ).order_by('-created_at')

    # Filtro por estado
    status_filter = request.GET.get('status', '')
    if status_filter:
        positions = positions.filter(status=status_filter)

    # Filtro por departamento
    department_filter = request.GET.get('department', '')
    if department_filter:
        positions = positions.filter(department_id=department_filter)

    departments = request.company.departments.order_by('name')

    return render(request, 'positions/position_list.html', {
        'positions': positions,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'departments': departments,
        'status_choices': Position.Status.choices,
    })


@login_required
def position_create(request):
    """Crear nueva posición."""
    if not request.company:
        messages.error(request, _('Debes tener una empresa asignada para crear posiciones.'))
        return redirect('core:select_company')

    if request.method == 'POST':
        form = PositionForm(request.POST, company=request.company)
        if form.is_valid():
            position = form.save(commit=False)
            position.company = request.company
            position.save()
            translate_instance_fields.delay(
                'positions', 'Position', str(position.pk), get_language(),
                ['title', 'description', 'requirements', 'about_company_snippet', 'benefits', 'salary_range'],
            )
            messages.success(request, _('Posición "%(title)s" creada correctamente.') % {'title': position.title})
            return redirect('positions:position_detail', pk=position.pk)
    else:
        form = PositionForm(company=request.company)
    return render(request, 'positions/position_form.html', {
        'form': form,
        'title': _('Nueva posición'),
    })


@login_required
def position_edit(request, pk):
    """Editar posición existente."""
    position = get_object_or_404(Position, pk=pk, company=request.company)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position, company=request.company)
        if form.is_valid():
            form.save()
            translate_instance_fields.delay(
                'positions', 'Position', str(position.pk), get_language(),
                ['title', 'description', 'requirements', 'about_company_snippet', 'benefits', 'salary_range'],
            )
            messages.success(request, _('Posición actualizada correctamente.'))
            return redirect('positions:position_detail', pk=position.pk)
    else:
        form = PositionForm(instance=position, company=request.company)
    return render(request, 'positions/position_form.html', {
        'form': form,
        'position': position,
        'title': _('Editar: %(title)s') % {'title': position.title},
    })


@login_required
def position_detail(request, pk):
    """Vista detalle de posición: oferta + candidatos + case study."""
    position = get_object_or_404(
        Position.objects.annotate(num_candidates=Count('candidates')),
        pk=pk,
        company=request.company,
    )
    latest_eval = AIEvaluation.objects.filter(
        candidate=OuterRef('pk'),
    ).order_by('-generated_at')
    candidates = position.candidates.annotate(
        eval_score=Subquery(latest_eval.values('overall_score')[:1]),
        eval_recommendation=Subquery(latest_eval.values('recommendation')[:1]),
    ).order_by('-created_at')

    # Filtro candidatos por estado
    candidate_status = request.GET.get('candidate_status', '')
    if candidate_status:
        candidates = candidates.filter(status=candidate_status)

    case_studies = position.case_studies.all()

    translatable_fields = ['description', 'requirements', 'benefits', 'about_company_snippet']
    translations = {}
    for lang in ALL_LANGUAGES:
        translations[lang] = {
            field: getattr(position, f'{field}_{lang}', '') or ''
            for field in translatable_fields
        }

    return render(request, 'positions/position_detail.html', {
        'position': position,
        'candidates': candidates,
        'candidate_status': candidate_status,
        'case_studies': case_studies,
        'translations_json': json.dumps(translations, ensure_ascii=False),
    })


@login_required
def position_status(request, pk):
    """Cambiar estado de la posición (publish/pause/close)."""
    position = get_object_or_404(Position, pk=pk, company=request.company)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'publish':
            position.status = Position.Status.PUBLISHED
            position.published_at = timezone.now()
            messages.success(request, _('Posición publicada.'))
        elif action == 'pause':
            position.status = Position.Status.PAUSED
            messages.success(request, _('Posición pausada.'))
        elif action == 'close':
            position.status = Position.Status.CLOSED
            position.closed_at = timezone.now()
            messages.success(request, _('Posición cerrada.'))
        elif action == 'draft':
            position.status = Position.Status.DRAFT
            messages.success(request, _('Posición movida a borrador.'))
        position.save()
        if action in ('publish', 'close'):
            notify_company(
                company=request.company,
                title=f'Posición {position.get_status_display().lower()}',
                message=f'"{position.title}" — {position.get_status_display()}.',
                link=f'/positions/{position.pk}/',
                notification_type='position',
                exclude_user=request.user,
            )
    return redirect('positions:position_detail', pk=position.pk)


@require_POST
@login_required
def position_delete(request, pk):
    """Soft-delete de posición."""
    position = get_object_or_404(Position, pk=pk, company=request.company)
    position.soft_delete()
    messages.success(request, _('Posición "%(title)s" eliminada.') % {'title': position.title})
    return redirect('positions:position_list')


@require_POST
@login_required
def position_ai_generate(request):
    """Endpoint AJAX: mejorar oferta con IA."""
    if not request.company:
        return JsonResponse({'error': _('Sin empresa asignada.')}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': _('JSON inválido.')}, status=400)

    company = request.company
    # Resolve department name from ID (the select sends a UUID)
    department_value = data.get('department', '')
    department_name = ''
    if department_value:
        dept = Department.objects.filter(pk=department_value, company=company).first()
        if dept:
            department_name = dept.name

    user_prompt = GENERATE_POSITION_PROMPT.format(
        title=data.get('title', ''),
        department=department_name,
        location=data.get('location', ''),
        employment_type=data.get('employment_type', ''),
        salary_range=data.get('salary_range', ''),
        description=data.get('description', ''),
        requirements=data.get('requirements', ''),
        company_name=company.name,
        company_description=company.description or 'No disponible',
        company_website=company.website or 'No disponible',
        company_benefits=company.benefits or 'No especificados',
        company_work_schedule=company.work_schedule or 'No especificada',
        company_remote_policy=company.remote_policy or 'No especificada',
        company_office_location=company.office_location or 'No especificada',
        company_culture=company.culture or 'No especificada',
    )

    try:
        result = call_claude(SYSTEM_PROMPT, user_prompt, json_output=True)
        if isinstance(result, dict):
            return JsonResponse(result)
        return JsonResponse({
            'description': str(result),
            'requirements': '',
            'about_company_snippet': '',
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        logger.exception("Error llamando a Claude API")
        return JsonResponse(
            {'error': _('Error al conectar con la IA. Inténtalo de nuevo.')},
            status=500,
        )


@require_POST
@login_required
def position_translate(request, pk):
    """AJAX endpoint: translate position fields synchronously."""
    position = get_object_or_404(Position, pk=pk, company=request.company)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': _('JSON inválido.')}, status=400)

    translatable_fields = ['description', 'requirements', 'benefits', 'about_company_snippet']

    # Auto-detect source language: pick the language that has the most content
    source_lang = None
    for lang in ALL_LANGUAGES:
        if any((getattr(position, f'{f}_{lang}', '') or '').strip() for f in translatable_fields):
            source_lang = lang
            break
    if not source_lang:
        return JsonResponse({'error': _('No hay contenido para traducir.')}, status=400)

    try:
        translate_fields(position, source_lang, translatable_fields)
    except Exception:
        logger.exception("Error translating position pk=%s", pk)
        return JsonResponse(
            {'error': _('Error al traducir. Inténtalo de nuevo.')},
            status=500,
        )

    position.refresh_from_db()
    translations = {}
    for lang in ALL_LANGUAGES:
        translations[lang] = {
            field: getattr(position, f'{field}_{lang}', '') or ''
            for field in translatable_fields
        }

    return JsonResponse({'translations': translations})


@login_required
def position_candidates_pdf(request, pk):
    """Generate a PDF report with candidate summaries and AI analysis."""
    position = get_object_or_404(Position, pk=pk, company=request.company)
    candidates = position.candidates.order_by('-ai_fit_score', '-created_at')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, spaceAfter=14)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceBefore=16, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=12)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=9, leading=12, leftIndent=12)

    elements = []

    # Header
    elements.append(Paragraph(position.title, title_style))
    dept = position.department.name if position.department else ''
    location = position.location or ''
    meta_parts = [p for p in [dept, location, position.get_status_display()] if p]
    elements.append(Paragraph(' · '.join(meta_parts), subtitle_style))

    if not candidates.exists():
        elements.append(Paragraph(_('No hay candidatos en esta posición.'), body_style))
    else:
        elements.append(Paragraph(
            _('%(count)d candidatos') % {'count': candidates.count()},
            body_style,
        ))
        elements.append(Spacer(1, 8))

        for candidate in candidates:
            # Candidate name header
            score_text = f' — {candidate.ai_fit_score}/10' if candidate.ai_fit_score else ''
            elements.append(Paragraph(
                f'{candidate.full_name}{score_text}',
                h2_style,
            ))

            # Info table
            info_data = [
                [Paragraph(_('Email'), label_style), Paragraph(candidate.email or '—', body_style)],
                [Paragraph(_('Estado'), label_style), Paragraph(candidate.get_status_display(), body_style)],
            ]
            if candidate.phone:
                info_data.append([Paragraph(_('Teléfono'), label_style), Paragraph(candidate.phone, body_style)])
            if candidate.rating:
                info_data.append([
                    Paragraph(_('Valoración'), label_style),
                    Paragraph('★' * candidate.rating + '☆' * (5 - candidate.rating), body_style),
                ])

            info_table = Table(info_data, colWidths=[3.5 * cm, 13 * cm])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            elements.append(info_table)

            # AI Summary
            if candidate.ai_summary:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(_('Resumen IA'), label_style))
                elements.append(Paragraph(candidate.ai_summary, body_style))

            # Strengths
            if candidate.ai_strengths:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(_('Puntos fuertes'), label_style))
                for s in candidate.ai_strengths:
                    elements.append(Paragraph(f'• {s}', bullet_style))

            # Weaknesses
            if candidate.ai_weaknesses:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(_('Puntos débiles'), label_style))
                for w in candidate.ai_weaknesses:
                    elements.append(Paragraph(f'• {w}', bullet_style))

            # Recruiter notes
            if candidate.recruiter_notes:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(_('Notas del reclutador'), label_style))
                elements.append(Paragraph(candidate.recruiter_notes, body_style))

            elements.append(Spacer(1, 10))

    doc.build(elements)
    buf.seek(0)

    filename = f'candidatos_{position.title[:30].replace(" ", "_")}.pdf'
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
