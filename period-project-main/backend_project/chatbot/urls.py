from django.urls import path
from . import views 
from .views import ChatbotView


urlpatterns = [
        path("chat/", views.chatbot_response, name="chatbot_response"),
        path("api/chatbot_response/", views.chatbot_response, name="chatbot_response"),

]