from django.contrib import admin

from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'interviewer', 'scheduled_at', 'status', 'overall_score')
    list_filter = ('status',)
    search_fields = ('candidate__first_name', 'candidate__last_name')
