from django.urls import path
from .views import chat_page, process_message

urlpatterns = [
    path('', chat_page, name='chat_page_url'),
    path('chatbot/', process_message, name='process_message'),
]