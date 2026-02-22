def build_user_context(request):
    """Extrae contexto del usuario para enviar al LLM."""
    user = request.user
    profile = getattr(user, 'profile', None)

    name = user.get_full_name() or user.username
    role = profile.get_role_display() if profile else 'Desconocido'
    company = profile.company.name if profile and profile.company else 'Sin empresa'
    plan = 'Gratuito (todas las funcionalidades disponibles)'
    page = request.META.get('HTTP_REFERER', 'Desconocida')

    return (
        f"Nombre: {name}\n"
        f"Rol: {role}\n"
        f"Empresa actual: {company}\n"
        f"Plan: {plan}\n"
        f"Página actual: {page}"
    )
