from django.contrib import admin

from .models import CandidateCaseStudy, CaseStudy


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'ai_generated', 'deadline_days', 'created_at')
    list_filter = ('ai_generated',)
    search_fields = ('title', 'position__title')


@admin.register(CandidateCaseStudy)
class CandidateCaseStudyAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'case_study', 'sent_at', 'submitted_at', 'score')
    list_filter = ('score',)
    search_fields = ('candidate__first_name', 'candidate__last_name')
