# backend_project/urls.py

from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # type: ignore
from backend_project.chatbot import views # type: ignore

urlpatterns = [
    # =========================
    # Django Admin
    # =========================
    path("admin/", admin.site.urls),

    # =========================
    # JWT Authentication
    # =========================
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # =========================
    # Tracker App APIs
    # =========================
    path("api/", include("tracker.urls")),

    # =========================
    # Chatbot API
    # =========================
    path("api/chatbot_response/", views.chatbot_response, name="chatbot_response"),
]