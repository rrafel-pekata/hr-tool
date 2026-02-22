from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    """Empresa / Tenant."""
    name = models.CharField('Nombre', max_length=200)
    slug = models.SlugField('Slug', unique=True, max_length=200)
    description = models.TextField('Descripción', blank=True, help_text='Qué hace la empresa, sector, misión...')
    logo = models.ImageField('Logo', upload_to='companies/logos/', blank=True)
    website = models.URLField('Web corporativa', blank=True)
    # Info general para ofertas
    benefits = models.TextField('Beneficios y ventajas', blank=True, help_text='Qué ofrece la empresa a los trabajadores: seguro, formación, fruta, gym...')
    work_schedule = models.CharField('Jornada laboral', max_length=200, blank=True, help_text='Ej: L-V 9:00-18:00, jornada flexible...')
    remote_policy = models.CharField('Política de trabajo remoto', max_length=200, blank=True, help_text='Ej: 100% remoto, híbrido 3 días oficina, presencial...')
    office_location = models.CharField('Ubicación oficina', max_length=300, blank=True, help_text='Dirección o zona de la oficina principal')
    culture = models.TextField('Cultura y valores', blank=True, help_text='Valores de la empresa, ambiente de trabajo, equipo...')
    is_active = models.BooleanField('Activa', default=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Perfil de usuario vinculado a una empresa."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        RECRUITER = 'recruiter', 'Recruiter'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Empresa',
    )
    role = models.CharField(
        'Rol',
        max_length=20,
        choices=Role.choices,
        default=Role.RECRUITER,
    )

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.company.name})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
