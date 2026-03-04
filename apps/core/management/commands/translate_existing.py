"""Translate all existing translatable content using AI.

Usage:
    python manage.py translate_existing
    python manage.py translate_existing --model Position
    python manage.py translate_existing --source es
"""
from django.core.management.base import BaseCommand

from apps.core.services import translate_fields


MODEL_CONFIGS = {
    'Company': {
        'app': 'tenants',
        'fields': ['name', 'description', 'benefits', 'work_schedule',
                    'remote_policy', 'office_location', 'culture'],
    },
    'Department': {
        'app': 'tenants',
        'fields': ['name', 'description'],
    },
    'Position': {
        'app': 'positions',
        'fields': ['title', 'description', 'requirements',
                    'about_company_snippet', 'benefits', 'salary_range'],
    },
    'CaseStudy': {
        'app': 'casestudies',
        'fields': ['title', 'brief_description', 'full_content',
                    'evaluation_criteria'],
    },
}


class Command(BaseCommand):
    help = 'Translate all existing content to all languages using AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model', type=str, default='',
            help='Only translate a specific model (e.g. Position, Company)',
        )
        parser.add_argument(
            '--source', type=str, default='es',
            help='Source language code (default: es)',
        )

    def handle(self, *args, **options):
        from django.apps import apps

        source_lang = options['source']
        filter_model = options['model']

        for model_name, config in MODEL_CONFIGS.items():
            if filter_model and model_name != filter_model:
                continue

            Model = apps.get_model(config['app'], model_name)
            instances = Model.objects.all()
            total = instances.count()
            self.stdout.write(f'\nTranslating {total} {model_name} instances...')

            for i, instance in enumerate(instances, 1):
                self.stdout.write(f'  [{i}/{total}] {instance}... ', ending='')
                try:
                    translate_fields(instance, source_lang, config['fields'])
                    self.stdout.write(self.style.SUCCESS('OK'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'ERROR: {e}'))

        self.stdout.write(self.style.SUCCESS('\nDone!'))
