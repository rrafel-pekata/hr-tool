from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('companies/', include('apps.tenants.urls')),
    path('positions/', include('apps.positions.urls')),
    path('candidates/', include('apps.candidates.urls')),
    path('interviews/', include('apps.interviews.urls')),
    path('casestudies/', include('apps.casestudies.urls')),
    path('evaluations/', include('apps.evaluations.urls')),
    path('portal/', include('apps.portal.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

# Serve media from local disk when S3 is not configured
if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
