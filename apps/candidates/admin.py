from django.contrib import admin

from .models import Candidate


@admin.action(description='Restaurar seleccionados')
def restore_selected(modeladmin, request, queryset):
    queryset.update(deleted_at=None)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'position', 'status', 'source', 'rating', 'deleted_at', 'created_at')
    list_filter = ('status', 'source', 'position__company', 'deleted_at')
    search_fields = ('first_name', 'last_name', 'email')
    actions = [restore_selected]

    def get_queryset(self, request):
        return Candidate.all_objects.all()
