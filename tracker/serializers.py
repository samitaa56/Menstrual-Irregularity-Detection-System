from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cycle, Symptom

# ======================================================
# AI Prediction Input Serializer (for /api/predict/)
# ======================================================
class CyclePredictionInputSerializer(serializers.Serializer):
    age = serializers.IntegerField(required=True, min_value=10, max_value=60)
    bmi = serializers.FloatField(required=True, min_value=10, max_value=50)
    life_stage = serializers.CharField(required=True)
    tracking_duration = serializers.IntegerField(required=True, min_value=1)
    pain_score = serializers.IntegerField(required=True, min_value=0, max_value=10)
    cycle_lengths = serializers.ListField(
        child=serializers.IntegerField(min_value=15, max_value=60),
        min_length=2,
        required=True
    )
    avg_bleeding_days = serializers.IntegerField(required=True, min_value=1, max_value=10)
    bleeding_volume_score = serializers.IntegerField(required=True, min_value=1, max_value=10)
    # Optional field
    intermenstrual_episodes = serializers.IntegerField(required=False, min_value=0, max_value=10)

    # Auto-calculated fields
    avg_cycle_length = serializers.IntegerField(read_only=True)
    cycle_length_variation = serializers.IntegerField(read_only=True)
    cycle_variation_coefficient = serializers.FloatField(read_only=True)
    pattern_disruption_score = serializers.IntegerField(read_only=True)


# ======================================================
# Signup Serializer
# ======================================================
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# ======================================================
# Save Cycle Serializer (DB Storage)
# ======================================================
class SaveCycleSerializer(serializers.ModelSerializer):
    # predictions from ML model may sometimes be absent, so make field optional
    next_cycle_prediction = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Cycle
        fields = (
            # User inputs
            "age", "bmi", "life_stage", "tracking_duration", "pain_score",
            # Calculated metrics
            "avg_cycle_length", "cycle_length_variation", "cycle_variation_coefficient", "pattern_disruption_score",
            # Bleeding data
            "avg_bleeding_days", "bleeding_volume_score",
            # AI outputs
            "irregularity_prediction", "irregularity_probability", "irregularity_type",
            "next_cycle_prediction",
        )

    # Validations
    def validate_next_cycle_prediction(self, value):
        # gracefully handle null/None
        if value is None:
            return None
        if isinstance(value, list):
            value = value[0]
        return int(round(value))

    def validate_avg_bleeding_days(self, value):
        if value > 10:
            raise serializers.ValidationError("Average bleeding days cannot exceed 10")
        return value


# ======================================================
# Cycle List Serializer (Dropdown / Selector)
# ======================================================
class CycleListSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = Cycle
        fields = ("id", "label", "created_date")

    def get_label(self, obj):
        return f"Cycle {obj.id} – {obj.created_at.date()}"

    def get_created_date(self, obj):
        return obj.created_at.date()


# ======================================================
# Symptom Serializer
# ======================================================
class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ("id", "cycle", "date", "symptom_name", "severity")
        read_only_fields = ("id",)


# ======================================================
# Reports
# ======================================================
class SymptomReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ("symptom_name", "severity", "date")


class CycleReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    symptoms = SymptomReportSerializer(many=True, read_only=True)

    class Meta:
        model = Cycle
        fields = (
            "id", "username", "created_at", "age", "bmi", "life_stage",
            "tracking_duration", "pain_score", "avg_cycle_length", "cycle_length_variation",
            "avg_bleeding_days", "bleeding_volume_score", "cycle_variation_coefficient",
            "pattern_disruption_score",
            "irregularity_prediction", "irregularity_probability", "irregularity_type",
            "symptoms",
        )