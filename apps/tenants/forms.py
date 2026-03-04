from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Company, Department

INPUT_CLASS = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'slug', 'description', 'logo', 'website',
            'benefits', 'work_schedule', 'remote_policy', 'office_location', 'culture',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Nombre de la empresa')}),
            'slug': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('slug-de-la-empresa')}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Qué hace la empresa, sector, misión...')}),
            'website': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://ejemplo.com'}),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            }),
            'benefits': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Seguro médico, formación, fruta en la oficina, gym...')}),
            'work_schedule': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Ej: L-V 9:00-18:00, jornada flexible...')}),
            'remote_policy': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Ej: Híbrido 2 días oficina, 100% remoto...')}),
            'office_location': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Ej: Calle Mayor 10, Barcelona')}),
            'culture': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Valores de la empresa, ambiente de trabajo...')}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': _('Ej: Ingeniería')}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': _('Descripción del departamento...')}),
        }
