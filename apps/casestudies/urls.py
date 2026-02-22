from django.urls import path

from . import views

app_name = 'casestudies'

urlpatterns = [
    path('create/<uuid:position_pk>/', views.casestudy_create, name='casestudy_create'),
    path('generate/<uuid:candidate_pk>/', views.casestudy_generate, name='casestudy_generate'),
    path('detail/<uuid:ccs_pk>/', views.casestudy_detail, name='casestudy_detail'),
    path('edit/<uuid:ccs_pk>/', views.casestudy_edit, name='casestudy_edit'),
    path('resend/<uuid:ccs_pk>/', views.casestudy_resend, name='casestudy_resend'),
    path('ai/generate/<uuid:candidate_pk>/', views.casestudy_ai_generate, name='casestudy_ai_generate'),
    path('send/<uuid:candidate_pk>/', views.casestudy_send, name='casestudy_send'),
]
