from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel


class Interview(TimeStampedModel):
    """Entrevista programada con un candidato."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('Programada')
        COMPLETED = 'completed', _('Realizada')
        CANCELLED = 'cancelled', _('Cancelada')
        NO_SHOW = 'no_show', _('No se presentó')

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='interviews',
        verbose_name=_('Candidato'),
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interviews_as_interviewer',
        verbose_name=_('Entrevistador'),
    )
    scheduled_at = models.DateTimeField(_('Fecha y hora'))
    duration_minutes = models.IntegerField(_('Duración (minutos)'), default=60)
    location_or_link = models.CharField(
        _('Lugar o link'),
        max_length=500,
        blank=True,
    )
    google_event_id = models.CharField(
        _('ID evento Google Calendar'),
        max_length=200,
        blank=True,
    )
    status = models.CharField(
        _('Estado'),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField(_('Notas'), blank=True)
    strengths = models.TextField(_('Puntos fuertes'), blank=True)
    weaknesses = models.TextField(_('Puntos débiles'), blank=True)
    overall_score = models.IntegerField(
        _('Puntuación global'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Entrevista')
        verbose_name_plural = _('Entrevistas')
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'Entrevista {self.candidate} — {self.scheduled_at:%d/%m/%Y %H:%M}'
