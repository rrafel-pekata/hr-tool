from django import template
from django.utils.safestring import mark_safe

register = template.Library()

STATUS_COLORS = {
    'new': ('Nuevo', 'blue'),
    'reviewing': ('En revisión', 'indigo'),
    'phone_screen': ('Phone screen', 'purple'),
    'interview_scheduled': ('Entrevista prog.', 'yellow'),
    'interview_done': ('Entrevista hecha', 'yellow'),
    'case_sent': ('Case enviado', 'purple'),
    'case_submitted': ('Case entregado', 'indigo'),
    'evaluation': ('En evaluación', 'blue'),
    'offer_sent': ('Oferta enviada', 'green'),
    'hired': ('Contratado', 'green'),
    'rejected': ('Descartado', 'red'),
    'withdrawn': ('Retirado', 'gray'),
}

COLOR_CLASSES = {
    'green': 'bg-green-100 text-green-800',
    'yellow': 'bg-yellow-100 text-yellow-800',
    'red': 'bg-red-100 text-red-800',
    'blue': 'bg-blue-100 text-blue-800',
    'indigo': 'bg-indigo-100 text-indigo-800',
    'purple': 'bg-purple-100 text-purple-800',
    'gray': 'bg-gray-100 text-gray-800',
}


@register.simple_tag
def candidate_status_badge(status):
    label, color = STATUS_COLORS.get(status, (status, 'gray'))
    css = COLOR_CLASSES.get(color, COLOR_CLASSES['gray'])
    return mark_safe(
        f'<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {css}">{label}</span>'
    )
