import os

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve


@csrf_exempt
def upload_media(request):
    """Upload media files via POST with token auth. Used to sync local media to production."""
    token = settings.MEDIA_UPLOAD_TOKEN
    if not token or request.headers.get('Authorization') != f'Bearer {token}':
        return HttpResponse('Unauthorized', status=401)
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    f = request.FILES.get('file')
    upload_path = request.POST.get('path', '')
    if not f or not upload_path:
        return JsonResponse({'error': 'file and path required'}, status=400)
    full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return JsonResponse({'ok': True, 'path': upload_path})

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
    path('api/upload-media/', upload_media, name='upload_media'),
]

# Serve media from local disk when S3 is not configured
if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
