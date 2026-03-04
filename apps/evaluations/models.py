from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel


class AIEvaluation(TimeStampedModel):
    """Evaluación final generada por IA para un candidato."""

    class Recommendation(models.TextChoices):
        HIRE = 'hire', _('Contratar')
        HOLD = 'hold', _('En espera')
        REJECT = 'reject', _('Rechazar')

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name=_('Candidato'),
    )
    generated_at = models.DateTimeField(_('Fecha de generación'), auto_now_add=True)
    prompt_used = models.TextField(_('Prompt enviado'))
    result = models.TextField(_('Respuesta completa de Claude'))
    cv_score = models.IntegerField(_('Puntuación CV'), null=True, blank=True)
    interview_score = models.IntegerField(
        _('Puntuación entrevista'),
        null=True,
        blank=True,
    )
    case_score = models.IntegerField(
        _('Puntuación case study'),
        null=True,
        blank=True,
    )
    overall_score = models.IntegerField(
        _('Puntuación final'),
        null=True,
        blank=True,
    )
    recommendation = models.CharField(
        _('Recomendación'),
        max_length=10,
        choices=Recommendation.choices,
        blank=True,
    )
    summary = models.TextField(_('Resumen ejecutivo'), blank=True)
    strengths = models.JSONField(_('Puntos fuertes'), default=list, blank=True)
    weaknesses = models.JSONField(_('Puntos débiles'), default=list, blank=True)

    class Meta:
        verbose_name = _('Evaluación IA')
        verbose_name_plural = _('Evaluaciones IA')
        ordering = ['-generated_at']

    def __str__(self):
        return f'Evaluación {self.candidate} — {self.generated_at:%d/%m/%Y}'
