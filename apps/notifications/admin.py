from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'company', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'company')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
