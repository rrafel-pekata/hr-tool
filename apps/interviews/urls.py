from django.urls import path

from . import views

app_name = 'interviews'

urlpatterns = [
    path('new/<uuid:candidate_pk>/', views.interview_create, name='interview_create'),
    path('<uuid:pk>/edit/', views.interview_edit, name='interview_edit'),
]
