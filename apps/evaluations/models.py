from django.db import models

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel


class AIEvaluation(TimeStampedModel):
    """Evaluación final generada por IA para un candidato."""

    class Recommendation(models.TextChoices):
        HIRE = 'hire', 'Contratar'
        HOLD = 'hold', 'En espera'
        REJECT = 'reject', 'Rechazar'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='Candidato',
    )
    generated_at = models.DateTimeField('Fecha de generación', auto_now_add=True)
    prompt_used = models.TextField('Prompt enviado')
    result = models.TextField('Respuesta completa de Claude')
    cv_score = models.IntegerField('Puntuación CV', null=True, blank=True)
    interview_score = models.IntegerField(
        'Puntuación entrevista',
        null=True,
        blank=True,
    )
    case_score = models.IntegerField(
        'Puntuación case study',
        null=True,
        blank=True,
    )
    overall_score = models.IntegerField(
        'Puntuación final',
        null=True,
        blank=True,
    )
    recommendation = models.CharField(
        'Recomendación',
        max_length=10,
        choices=Recommendation.choices,
        blank=True,
    )
    summary = models.TextField('Resumen ejecutivo', blank=True)

    class Meta:
        verbose_name = 'Evaluación IA'
        verbose_name_plural = 'Evaluaciones IA'
        ordering = ['-generated_at']

    def __str__(self):
        return f'Evaluación {self.candidate} — {self.generated_at:%d/%m/%Y}'
