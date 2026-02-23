def build_user_context(request):
    """Extrae contexto del usuario para enviar al LLM."""
    user = request.user

    name = user.get_full_name() or user.username
    role = request.membership.get_role_display() if getattr(request, 'membership', None) else 'Desconocido'
    company = request.company.name if getattr(request, 'company', None) else 'Sin empresa'
    plan = 'Gratuito (todas las funcionalidades disponibles)'
    page = request.META.get('HTTP_REFERER', 'Desconocida')

    return (
        f"Nombre: {name}\n"
        f"Rol: {role}\n"
        f"Empresa actual: {company}\n"
        f"Plan: {plan}\n"
        f"Página actual: {page}"
    )
