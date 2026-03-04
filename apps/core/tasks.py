import logging

from celery import shared_task
from django.apps import apps

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def translate_instance_fields(self, app_label, model_name, pk, source_lang, fields):
    """Celery task: translate model fields asynchronously.

    Args:
        app_label: e.g. 'positions'
        model_name: e.g. 'Position'
        pk: primary key of the instance
        source_lang: language code of the source content
        fields: list of field names to translate
    """
    from apps.core.services import translate_fields

    try:
        Model = apps.get_model(app_label, model_name)
        instance = Model.objects.get(pk=pk)
        translate_fields(instance, source_lang, fields)
    except Exception as exc:
        logger.exception(
            "translate_instance_fields failed for %s.%s pk=%s",
            app_label, model_name, pk,
        )
        raise self.retry(exc=exc)
