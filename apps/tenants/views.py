from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompanyForm
from .models import Company, UserProfile


@login_required
def company_list(request):
    """Listado de empresas del usuario."""
    if hasattr(request.user, 'profile'):
        companies = Company.objects.filter(
            pk=request.user.profile.company_id
        ).annotate(
            active_positions=Count(
                'positions',
                filter=Q(positions__status='published')
            )
        )
    else:
        # Superuser sin perfil: ver todas
        companies = Company.objects.all().annotate(
            active_positions=Count(
                'positions',
                filter=Q(positions__status='published')
            )
        )
    return render(request, 'tenants/company_list.html', {'companies': companies})


@login_required
def company_create(request):
    """Crear nueva empresa."""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            # Si el usuario no tiene perfil, asignarlo como admin
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(
                    user=request.user,
                    company=company,
                    role=UserProfile.Role.ADMIN,
                )
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
