from django.contrib import admin # type: ignore
from .models import Cycle, Symptom, PendingUser # type: ignore


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "irregularity_prediction",
        "irregularity_type",          # 🔥 ADD THIS
        "irregularity_probability",
        "next_cycle_prediction",
        "created_at",
    )

    list_filter = (
        "irregularity_prediction",
        "irregularity_type",          # 🔥 ADD FILTER
        "created_at",
    )

    search_fields = (
        "user__username",
        "irregularity_type",          # 🔥 SEARCH BY TYPE
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Hide history-only cycles from the admin list to avoid confusion
        from django.db.models import Q # type: ignore
        return qs.exclude(
            Q(irregularity_prediction__isnull=True) & 
            Q(irregularity_probability__isnull=True) & 
            Q(age__isnull=True)
        )


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = (
        "cycle",
        "symptom_name",
        "severity",
        "created_at",
    )

    list_filter = (
        "severity",
        "created_at",
    )

    search_fields = (
        "symptom_name",
    )

    ordering = (
        "-created_at",
    )
@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "verification_token", "expires_at", "created_at")
    search_fields = ("username", "email", "verification_token")
    ordering = ("-created_at",)
