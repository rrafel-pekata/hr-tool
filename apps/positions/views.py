import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.services import call_claude

from .forms import PositionForm
from .models import Position
from .prompts import GENERATE_POSITION_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@login_required
def position_list(request):
    """Listado de posiciones de la empresa activa."""
    if not request.company:
        return redirect('tenants:company_list')

    positions = Position.objects.filter(company=request.company).annotate(
        num_candidates=Count('candidates')
    ).order_by('-created_at')

    # Filtro por estado
    status_filter = request.GET.get('status', '')
    if status_filter:
        positions = positions.filter(status=status_filter)

    return render(request, 'positions/position_list.html', {
        'positions': positions,
        'status_filter': status_filter,
        'status_choices': Position.Status.choices,
    })


@login_required
def position_create(request):
    """Crear nueva posición."""
    if not request.company:
        messages.error(request, 'Debes tener una empresa asignada para crear posiciones.')
        return redirect('tenants:company_list')

    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.company = request.company
            position.save()
            messages.success(request, f'Posición "{position.title}" creada correctamente.')
            return redirect('positions:position_detail', pk=position.pk)
    else:
        form = PositionForm()
    return render(request, 'positions/position_form.html', {
        'form': form,
        'title': 'Nueva posición',
    })


@login_required
def position_edit(request, pk):
    """Editar posición existente."""
    position = get_object_or_404(Position, pk=pk, company=request.company)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Posición actualizada correctamente.')
            return redirect('positions:position_detail', pk=position.pk)
    else:
        form = PositionForm(instance=position)
    return render(request, 'positions/position_form.html', {
        'form': form,
        'position': position,
        'title': f'Editar: {position.title}',
    })


@login_required
def position_detail(request, pk):
    """Vista detalle de posición: oferta + candidatos + case study."""
    position = get_object_or_404(
        Position.objects.annotate(num_candidates=Count('candidates')),
        pk=pk,
        company=request.company,
    )
    candidates = position.candidates.order_by('-created_at')

    # Filtro candidatos por estado
    candidate_status = request.GET.get('candidate_status', '')
    if candidate_status:
        candidates = candidates.filter(status=candidate_status)

    case_studies = position.case_studies.all()

    return render(request, 'positions/position_detail.html', {
        'position': position,
        'candidates': candidates,
        'candidate_status': candidate_status,
        'case_studies': case_studies,
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
            messages.success(request, 'Posición publicada.')
        elif action == 'pause':
            position.status = Position.Status.PAUSED
            messages.success(request, 'Posición pausada.')
        elif action == 'close':
            position.status = Position.Status.CLOSED
            position.closed_at = timezone.now()
            messages.success(request, 'Posición cerrada.')
        elif action == 'draft':
            position.status = Position.Status.DRAFT
            messages.success(request, 'Posición movida a borrador.')
        position.save()
    return redirect('positions:position_detail', pk=position.pk)


@require_POST
@login_required
def position_ai_generate(request):
    """Endpoint AJAX: mejorar oferta con IA."""
    if not request.company:
        return JsonResponse({'error': 'Sin empresa asignada.'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    company = request.company
    user_prompt = GENERATE_POSITION_PROMPT.format(
        title=data.get('title', ''),
        department=data.get('department', ''),
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
            {'error': 'Error al conectar con la IA. Inténtalo de nuevo.'},
            status=500,
        )
