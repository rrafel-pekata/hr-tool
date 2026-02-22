from django.conf import settings
from django.db import models

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel


class Interview(TimeStampedModel):
    """Entrevista programada con un candidato."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Programada'
        COMPLETED = 'completed', 'Realizada'
        CANCELLED = 'cancelled', 'Cancelada'
        NO_SHOW = 'no_show', 'No se presentó'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='interviews',
        verbose_name='Candidato',
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interviews_as_interviewer',
        verbose_name='Entrevistador',
    )
    scheduled_at = models.DateTimeField('Fecha y hora')
    duration_minutes = models.IntegerField('Duración (minutos)', default=60)
    location_or_link = models.CharField(
        'Lugar o link',
        max_length=500,
        blank=True,
    )
    google_event_id = models.CharField(
        'ID evento Google Calendar',
        max_length=200,
        blank=True,
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField('Notas', blank=True)
    strengths = models.TextField('Puntos fuertes', blank=True)
    weaknesses = models.TextField('Puntos débiles', blank=True)
    overall_score = models.IntegerField(
        'Puntuación global',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'Entrevista {self.candidate} — {self.scheduled_at:%d/%m/%Y %H:%M}'
