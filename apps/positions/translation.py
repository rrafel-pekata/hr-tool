from modeltranslation.translator import TranslationOptions, register

from .models import Position


@register(Position)
class PositionTranslationOptions(TranslationOptions):
    fields = (
        'title', 'description', 'requirements',
        'about_company_snippet', 'benefits', 'salary_range',
    )
