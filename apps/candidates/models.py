import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.positions.models import Position


class Candidate(SoftDeleteMixin, TimeStampedModel):
    """Candidato asociado a una posición."""

    class Source(models.TextChoices):
        MANUAL = 'manual', _('Manual')
        LINKEDIN = 'linkedin', _('LinkedIn')
        EMAIL = 'email', _('Email')
        PORTAL = 'portal', _('Portal')

    class Status(models.TextChoices):
        NEW = 'new', _('Nuevo')
        REVIEWING = 'reviewing', _('En revisión')
        PHONE_SCREEN = 'phone_screen', _('Phone screen')
        INTERVIEW_SCHEDULED = 'interview_scheduled', _('Entrevista programada')
        INTERVIEW_DONE = 'interview_done', _('Entrevista realizada')
        CASE_SENT = 'case_sent', _('Case study enviado')
        CASE_SUBMITTED = 'case_submitted', _('Case study entregado')
        EVALUATION = 'evaluation', _('En evaluación')
        OFFER_SENT = 'offer_sent', _('Oferta enviada')
        HIRED = 'hired', _('Contratado')
        REJECTED = 'rejected', _('Descartado')
        WITHDRAWN = 'withdrawn', _('Retirado')

    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='candidates',
        verbose_name=_('Posición'),
    )
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellidos'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Teléfono'), max_length=30, blank=True)
    linkedin_url = models.URLField(_('LinkedIn'), blank=True)
    cv_file = models.FileField(_('CV (PDF)'), upload_to='candidates/cvs/', blank=True)
    cv_text_extracted = models.TextField(_('Texto extraído del CV'), blank=True)
    source = models.CharField(
        _('Origen'),
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    status = models.CharField(
        _('Estado'),
        max_length=25,
        choices=Status.choices,
        default=Status.NEW,
    )
    portal_token = models.UUIDField(
        _('Token portal'),
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    portal_token_expires_at = models.DateTimeField(
        _('Expiración del token'),
        null=True,
        blank=True,
    )
    recruiter_notes = models.TextField(_('Notas del reclutador'), blank=True)
    ai_summary = models.TextField(_('Resumen IA'), blank=True)
    ai_strengths = models.JSONField(_('Puntos fuertes IA'), default=list, blank=True)
    ai_weaknesses = models.JSONField(_('Puntos débiles IA'), default=list, blank=True)
    ai_fit_score = models.IntegerField(_('Puntuación encaje IA'), null=True, blank=True)
    rating = models.IntegerField(_('Valoración'), null=True, blank=True)

    class Meta:
        verbose_name = _('Candidato')
        verbose_name_plural = _('Candidatos')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
