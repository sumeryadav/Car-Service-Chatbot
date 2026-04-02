from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.chatbot_view, name="chatbot_view"),   # old flow
    path("chatbot/api/", views.chatbot_api, name="chatbot_api"),
    path("chat-page/", views.chat_page, name="chat_page"),
  
]
