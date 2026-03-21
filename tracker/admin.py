from django.contrib import admin
from .models import Cycle, Symptom


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
