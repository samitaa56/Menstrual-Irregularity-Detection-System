from django.db import models  # type: ignore
from django.contrib.auth.models import User  # type: ignore


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
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)

    life_stage = models.CharField(max_length=30, null=True, blank=True)

    tracking_duration = models.IntegerField(null=True, blank=True)
    pain_score = models.IntegerField(null=True, blank=True)

    avg_cycle_length = models.IntegerField(null=True, blank=True)
    cycle_length_variation = models.IntegerField(null=True, blank=True)

    avg_bleeding_days = models.IntegerField(null=True, blank=True)
    bleeding_volume_score = models.IntegerField(null=True, blank=True)

    intermenstrual_episodes = models.IntegerField(null=True, blank=True)
    missed_periods = models.IntegerField(null=True, blank=True)
    cycle_variation_coefficient = models.FloatField(null=True, blank=True)

    pattern_disruption_score = models.IntegerField(null=True, blank=True)

    # ---------- AI Prediction Outputs ----------
    # ✅ IMPORTANT FIX:
    # These must be optional because AddCycleHistory saves ONLY avg_cycle_length history.
    irregularity_prediction = models.CharField(
        "Prediction Status",
        max_length=20,
        choices=IRREGULARITY_CHOICES,
        null=True,
        blank=True
    )

    irregularity_probability = models.FloatField(
        "Chance of Irregularity",
        null=True,
        blank=True
    )

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
        # Safer string (won't break when prediction fields are empty)
        return f"{self.user.username} | cycle={self.avg_cycle_length} | next={self.next_cycle_prediction}"


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


# =========================
# Pending User (Unverified Signup)
# =========================
class PendingUser(models.Model):
    """
    ✅ Store unverified signup data
    User moved to User model ONLY after email verification
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Hashed
    verification_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Token expires after 24 hours

    def __str__(self):
        return f"Pending: {self.username} ({self.email})"
