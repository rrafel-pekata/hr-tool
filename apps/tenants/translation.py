from modeltranslation.translator import TranslationOptions, register

from .models import Company, Department


@register(Company)
class CompanyTranslationOptions(TranslationOptions):
    fields = (
        'name', 'description', 'benefits', 'work_schedule',
        'remote_policy', 'office_location', 'culture',
    )


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
