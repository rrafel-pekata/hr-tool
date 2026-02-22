from django import forms

from .models import CaseStudy

INPUT_CLASS = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none'


class CaseStudyForm(forms.ModelForm):
    class Meta:
        model = CaseStudy
        fields = ['title', 'brief_description', 'full_content', 'deadline_days', 'evaluation_criteria']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Título del case study'}),
            'brief_description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Descripción breve / briefing para IA...'}),
            'full_content': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 12, 'placeholder': 'Contenido completo del case study...'}),
            'deadline_days': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 30}),
            'evaluation_criteria': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Criterios de evaluación para la IA...'}),
        }
