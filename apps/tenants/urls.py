from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('create/', views.company_create, name='company_create'),
    path('<uuid:pk>/', views.company_detail, name='company_detail'),
    path('<uuid:pk>/edit/', views.company_edit, name='company_edit'),
    path('<uuid:pk>/toggle/', views.company_toggle_active, name='company_toggle_active'),
]
