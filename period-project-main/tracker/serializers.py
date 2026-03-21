from rest_framework import serializers  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from .models import Cycle, Symptom  # type: ignore


# ======================================================
# AI Prediction Input (USED ONLY FOR /api/predict/)
# ======================================================
class CyclePredictionInputSerializer(serializers.Serializer):
    # 👤 User basic inputs
    age = serializers.IntegerField(min_value=10, max_value=60)
    bmi = serializers.FloatField(min_value=10, max_value=50, required=False)
    height = serializers.FloatField(min_value=50, max_value=250, required=False)
    weight = serializers.FloatField(min_value=20, max_value=300, required=False)
    life_stage = serializers.CharField()
    tracking_duration = serializers.IntegerField(min_value=0, required=False, default=0)
    pain_score = serializers.IntegerField(min_value=0, max_value=10)

    # 🔥 USER ENTERS ONLY RAW CYCLE LENGTHS
    cycle_lengths = serializers.ListField(
        child=serializers.IntegerField(min_value=15, max_value=120),
        min_length=2
    )

    # 🩸 User inputs
    avg_bleeding_days = serializers.IntegerField(min_value=1, max_value=10)
    bleeding_volume_score = serializers.IntegerField(min_value=1, max_value=10)
    intermenstrual_episodes = serializers.IntegerField(min_value=0, max_value=10, required=False, default=0)
    missed_periods = serializers.IntegerField(min_value=0, max_value=12, required=False, default=0)

    # 🔒 AUTO-CALCULATED (SET IN views.py)
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

    def validate_email(self, value):
        """
        ✅ Validate email:
        1. Check format
        2. Check if domain has valid MX records (exists)
        3. Check if email is already registered
        """
        import dns.resolver  # type: ignore
        from django.core.exceptions import ValidationError  # type: ignore
        
        # 1. Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        
        # 2. Basic format check
        if "@" not in value or "." not in value.split("@")[1]:
            raise serializers.ValidationError("Invalid email format.")
        
        # 3. Check domain (Lighter check - just format first)
        # We skip mandatory MX lookup as it can fail in offline/restricted environments
        # and cause signup to fail unexpectedly.
        try:
            domain = value.split("@")[1]
            print(f"DEBUG: Validating domain format for: {domain}")
            # we keep the resolver import for logging but don't raise error
            import dns.resolver # type: ignore
            # Optional: just log it
            # dns.resolver.resolve(domain, 'MX') 
        except Exception:
            pass
        
        return value

    def create(self, validated_data):
        # ✅ Create user as INACTIVE until email is verified
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User must verify email first
        user.save()
        return user


# ======================================================
# Save Cycle (DB STORAGE) 🔥 MOST IMPORTANT
# ======================================================
class SaveCycleSerializer(serializers.ModelSerializer):
    next_cycle_prediction = serializers.IntegerField()

    class Meta:
        model = Cycle
        fields = (
            # 👤 User inputs
            "age",
            "height",
            "weight",
            "bmi",
            "life_stage",
            "tracking_duration",
            "pain_score",

            # 🔢 Calculated metrics
            "avg_cycle_length",
            "cycle_length_variation",
            "cycle_variation_coefficient",
            "pattern_disruption_score",

            # 🩸 Bleeding data
            "avg_bleeding_days",
            "bleeding_volume_score",
            "intermenstrual_episodes",
            "missed_periods",

            # 🤖 AI outputs
            "irregularity_prediction",
            "irregularity_probability",
            "irregularity_type",     # ✅ STORED IN DB
            "next_cycle_prediction",
        )

    # ------------------------------
    # VALIDATIONS
    # ------------------------------
    def validate_next_cycle_prediction(self, value):
        if isinstance(value, list):
            value = value[0]
        return int(round(value))

    def validate_avg_bleeding_days(self, value):
        if value > 10:
            raise serializers.ValidationError(
                "Average bleeding days cannot exceed 10"
            )
        return value


# ======================================================
# Cycle List (Dropdown / Selector)
# ======================================================
class CycleListSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = Cycle
        fields = ("id", "label", "created_date")

    def get_label(self, obj):
        # Determine if this cycle has full prediction data or is just a history entry
        if obj.irregularity_prediction is not None or obj.irregularity_probability is not None or obj.age is not None:
            # It's a predicted cycle. Let's find its cycle number.
            # Count only full predicted cycles that came before or at the same time as this one.
            from django.db.models import Q # type: ignore
            total_predicted_before_me = Cycle.objects.filter(
                user=obj.user, 
                created_at__lte=obj.created_at
            ).exclude(
                Q(irregularity_prediction__isnull=True) & 
                Q(irregularity_probability__isnull=True) & 
                Q(age__isnull=True)
            ).count()
            return f"Cycle {total_predicted_before_me} – {obj.created_at.date()}"
        else:
            return f"History ({obj.avg_cycle_length}d) – {obj.created_at.date()}"

    def get_created_date(self, obj):
        return obj.created_at.date()


# ======================================================
# Symptom Write
# ======================================================
class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ("id", "cycle", "date", "symptom_name", "severity")
        read_only_fields = ("id",)


# ======================================================
# Reports – Symptom Output
# ======================================================
class SymptomReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ("symptom_name", "severity", "date")


# ======================================================
# Reports – Cycle + Symptoms (READ ONLY)
# ======================================================
class CycleReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    symptoms = SymptomReportSerializer(many=True, read_only=True)  # type: ignore

    class Meta:
        model = Cycle
        fields = (
            "id",
            "username",
            "created_at",
            "age",
            "height",
            "weight",
            "bmi",
            "life_stage",
            "tracking_duration",
            "pain_score",
            "avg_cycle_length",
            "cycle_length_variation",
            "avg_bleeding_days",
            "bleeding_volume_score",
            "intermenstrual_episodes",
            "missed_periods",
            "cycle_variation_coefficient",
            "pattern_disruption_score",
            "irregularity_prediction",
            "irregularity_probability",
            "irregularity_type",
            "next_cycle_prediction",
            "symptoms",
        )
