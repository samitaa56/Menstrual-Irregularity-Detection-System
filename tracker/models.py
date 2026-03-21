from django.db import models
from django.contrib.auth.models import User


# =========================
# Cycle Model
# =========================
class Cycle(models.Model):

    IRREGULARITY_CHOICES = (
        ("Regular", "Regular"),
        ("Irregular", "Irregular"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cycles"
    )

    # ---------- User Input Fields ----------
    age = models.IntegerField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    life_stage = models.CharField(max_length=30, null=True, blank=True)
    tracking_duration = models.IntegerField(null=True, blank=True)
    pain_score = models.IntegerField(null=True, blank=True)
    avg_cycle_length = models.IntegerField(null=True, blank=True)
    cycle_length_variation = models.IntegerField(null=True, blank=True)
    avg_bleeding_days = models.IntegerField(null=True, blank=True)
    bleeding_volume_score = models.IntegerField(null=True, blank=True)
    cycle_variation_coefficient = models.FloatField(null=True, blank=True)
    pattern_disruption_score = models.IntegerField(null=True, blank=True)

    # ---------- AI Prediction Outputs ----------
    irregularity_prediction = models.CharField(
        max_length=20,
        choices=IRREGULARITY_CHOICES
    )
    irregularity_probability = models.FloatField()
    irregularity_type = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    next_cycle_prediction = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} | "
            f"{self.irregularity_prediction} | "
            f"{self.irregularity_type} | "
            f"{self.next_cycle_prediction} days"
        )


# =========================
# Symptom Model
# =========================
class Symptom(models.Model):

    SEVERITY_CHOICES = [
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
    ]

    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.CASCADE,
        related_name="symptoms"
    )

    date = models.DateField()
    symptom_name = models.CharField(max_length=100)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="mild"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symptom_name} - Cycle {self.cycle.id}"