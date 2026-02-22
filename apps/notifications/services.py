from apps.notifications.models import Notification
from apps.tenants.models import UserProfile


def notify_user(user, company, title, message, link='', notification_type='info'):
    """Crea una notificación para un usuario."""
    return Notification.objects.create(
        user=user,
        company=company,
        title=title,
        message=message,
        link=link,
        notification_type=notification_type,
    )


def notify_admins(company, title, message, link='', notification_type='info'):
    """Crea una notificación para todos los admins de la empresa."""
    admin_profiles = UserProfile.objects.filter(
        company=company,
        role=UserProfile.Role.ADMIN,
    ).select_related('user')

    notifications = [
        Notification(
            user=profile.user,
            company=company,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type,
        )
        for profile in admin_profiles
    ]
    return Notification.objects.bulk_create(notifications)


def notify_company(company, title, message, link='', notification_type='info', exclude_user=None):
    """Crea una notificación para todos los miembros de la empresa, opcionalmente excluyendo a un usuario."""
    profiles = UserProfile.objects.filter(company=company).select_related('user')

    notifications = [
        Notification(
            user=profile.user,
            company=company,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type,
        )
        for profile in profiles
        if profile.user != exclude_user
    ]
    return Notification.objects.bulk_create(notifications)
