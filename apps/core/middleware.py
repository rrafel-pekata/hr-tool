from apps.tenants.models import UserProfile


class TenantMiddleware:
    """Adjunta la empresa del usuario logado a cada request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                request.company = profile.company
            except UserProfile.DoesNotExist:
                pass
        response = self.get_response(request)
        return response
