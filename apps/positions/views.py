import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_POST

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

    source_lang = data.get('source_lang', get_language())
    if source_lang not in ('es', 'en', 'ca'):
        return JsonResponse({'error': _('Idioma no válido.')}, status=400)

    translatable_fields = ['description', 'requirements', 'benefits', 'about_company_snippet']

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
