from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('case/<uuid:token>/', views.portal_case_study, name='portal_case_study'),
]
