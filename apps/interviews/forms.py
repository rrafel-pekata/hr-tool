from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Interview

INPUT_CLASS = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none'


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'scheduled_at', 'duration_minutes', 'interviewer',
            'location_or_link', 'notes',
        ]
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 15, 'step': 15}),
            'interviewer': forms.Select(attrs={'class': INPUT_CLASS}),
            'location_or_link': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Lugar o link de videollamada')}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Notas previas...')}),
        }


class InterviewNotesForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['status', 'notes', 'strengths', 'weaknesses', 'overall_score']
        widgets = {
            'status': forms.Select(attrs={'class': INPUT_CLASS}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': _('Notas de la entrevista...')}),
            'strengths': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Puntos fuertes observados...')}),
            'weaknesses': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Puntos débiles observados...')}),
            'overall_score': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 10}),
        }
