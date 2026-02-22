from apps.notifications.models import Notification


def unread_notification_count(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {}
    company = getattr(request, 'company', None)
    if not company:
        return {}
    count = Notification.objects.filter(
        user=request.user,
        company=company,
        is_read=False,
    ).count()
    return {'unread_notification_count': count}
