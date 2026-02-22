from django.contrib.auth.mixins import LoginRequiredMixin


class TenantQuerySetMixin:
    """Filtra querysets por la empresa del usuario logado."""

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(company=self.request.company)
        return qs.none()


class TenantRequiredMixin(LoginRequiredMixin, TenantQuerySetMixin):
    """Requiere login y filtra por tenant."""
    pass
