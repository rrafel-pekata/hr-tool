import io
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
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
    company = request.company
    candidates = position.candidates.order_by(
        models.F('ai_fit_score').desc(nulls_last=True), '-created_at',
    ).distinct()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    # Brand color
    brand = colors.HexColor('#4F46E5')
    brand_light = colors.HexColor('#EEF2FF')
    green_bg = colors.HexColor('#F0FDF4')
    green_text = colors.HexColor('#166534')
    red_bg = colors.HexColor('#FEF2F2')
    red_text = colors.HexColor('#991B1B')
    grey_text = colors.HexColor('#6B7280')
    dark_text = colors.HexColor('#111827')

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, textColor=brand, spaceAfter=4)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=grey_text, spaceAfter=6)
    company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=11, textColor=dark_text, alignment=TA_RIGHT)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=brand, spaceBefore=4, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=13, textColor=dark_text)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, textColor=grey_text, spaceBefore=6, spaceAfter=2)
    bullet_green = ParagraphStyle('BulletGreen', parent=styles['Normal'], fontSize=9, leading=12, leftIndent=12, textColor=green_text)
    bullet_red = ParagraphStyle('BulletRed', parent=styles['Normal'], fontSize=9, leading=12, leftIndent=12, textColor=red_text)
    score_style = ParagraphStyle('Score', parent=styles['Normal'], fontSize=11, textColor=brand, alignment=TA_RIGHT)
    count_style = ParagraphStyle('Count', parent=styles['Normal'], fontSize=10, textColor=grey_text, spaceAfter=10)

    elements = []

    # --- Header with logo ---
    header_data = []
    title_parts = [Paragraph(position.title, title_style)]
    dept = position.department.name if position.department else ''
    location = position.location or ''
    meta_parts = [p for p in [dept, location, position.get_status_display()] if p]
    if meta_parts:
        title_parts.append(Paragraph(' · '.join(meta_parts), subtitle_style))

    right_parts = [Paragraph(company.name, company_style)]

    if company.logo:
        try:
            logo_img = Image(company.logo.path, width=2.5 * cm, height=2.5 * cm)
            logo_img.hAlign = 'RIGHT'
            right_parts.insert(0, logo_img)
        except Exception:
            pass

    header_data.append([title_parts, right_parts])
    header_table = Table(header_data, colWidths=[12 * cm, 5 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width='100%', thickness=2, color=brand, spaceAfter=12))

    if not candidates.exists():
        elements.append(Paragraph(_('No hay candidatos en esta posición.'), body_style))
    else:
        elements.append(Paragraph(
            _('%(count)d candidatos') % {'count': candidates.count()},
            count_style,
        ))

        for idx, candidate in enumerate(candidates):
            # Candidate card header with score
            name_text = f'<b>{candidate.full_name}</b>'
            score_text = f'<b>{candidate.ai_fit_score}/10</b>' if candidate.ai_fit_score else ''
            card_header = Table(
                [[Paragraph(name_text, h2_style), Paragraph(score_text, score_style)]],
                colWidths=[13 * cm, 4 * cm],
            )
            card_header.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), brand_light),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (0, 0), 10),
                ('RIGHTPADDING', (1, 0), (1, 0), 10),
                ('ROUNDEDCORNERS', [4, 4, 0, 0]),
            ]))
            elements.append(card_header)

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

            info_table = Table(info_data, colWidths=[3.5 * cm, 13.5 * cm])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
            ]))
            elements.append(info_table)

            # AI Summary
            if candidate.ai_summary:
                elements.append(Paragraph(_('Resumen IA'), label_style))
                elements.append(Paragraph(candidate.ai_summary, body_style))

            # Strengths & Weaknesses side by side
            has_strengths = bool(candidate.ai_strengths)
            has_weaknesses = bool(candidate.ai_weaknesses)
            if has_strengths or has_weaknesses:
                elements.append(Spacer(1, 6))
                strength_parts = []
                weakness_parts = []
                if has_strengths:
                    strength_parts.append(Paragraph(f'<b>{_("Puntos fuertes")}</b>', ParagraphStyle('SLabel', parent=body_style, textColor=green_text, fontSize=8)))
                    for s in candidate.ai_strengths:
                        strength_parts.append(Paragraph(f'• {s}', bullet_green))
                if has_weaknesses:
                    weakness_parts.append(Paragraph(f'<b>{_("Puntos débiles")}</b>', ParagraphStyle('WLabel', parent=body_style, textColor=red_text, fontSize=8)))
                    for w in candidate.ai_weaknesses:
                        weakness_parts.append(Paragraph(f'• {w}', bullet_red))

                sw_table = Table(
                    [[strength_parts or '', weakness_parts or '']],
                    colWidths=[8.5 * cm, 8.5 * cm],
                )
                sw_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (0, 0), (0, 0), green_bg if has_strengths else colors.white),
                    ('BACKGROUND', (1, 0), (1, 0), red_bg if has_weaknesses else colors.white),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('ROUNDEDCORNERS', [4, 4, 4, 4]),
                ]))
                elements.append(sw_table)

            # Recruiter notes
            if candidate.recruiter_notes:
                elements.append(Paragraph(_('Notas del reclutador'), label_style))
                elements.append(Paragraph(candidate.recruiter_notes, body_style))

            elements.append(Spacer(1, 14))
            if idx < len(candidates) - 1:
                elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#E5E7EB'), spaceAfter=6))

    doc.build(elements)
    buf.seek(0)

    filename = f'candidatos_{position.title[:30].replace(" ", "_")}.pdf'
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
