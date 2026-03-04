from django.conf import settings
from django.shortcuts import redirect
from django.utils import translation

from apps.tenants.models import CompanyMembership, Company

# Paths that don't require an active company
EXEMPT_PATHS = (
    '/login/', '/logout/', '/admin/', '/portal/', '/select-company/',
)


class TenantMiddleware:
    """Adjunta la empresa activa del usuario a cada request usando CompanyMembership."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        request.membership = None
        request.user_companies = []

        if request.user.is_authenticated:
            memberships = list(
                CompanyMembership.objects.filter(
                    user=request.user,
                    company__deleted_at__isnull=True,
                )
                .select_related('company')
                .order_by('company__name')
            )
            request.user_companies = [m.company for m in memberships]

            if memberships:
                active_company_id = request.session.get('active_company_id')

                if active_company_id:
                    # Validate the stored company belongs to the user
                    membership = next(
                        (m for m in memberships if str(m.company_id) == str(active_company_id)),
                        None,
                    )
                    if membership:
                        request.company = membership.company
                        request.membership = membership

                if not request.company and len(memberships) == 1:
                    # Auto-select if user only has one company
                    request.company = memberships[0].company
                    request.membership = memberships[0]
                    request.session['active_company_id'] = str(request.company.pk)

        response = self.get_response(request)
        return response


class UserLanguageMiddleware:
    """Activate the user's preferred language from their UserSettings."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                lang = request.user.settings.language
            except Exception:
                lang = settings.LANGUAGE_CODE
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        return response
