from django.urls import path

from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/', views.chatbot_message, name='message'),
    path('clear/', views.chatbot_clear, name='clear'),
]
