from django.db import models

from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.tenants.models import Company, Department


class Position(SoftDeleteMixin, TimeStampedModel):
    """Oferta de trabajo / Posición."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Tiempo completo'
        PART_TIME = 'part_time', 'Media jornada'
        FREELANCE = 'freelance', 'Freelance'
        INTERNSHIP = 'internship', 'Prácticas'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        PUBLISHED = 'published', 'Publicada'
        PAUSED = 'paused', 'Pausada'
        CLOSED = 'closed', 'Cerrada'

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Empresa',
    )
    title = models.CharField('Título del puesto', max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='positions',
        verbose_name='Departamento',
    )
    location = models.CharField('Ubicación', max_length=200, blank=True)
    employment_type = models.CharField(
        'Tipo de empleo',
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    description = models.TextField('Descripción del puesto', blank=True)
    requirements = models.TextField('Requisitos', blank=True)
    about_company_snippet = models.TextField('Sobre la empresa', blank=True)
    benefits = models.TextField('Qué ofrecemos', blank=True)
    salary_range = models.CharField('Rango salarial', max_length=100, blank=True)
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField('Fecha de publicación', null=True, blank=True)
    closed_at = models.DateTimeField('Fecha de cierre', null=True, blank=True)
    has_case_study = models.BooleanField('Usa case study', default=False)
    ai_generated_draft = models.BooleanField('Borrador generado con IA', default=False)

    class Meta:
        verbose_name = 'Posición'
        verbose_name_plural = 'Posiciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.company.name}'

    @property
    def candidate_count(self):
        return self.candidates.count()
