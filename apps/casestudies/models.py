from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel
from apps.positions.models import Position


class CaseStudy(TimeStampedModel):
    """Case Study asociado a una posición."""
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='case_studies',
        verbose_name=_('Posición'),
    )
    title = models.CharField(_('Título'), max_length=200)
    brief_description = models.TextField(_('Descripción breve'))
    full_content = models.TextField(_('Contenido completo'), blank=True)
    ai_generated = models.BooleanField(_('Generado con IA'), default=False)
    deadline_days = models.IntegerField(_('Días para entrega'), default=7)
    evaluation_criteria = models.TextField(_('Criterios de evaluación'), blank=True)

    class Meta:
        verbose_name = _('Case Study')
        verbose_name_plural = _('Case Studies')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.position.title}'


class CandidateCaseStudy(TimeStampedModel):
    """Envío de case study a un candidato individual."""
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='case_studies',
        verbose_name=_('Candidato'),
    )
    case_study = models.ForeignKey(
        CaseStudy,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name=_('Case Study'),
    )
    sent_at = models.DateTimeField(_('Fecha de envío'), null=True, blank=True)
    deadline = models.DateTimeField(_('Fecha límite'), null=True, blank=True)
    submitted_at = models.DateTimeField(_('Fecha de entrega'), null=True, blank=True)
    submission_file = models.FileField(
        _('Archivo de respuesta'),
        upload_to='casestudies/submissions/',
        blank=True,
    )
    submission_text = models.TextField(_('Texto extraído'), blank=True)
    submission_notes = models.TextField(_('Notas del candidato'), blank=True)
    evaluator_notes = models.TextField(_('Notas del evaluador'), blank=True)
    ai_evaluation = models.TextField(_('Evaluación IA'), blank=True)
    score = models.IntegerField(_('Puntuación'), null=True, blank=True)

    class Meta:
        verbose_name = _('Case Study del candidato')
        verbose_name_plural = _('Case Studies de candidatos')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.candidate} — {self.case_study.title}'

    @property
    def is_submitted(self):
        return self.submitted_at is not None

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.deadline and not self.is_submitted:
            return timezone.now() > self.deadline
        return False
