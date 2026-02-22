from django.db import models

from apps.candidates.models import Candidate
from apps.core.models import TimeStampedModel
from apps.positions.models import Position


class CaseStudy(TimeStampedModel):
    """Case Study asociado a una posición."""
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='case_studies',
        verbose_name='Posición',
    )
    title = models.CharField('Título', max_length=200)
    brief_description = models.TextField('Descripción breve')
    full_content = models.TextField('Contenido completo', blank=True)
    ai_generated = models.BooleanField('Generado con IA', default=False)
    deadline_days = models.IntegerField('Días para entrega', default=7)
    evaluation_criteria = models.TextField('Criterios de evaluación', blank=True)

    class Meta:
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.position.title}'


class CandidateCaseStudy(TimeStampedModel):
    """Envío de case study a un candidato individual."""
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='case_studies',
        verbose_name='Candidato',
    )
    case_study = models.ForeignKey(
        CaseStudy,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Case Study',
    )
    sent_at = models.DateTimeField('Fecha de envío', null=True, blank=True)
    deadline = models.DateTimeField('Fecha límite', null=True, blank=True)
    submitted_at = models.DateTimeField('Fecha de entrega', null=True, blank=True)
    submission_file = models.FileField(
        'Archivo de respuesta',
        upload_to='casestudies/submissions/',
        blank=True,
    )
    submission_text = models.TextField('Texto extraído', blank=True)
    submission_notes = models.TextField('Notas del candidato', blank=True)
    evaluator_notes = models.TextField('Notas del evaluador', blank=True)
    ai_evaluation = models.TextField('Evaluación IA', blank=True)
    score = models.IntegerField('Puntuación', null=True, blank=True)

    class Meta:
        verbose_name = 'Case Study del candidato'
        verbose_name_plural = 'Case Studies de candidatos'
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
