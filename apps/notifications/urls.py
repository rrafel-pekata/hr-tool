from django.urls import path

from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('count/', views.notification_count, name='count'),
    path('<uuid:pk>/read/', views.notification_mark_read, name='mark_read'),
    path('read-all/', views.notification_mark_all_read, name='mark_all_read'),
]
