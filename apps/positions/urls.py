from django.urls import path

from . import views

app_name = 'positions'

urlpatterns = [
    path('', views.position_list, name='position_list'),
    path('create/', views.position_create, name='position_create'),
    path('<uuid:pk>/', views.position_detail, name='position_detail'),
    path('<uuid:pk>/edit/', views.position_edit, name='position_edit'),
    path('<uuid:pk>/delete/', views.position_delete, name='position_delete'),
    path('<uuid:pk>/status/', views.position_status, name='position_status'),
    path('ai/generate/', views.position_ai_generate, name='position_ai_generate'),
]
