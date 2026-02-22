from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.notifications.models import Notification


@login_required
def notification_list(request):
    """Devuelve las 20 notificaciones más recientes del usuario (JSON)."""
    qs = Notification.objects.filter(
        user=request.user,
        company=request.company,
    )[:20]

    data = [
        {
            'id': str(n.id),
            'type': n.notification_type,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        }
        for n in qs
    ]
    return JsonResponse({'notifications': data})


@login_required
def notification_count(request):
    """Devuelve el número de notificaciones no leídas (JSON)."""
    count = Notification.objects.filter(
        user=request.user,
        company=request.company,
        is_read=False,
    ).count()
    return JsonResponse({'count': count})


@login_required
@require_POST
def notification_mark_read(request, pk):
    """Marca una notificación como leída."""
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
        company=request.company,
    )
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def notification_mark_all_read(request):
    """Marca todas las notificaciones del usuario como leídas."""
    Notification.objects.filter(
        user=request.user,
        company=request.company,
        is_read=False,
    ).update(is_read=True)
    return JsonResponse({'ok': True})
