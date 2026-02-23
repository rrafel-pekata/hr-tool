from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('ayuda/', views.help_page, name='help'),
    path('select-company/', views.select_company, name='select_company'),
    path('switch-company/', views.switch_company, name='switch_company'),
]
