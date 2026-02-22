from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('companies/', include('apps.tenants.urls')),
    path('positions/', include('apps.positions.urls')),
    path('candidates/', include('apps.candidates.urls')),
    path('interviews/', include('apps.interviews.urls')),
    path('casestudies/', include('apps.casestudies.urls')),
    path('evaluations/', include('apps.evaluations.urls')),
    path('portal/', include('apps.portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
