from django.urls import path

from . import views

app_name = 'candidates'

urlpatterns = [
    path('analyze-cv/<uuid:position_pk>/', views.analyze_cv, name='analyze_cv'),
    path('bulk-upload/<uuid:position_pk>/', views.bulk_upload_cvs, name='bulk_upload_cvs'),
    path('new/<uuid:position_pk>/', views.candidate_create, name='candidate_create'),
    path('<uuid:pk>/', views.candidate_detail, name='candidate_detail'),
    path('<uuid:pk>/edit/', views.candidate_edit, name='candidate_edit'),
    path('<uuid:pk>/status/', views.candidate_status, name='candidate_status'),
    path('<uuid:pk>/notes/', views.candidate_notes, name='candidate_notes'),
    path('<uuid:pk>/rating/', views.candidate_rating, name='candidate_rating'),
    path('<uuid:pk>/upload-cv/', views.candidate_upload_cv, name='candidate_upload_cv'),
    path('<uuid:pk>/cv-preview/', views.candidate_cv_preview, name='candidate_cv_preview'),
]
