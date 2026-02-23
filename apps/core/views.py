from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.tenants.models import Company


@login_required
def dashboard(request):
    """Redirige al dashboard de la empresa activa o al selector."""
    if not request.company:
        if request.user_companies:
            return redirect('core:select_company')
        return redirect('core:select_company')
    return redirect('tenants:company_detail', pk=request.company.pk)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    error = None
    if request.method == 'POST':
        email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        error = 'Credenciales inválidas.'
    return render(request, 'registration/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def help_page(request):
    return render(request, 'core/help.html')


@login_required
def select_company(request):
    """Muestra tarjetas de empresas del usuario para seleccionar una."""
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if company_id:
            # Validate membership
            membership = request.user.company_memberships.filter(
                company_id=company_id,
            ).select_related('company').first()
            if membership:
                request.session['active_company_id'] = str(membership.company_id)
                return redirect('core:dashboard')

    companies = request.user_companies
    memberships = {
        str(m.company_id): m
        for m in request.user.company_memberships.select_related('company').all()
    }
    company_data = []
    for company in companies:
        m = memberships.get(str(company.pk))
        company_data.append({
            'company': company,
            'role': m.get_role_display() if m else '',
        })

    return render(request, 'tenants/company_select.html', {
        'company_data': company_data,
    })


@require_POST
@login_required
def switch_company(request):
    """POST endpoint para cambiar de empresa (desde sidebar)."""
    company_id = request.POST.get('company_id')
    if company_id:
        membership = request.user.company_memberships.filter(
            company_id=company_id,
        ).first()
        if membership:
            request.session['active_company_id'] = str(membership.company_id)

    # Redirect to the referring page, or dashboard
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)
