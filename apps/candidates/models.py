import uuid

from django.db import models

from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.positions.models import Position


class Candidate(SoftDeleteMixin, TimeStampedModel):
    """Candidato asociado a una posición."""

    class Source(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        LINKEDIN = 'linkedin', 'LinkedIn'
        EMAIL = 'email', 'Email'
        PORTAL = 'portal', 'Portal'

    class Status(models.TextChoices):
        NEW = 'new', 'Nuevo'
        REVIEWING = 'reviewing', 'En revisión'
        PHONE_SCREEN = 'phone_screen', 'Phone screen'
        INTERVIEW_SCHEDULED = 'interview_scheduled', 'Entrevista programada'
        INTERVIEW_DONE = 'interview_done', 'Entrevista realizada'
        CASE_SENT = 'case_sent', 'Case study enviado'
        CASE_SUBMITTED = 'case_submitted', 'Case study entregado'
        EVALUATION = 'evaluation', 'En evaluación'
        OFFER_SENT = 'offer_sent', 'Oferta enviada'
        HIRED = 'hired', 'Contratado'
        REJECTED = 'rejected', 'Descartado'
        WITHDRAWN = 'withdrawn', 'Retirado'

    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='candidates',
        verbose_name='Posición',
    )
    first_name = models.CharField('Nombre', max_length=100)
    last_name = models.CharField('Apellidos', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Teléfono', max_length=30, blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    cv_file = models.FileField('CV (PDF)', upload_to='candidates/cvs/', blank=True)
    cv_text_extracted = models.TextField('Texto extraído del CV', blank=True)
    source = models.CharField(
        'Origen',
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    status = models.CharField(
        'Estado',
        max_length=25,
        choices=Status.choices,
        default=Status.NEW,
    )
    portal_token = models.UUIDField(
        'Token portal',
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    portal_token_expires_at = models.DateTimeField(
        'Expiración del token',
        null=True,
        blank=True,
    )
    recruiter_notes = models.TextField('Notas del reclutador', blank=True)
    ai_summary = models.TextField('Resumen IA', blank=True)
    ai_strengths = models.JSONField('Puntos fuertes IA', default=list, blank=True)
    ai_weaknesses = models.JSONField('Puntos débiles IA', default=list, blank=True)
    ai_fit_score = models.IntegerField('Puntuación encaje IA', null=True, blank=True)
    rating = models.IntegerField('Valoración', null=True, blank=True)

    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
