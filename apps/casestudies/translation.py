from modeltranslation.translator import TranslationOptions, register

from .models import CaseStudy


@register(CaseStudy)
class CaseStudyTranslationOptions(TranslationOptions):
    fields = (
        'title', 'brief_description', 'full_content',
        'evaluation_criteria',
    )
