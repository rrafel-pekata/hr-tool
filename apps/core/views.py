from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def dashboard(request):
    """Redirige a /companies/ si hay más de una empresa, sino al dashboard de la empresa."""
    if request.company:
        return redirect('tenants:company_detail', pk=request.company.pk)
    return redirect('tenants:company_list')


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
