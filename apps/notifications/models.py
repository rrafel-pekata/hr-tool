from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        CANDIDATE_NEW = 'candidate_new', _('Nuevo candidato')
        STATUS_CHANGE = 'status_change', _('Cambio de estado')
        INTERVIEW = 'interview', _('Entrevista')
        CASE_STUDY = 'case_study', _('Caso práctico')
        EVALUATION = 'evaluation', _('Evaluación')
        POSITION = 'position', _('Posición')
        INFO = 'info', _('Información')
        SYSTEM = 'system', _('Sistema')

    company = models.ForeignKey(
        'tenants.Company',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Empresa'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Destinatario'),
    )
    notification_type = models.CharField(
        _('Tipo'),
        max_length=30,
        choices=Type.choices,
        default=Type.INFO,
    )
    title = models.CharField(_('Título'), max_length=200)
    message = models.TextField(_('Mensaje'))
    link = models.CharField(_('Enlace'), max_length=500, blank=True)
    is_read = models.BooleanField(_('Leída'), default=False)

    class Meta:
        verbose_name = _('Notificación')
        verbose_name_plural = _('Notificaciones')
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['user', 'is_read', '-created_at'],
                name='notif_user_read_created',
            ),
        ]

    def __str__(self):
        return f'{self.title} → {self.user}'
