from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteMixin, TimeStampedModel


class Company(SoftDeleteMixin, TimeStampedModel):
    """Empresa / Tenant."""
    name = models.CharField(_('Nombre'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, max_length=200)
    description = models.TextField(_('Descripción'), blank=True, help_text=_('Qué hace la empresa, sector, misión...'))
    logo = models.ImageField(_('Logo'), upload_to='companies/logos/', blank=True)
    website = models.URLField(_('Web corporativa'), blank=True)
    # Info general para ofertas
    benefits = models.TextField(_('Beneficios y ventajas'), blank=True, help_text=_('Qué ofrece la empresa a los trabajadores: seguro, formación, fruta, gym...'))
    work_schedule = models.CharField(_('Jornada laboral'), max_length=200, blank=True, help_text=_('Ej: L-V 9:00-18:00, jornada flexible...'))
    remote_policy = models.CharField(_('Política de trabajo remoto'), max_length=200, blank=True, help_text=_('Ej: 100% remoto, híbrido 3 días oficina, presencial...'))
    office_location = models.CharField(_('Ubicación oficina'), max_length=300, blank=True, help_text=_('Dirección o zona de la oficina principal'))
    culture = models.TextField(_('Cultura y valores'), blank=True, help_text=_('Valores de la empresa, ambiente de trabajo, equipo...'))
    is_active = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Empresa')
        verbose_name_plural = _('Empresas')
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Perfil de usuario vinculado a una empresa. DEPRECATED: usar CompanyMembership."""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        RECRUITER = 'recruiter', _('Recruiter')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('Empresa'),
    )
    role = models.CharField(
        _('Rol'),
        max_length=20,
        choices=Role.choices,
        default=Role.RECRUITER,
    )

    class Meta:
        verbose_name = _('Perfil de usuario')
        verbose_name_plural = _('Perfiles de usuario')

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.company.name})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class CompanyMembership(models.Model):
    """Membresía usuario ↔ empresa (through model)."""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        RECRUITER = 'recruiter', _('Recruiter')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_memberships',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('Empresa'),
    )
    role = models.CharField(
        _('Rol'),
        max_length=20,
        choices=Role.choices,
        default=Role.RECRUITER,
    )

    class Meta:
        verbose_name = _('Membresía de empresa')
        verbose_name_plural = _('Membresías de empresa')
        unique_together = [('user', 'company')]

    def __str__(self):
        return f'{self.user.get_full_name()} → {self.company.name} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class Department(TimeStampedModel):
    """Departamento dentro de una empresa."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_('Empresa'),
    )
    name = models.CharField(_('Nombre'), max_length=100)
    description = models.TextField(_('Descripción'), blank=True)

    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')
        unique_together = [('company', 'name')]
        ordering = ['name']

    def __str__(self):
        return self.name
