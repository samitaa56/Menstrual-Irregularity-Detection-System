from django.urls import path
from .views import (
    CyclePredictionView,
    SignupView,
    VerifyEmailView,
    SaveCycleView,
    UserCyclesView,
    SaveCycleHistoryView,
    ReportsView,
    SymptomCreateView,
    DevQuickVerifyView,
)

urlpatterns = [
    # =========================
    # Auth / Signup
    # =========================
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify-email"),
    path("dev-verify/", DevQuickVerifyView.as_view(), name="dev-verify"),  # 🔴 Development only

    # =========================
    # Prediction
    # =========================
    path("predict/", CyclePredictionView.as_view(), name="cycle-predict"),

    # =========================
    # Cycles
    # =========================
    path("cycles/history/", SaveCycleHistoryView.as_view(), name="save-cycle-history"),
    path("cycles/save/", SaveCycleView.as_view(), name="save-cycle"),
    path("cycles/", UserCyclesView.as_view(), name="user-cycles"),

    # =========================
    # Reports
    # =========================
    path("reports/", ReportsView.as_view(), name="user-reports"),

    # =========================
    # Symptoms
    # =========================
    path("symptoms/", SymptomCreateView.as_view(), name="create-symptom"),
]
