from django.urls import path
from .views import (
    CyclePredictionView,
    SignupView,
    SaveCycleView,
    UserCyclesView,
    SymptomCreateView,
    ReportsView,
)

urlpatterns = [
    # =========================
    # AI Prediction
    # =========================
    path(
        "predict/",
        CyclePredictionView.as_view(),
        name="cycle-predict",
    ),

    # =========================
    # User Signup
    # =========================
    path(
        "signup/",
        SignupView.as_view(),
        name="signup",
    ),

    # =========================
    # Cycle Management
    # =========================
    path(
        "cycles/save/",
        SaveCycleView.as_view(),
        name="save-cycle",
    ),
    path(
        "cycles/",
        UserCyclesView.as_view(),
        name="user-cycles",
    ),

    # =========================
    # Reports (Cycle + Symptoms)
    # =========================
    path(
        "reports/",
        ReportsView.as_view(),
        name="user-reports",
    ),

    # =========================
    # Symptoms
    # =========================
    path(
        "symptoms/",
        SymptomCreateView.as_view(),
        name="create-symptom",
    ),
]
