from django import forms

from .models import Position

INPUT_CLASS = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none'
SELECT_CLASS = INPUT_CLASS


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = [
            'title', 'department', 'location', 'employment_type',
            'description', 'requirements', 'benefits', 'about_company_snippet',
            'salary_range', 'has_case_study',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Senior Backend Developer'}),
            'department': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Ingeniería'}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Remoto / Barcelona'}),
            'employment_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 8, 'placeholder': 'Descripción del puesto...'}),
            'requirements': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 6, 'placeholder': 'Requisitos del puesto...'}),
            'benefits': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Beneficios, ventajas, jornada, modalidad de trabajo...'}),
            'about_company_snippet': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Texto sobre la empresa para la oferta...'}),
            'salary_range': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: 40.000€ - 55.000€'}),
            'has_case_study': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'}),
        }
