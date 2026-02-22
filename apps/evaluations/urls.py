from django.urls import path

from . import views

app_name = 'evaluations'

urlpatterns = [
    path('candidate/<uuid:candidate_pk>/', views.evaluate_candidate, name='evaluate_candidate'),
]
