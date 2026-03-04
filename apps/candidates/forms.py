from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Candidate

INPUT_CLASS = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none'


class CandidateCreateForm(forms.ModelForm):
    """Formulario de creación: datos básicos + CV."""
    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'linkedin_url', 'cv_file', 'source',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Nombre')}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Apellidos')}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': _('email@ejemplo.com')}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('+34 600 000 000')}),
            'linkedin_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://linkedin.com/in/...'}),
            'cv_file': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': '.pdf',
            }),
            'source': forms.Select(attrs={'class': INPUT_CLASS}),
        }


class CandidateEditForm(forms.ModelForm):
    """Formulario de edición: datos personales + notas."""
    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'linkedin_url', 'recruiter_notes', 'rating',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'linkedin_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
            'recruiter_notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': _('Notas rápidas sobre el candidato...')}),
            'rating': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 5}),
        }
