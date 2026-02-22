from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        CANDIDATE_NEW = 'candidate_new', 'Nuevo candidato'
        STATUS_CHANGE = 'status_change', 'Cambio de estado'
        INTERVIEW = 'interview', 'Entrevista'
        CASE_STUDY = 'case_study', 'Caso práctico'
        EVALUATION = 'evaluation', 'Evaluación'
        POSITION = 'position', 'Posición'
        INFO = 'info', 'Información'
        SYSTEM = 'system', 'Sistema'

    company = models.ForeignKey(
        'tenants.Company',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Empresa',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario',
    )
    notification_type = models.CharField(
        'Tipo',
        max_length=30,
        choices=Type.choices,
        default=Type.INFO,
    )
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    link = models.CharField('Enlace', max_length=500, blank=True)
    is_read = models.BooleanField('Leída', default=False)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['user', 'is_read', '-created_at'],
                name='notif_user_read_created',
            ),
        ]

    def __str__(self):
        return f'{self.title} → {self.user}'
