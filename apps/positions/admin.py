from django.contrib import admin

from .models import Position


@admin.action(description='Restaurar seleccionados')
def restore_selected(modeladmin, request, queryset):
    queryset.update(deleted_at=None)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'department', 'status', 'employment_type', 'deleted_at', 'created_at')
    list_filter = ('status', 'employment_type', 'company', 'deleted_at')
    search_fields = ('title', 'department', 'company__name')
    actions = [restore_selected]

    def get_queryset(self, request):
        return Position.all_objects.all()
