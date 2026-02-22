from django.contrib import admin

from .models import Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'department', 'status', 'employment_type', 'created_at')
    list_filter = ('status', 'employment_type', 'company')
    search_fields = ('title', 'department', 'company__name')
