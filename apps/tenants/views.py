import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.services import call_claude

from .forms import CompanyForm, DepartmentForm
from .models import Company, CompanyMembership, Department
from .prompts import IMPROVE_COMPANY_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@login_required
def company_list(request):
    """Listado de empresas del usuario."""
    memberships = CompanyMembership.objects.filter(user=request.user)
    company_ids = memberships.values_list('company_id', flat=True)

    if company_ids:
        companies = Company.objects.filter(pk__in=company_ids).annotate(
            active_positions=Count(
                'positions',
                filter=Q(positions__status='published')
            )
        )
    elif request.user.is_superuser:
        # Superuser sin memberships: ver todas
        companies = Company.objects.all().annotate(
            active_positions=Count(
                'positions',
                filter=Q(positions__status='published')
            )
        )
    else:
        companies = Company.objects.none()

    return render(request, 'tenants/company_list.html', {'companies': companies})


@login_required
def company_create(request):
    """Crear nueva empresa."""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            # Create membership as admin
            CompanyMembership.objects.create(
                user=request.user,
                company=company,
                role=CompanyMembership.Role.ADMIN,
            )
            # Set as active company
            request.session['active_company_id'] = str(company.pk)
            messages.success(request, f'Empresa "{company.name}" creada correctamente.')
            return redirect('tenants:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    return render(request, 'tenants/company_form.html', {
        'form': form,
        'title': 'Nueva empresa',
    })


@login_required
def company_edit(request, pk):
    """Editar empresa existente."""
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa actualizada correctamente.')
            return redirect('tenants:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'tenants/company_form.html', {
        'form': form,
        'company': company,
        'title': f'Editar {company.name}',
    })


@login_required
def company_detail(request, pk):
    """Dashboard de empresa: KPIs + listado de posiciones."""
    company = get_object_or_404(Company, pk=pk)
    positions = company.positions.annotate(
        num_candidates=Count('candidates')
    ).order_by('-created_at')

    # KPIs
    total_positions = positions.count()
    active_positions = positions.filter(status='published').count()
    total_candidates = sum(p.num_candidates for p in positions)

    return render(request, 'tenants/company_detail.html', {
        'company': company,
        'positions': positions,
        'total_positions': total_positions,
        'active_positions': active_positions,
        'total_candidates': total_candidates,
    })


@require_POST
@login_required
def company_ai_improve(request):
    """Endpoint AJAX: mejorar información de empresa con IA."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    user_prompt = IMPROVE_COMPANY_PROMPT.format(
        name=data.get('name', ''),
        website=data.get('website', ''),
        description=data.get('description', ''),
        benefits=data.get('benefits', ''),
        work_schedule=data.get('work_schedule', ''),
        remote_policy=data.get('remote_policy', ''),
        office_location=data.get('office_location', ''),
        culture=data.get('culture', ''),
    )

    try:
        result = call_claude(SYSTEM_PROMPT, user_prompt, json_output=True)
        if isinstance(result, dict):
            return JsonResponse(result)
        return JsonResponse({'description': str(result)})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        logger.exception("Error llamando a Claude API")
        return JsonResponse(
            {'error': 'Error al conectar con la IA. Inténtalo de nuevo.'},
            status=500,
        )


@require_POST
@login_required
def company_delete(request, pk):
    """Soft-delete de empresa."""
    company = get_object_or_404(Company, pk=pk)
    company.soft_delete()
    # Limpiar empresa activa de la sesión si era esta
    if str(request.session.get('active_company_id')) == str(company.pk):
        request.session.pop('active_company_id', None)
    messages.success(request, f'Empresa "{company.name}" eliminada.')
    return redirect('core:select_company')


@login_required
def company_toggle_active(request, pk):
    """Activar/desactivar empresa."""
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.is_active = not company.is_active
        company.save(update_fields=['is_active'])
        estado = 'activada' if company.is_active else 'desactivada'
        messages.success(request, f'Empresa {estado} correctamente.')
    return redirect('tenants:company_detail', pk=company.pk)


# ─── Department CRUD ─────────────────────────────────────────────


@login_required
def department_list(request):
    """Lista departamentos de la empresa activa con conteo de posiciones."""
    if not request.company:
        return redirect('core:select_company')

    departments = (
        Department.objects.filter(company=request.company)
        .annotate(num_positions=Count('positions'))
        .order_by('name')
    )
    return render(request, 'tenants/department_list.html', {
        'departments': departments,
    })


@login_required
def department_create(request):
    """Crear nuevo departamento."""
    if not request.company:
        return redirect('core:select_company')

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.company = request.company
            department.save()
            messages.success(request, f'Departamento "{department.name}" creado correctamente.')
            return redirect('tenants:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'tenants/department_form.html', {
        'form': form,
        'title': 'Nuevo departamento',
    })


@login_required
def department_edit(request, pk):
    """Editar departamento existente."""
    department = get_object_or_404(Department, pk=pk, company=request.company)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento actualizado correctamente.')
            return redirect('tenants:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'tenants/department_form.html', {
        'form': form,
        'department': department,
        'title': f'Editar: {department.name}',
    })


@require_POST
@login_required
def department_delete(request, pk):
    """Eliminar departamento (posiciones quedan con department=NULL)."""
    department = get_object_or_404(Department, pk=pk, company=request.company)
    name = department.name
    department.delete()
    messages.success(request, f'Departamento "{name}" eliminado.')
    return redirect('tenants:department_list')
