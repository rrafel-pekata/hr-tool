import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Modelo base abstracto con UUID como PK y timestamps automáticos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager que excluye registros con deleted_at no nulo."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteMixin(models.Model):
    """Mixin para soft-delete: campo deleted_at + métodos soft_delete/restore."""
    deleted_at = models.DateTimeField('Eliminado en', null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
