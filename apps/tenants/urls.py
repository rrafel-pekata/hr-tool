from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('create/', views.company_create, name='company_create'),
    path('<uuid:pk>/', views.company_detail, name='company_detail'),
    path('<uuid:pk>/edit/', views.company_edit, name='company_edit'),
    path('<uuid:pk>/delete/', views.company_delete, name='company_delete'),
    path('<uuid:pk>/toggle/', views.company_toggle_active, name='company_toggle_active'),
    path('ai/improve/', views.company_ai_improve, name='company_ai_improve'),
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<uuid:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<uuid:pk>/delete/', views.department_delete, name='department_delete'),
]
