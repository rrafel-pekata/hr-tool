from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.tenants.models import Company, Department


class Position(SoftDeleteMixin, TimeStampedModel):
    """Oferta de trabajo / Posición."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', _('Tiempo completo')
        PART_TIME = 'part_time', _('Media jornada')
        FREELANCE = 'freelance', _('Freelance')
        INTERNSHIP = 'internship', _('Prácticas')

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Borrador')
        PUBLISHED = 'published', _('Publicada')
        PAUSED = 'paused', _('Pausada')
        CLOSED = 'closed', _('Cerrada')

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('Empresa'),
    )
    title = models.CharField(_('Título del puesto'), max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='positions',
        verbose_name=_('Departamento'),
    )
    location = models.CharField(_('Ubicación'), max_length=200, blank=True)
    employment_type = models.CharField(
        _('Tipo de empleo'),
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    description = models.TextField(_('Descripción del puesto'), blank=True)
    requirements = models.TextField(_('Requisitos'), blank=True)
    about_company_snippet = models.TextField(_('Sobre la empresa'), blank=True)
    benefits = models.TextField(_('Qué ofrecemos'), blank=True)
    salary_range = models.CharField(_('Rango salarial'), max_length=100, blank=True)
    status = models.CharField(
        _('Estado'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(_('Fecha de publicación'), null=True, blank=True)
    closed_at = models.DateTimeField(_('Fecha de cierre'), null=True, blank=True)
    has_case_study = models.BooleanField(_('Usa case study'), default=False)
    ai_generated_draft = models.BooleanField(_('Borrador generado con IA'), default=False)

    class Meta:
        verbose_name = _('Posición')
        verbose_name_plural = _('Posiciones')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.company.name}'

    @property
    def candidate_count(self):
        return self.candidates.count()
