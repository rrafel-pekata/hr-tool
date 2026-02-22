from django.contrib import admin

from .models import AIEvaluation


@admin.register(AIEvaluation)
class AIEvaluationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'generated_at', 'overall_score', 'recommendation')
    list_filter = ('recommendation',)
    search_fields = ('candidate__first_name', 'candidate__last_name')
