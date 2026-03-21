# tracker/views.py
import numpy as np  # type: ignore
from django.db import transaction  # type: ignore
from django.conf import settings  # type: ignore

from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status, generics  # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated  # type: ignore
from rest_framework.exceptions import PermissionDenied  # type: ignore

from django.core.mail import send_mail  # type: ignore
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # type: ignore
from django.utils.encoding import force_bytes, force_str  # type: ignore
from django.contrib.auth.tokens import default_token_generator  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from .models import Cycle, PendingUser  # type: ignore
from .serializers import (  # type: ignore
    CyclePredictionInputSerializer,
    SignupSerializer,
    SaveCycleSerializer,
    CycleListSerializer,
    SymptomSerializer,
    CycleReportSerializer,
)
from .ml_utils import predict_both  # type: ignore
import secrets
from datetime import timedelta
from django.utils import timezone  # type: ignore


# ======================================================
# AI Prediction API
# ======================================================
class CyclePredictionView(APIView):
    """
    ✅ Predict endpoint:
    - If cycle_lengths NOT sent:
        - If authenticated: fetch last N avg_cycle_length values from DB
        - If not authenticated: return error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        used_db_history = False

        # --------------------------------------------------
        # 0) Auto-calculate Tracking Duration (Months)
        # --------------------------------------------------
        if request.user and request.user.is_authenticated:
            first_cycle = Cycle.objects.filter(user=request.user).order_by("created_at").first()
            if first_cycle:
                from django.utils import timezone  # type: ignore
                from datetime import date
                delta = timezone.now().date() - first_cycle.created_at.date()
                data["tracking_duration"] = max(0, (delta.days // 30))
            else:
                data["tracking_duration"] = 0
        else:
            data["tracking_duration"] = data.get("tracking_duration", 0)

        # --------------------------------------------------
        # 1) If cycle_lengths missing -> try DB history
        # --------------------------------------------------
        if not data.get("cycle_lengths"):
            if request.user and request.user.is_authenticated:
                n = int(data.get("history_n", 5))

                cycles = (
                    Cycle.objects.filter(user=request.user)
                    .exclude(avg_cycle_length__isnull=True)
                    .order_by("-created_at")[:n]
                )

                cycle_lengths_from_db = list(reversed([int(c.avg_cycle_length) for c in cycles]))

                if len(cycle_lengths_from_db) < 2:
                    return Response(
                        {"error": "Please save at least 2 cycles first to enable prediction."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                data["cycle_lengths"] = cycle_lengths_from_db
                used_db_history = True
            else:
                return Response(
                    {
                        "error": "Please login and save at least 2 cycles first, or provide cycle lengths manually."
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # --------------------------------------------------
        # 2) Validate input
        # --------------------------------------------------
        serializer = CyclePredictionInputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # --------------------------------------------------
        # 2.5) Calculate BMI if height/weight provided
        # --------------------------------------------------
        if not validated.get("bmi"):
            h = validated.get("height")
            w = validated.get("weight")
            if h and w:
                height_m = h / 100
                validated["bmi"] = round(w / (height_m * height_m), 2)
            else:
                if not validated.get("bmi"):
                    return Response({"error": "BMI or Height/Weight required."}, status=status.HTTP_400_BAD_REQUEST)

        cycle_lengths = list(validated["cycle_lengths"])

        # --------------------------------------------------
        # 3) Auto calculations
        # --------------------------------------------------

        # ✅ FIX: Add extended cycles for missed periods
        # If user missed periods, each missed period = 60 day cycle
        # This correctly makes cycle status Irregular when periods are missed
        missed = int(validated.get("missed_periods", 0))
        if missed > 0:
            extended_cycles = [60] * missed
            cycle_lengths = cycle_lengths + extended_cycles

        avg_cycle = round(sum(cycle_lengths) / len(cycle_lengths))
        variation = max(cycle_lengths) - min(cycle_lengths)
        cvc = round(np.std(cycle_lengths) / avg_cycle, 2)

        # Cycle status (rule-based)
        if 21 <= avg_cycle <= 35 and variation <= 7:
            cycle_status = "Regular Cycle"
        else:
            cycle_status = "Irregular Cycle"

        # Pattern disruption score
        if variation <= 1:
            disruption = 1
        elif variation <= 3:
            disruption = 3
        elif variation <= 5:
            disruption = 6
        else:
            disruption = 9

        # Inject calculated values for ML
        validated["avg_cycle_length"] = avg_cycle
        validated["cycle_length_variation"] = variation
        validated["cycle_variation_coefficient"] = cvc
        validated["pattern_disruption_score"] = disruption

        # --------------------------------------------------
        # 4) AI prediction
        # --------------------------------------------------
        result = predict_both(validated)

        # --------------------------------------------------
        # 4.5) Clinical Override Rule
        # Rule A: bleeding > 8 days + moderate/severe pain+flow
        # Rule B: missed_periods >= 3 (Amenorrhea indicator)
        # --------------------------------------------------
        bleeding_days = validated.get("avg_bleeding_days", 0)
        pain = validated.get("pain_score", 0)
        flow = validated.get("bleeding_volume_score", 0)
        missed = validated.get("missed_periods", 0)

        clinical_override = (
            (
                bleeding_days > 8
                and (
                    (pain >= 7 and flow >= 3) or
                    (flow >= 7 and pain >= 3)
                )
            )
            or
            missed >= 3
        )

        if clinical_override:
            result["prediction_status"] = "Irregular"
            result["confidence"] = 0.92
            result["chance_of_irregularity"] = 0.92

        # --------------------------------------------------
        # 5) Final response
        # --------------------------------------------------
        result.update(
            {
                "cycle_status": cycle_status,
                "avg_cycle_length": avg_cycle,
                "cycle_length_variation": variation,
                "cycle_variation_coefficient": cvc,
                "pattern_disruption_score": disruption,
                "history_source": "db" if used_db_history else "user_input",
                "history_used": cycle_lengths,
                "bmi": validated.get("bmi"),
                "height": validated.get("height"),
                "weight": validated.get("weight"),
            }
        )

        return Response(result, status=status.HTTP_200_OK)


# ======================================================
# ✅ Save Cycle History (for AddCycleHistory.jsx)
# ======================================================
class SaveCycleHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cycle_lengths = request.data.get("cycle_lengths", None)

        if cycle_lengths is None:
            return Response(
                {"error": "cycle_lengths is required (example: [28, 30])."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(cycle_lengths, list):
            return Response(
                {"error": "cycle_lengths must be a list (e.g. [28, 30])"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cleaned = []
        for x in cycle_lengths:
            try:
                val = int(str(x).strip())
            except Exception:
                continue

            if 15 <= val <= 120:
                cleaned.append(val)

        if len(cleaned) < 2:
            return Response(
                {"error": "Please enter at least 2 valid cycle lengths (15–120 days)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                for length in cleaned:
                    Cycle.objects.create(
                        user=request.user,
                        avg_cycle_length=length,
                    )

            return Response(
                {"message": "Cycle history saved successfully", "saved_count": len(cleaned)},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "error": "Failed to save cycle history.",
                    "detail": str(e),
                    "fix": "Run makemigrations + migrate after updating models.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# ======================================================
# Save Cycle API (full cycle save after prediction)
# ======================================================
class SaveCycleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SaveCycleSerializer(data=request.data)

        if serializer.is_valid():
            cycle = serializer.save(user=request.user)
            return Response(
                {"message": "Cycle saved successfully", "cycle_id": cycle.id},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================================================
# Get User Cycles
# ======================================================
class UserCyclesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q  # type: ignore
        include_history = request.query_params.get('include_history', 'false').lower() == 'true'

        cycles = Cycle.objects.filter(user=request.user)

        if not include_history:
            cycles = cycles.exclude(
                Q(irregularity_prediction__isnull=True) &
                Q(irregularity_probability__isnull=True) &
                Q(age__isnull=True)
            )

        cycles = cycles.order_by("-created_at")
        serializer = CycleListSerializer(cycles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ======================================================
# Reports
# ======================================================
class ReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q  # type: ignore
        cycles = Cycle.objects.filter(
            user=request.user
        ).exclude(
            Q(irregularity_prediction__isnull=True) &
            Q(irregularity_probability__isnull=True) &
            Q(age__isnull=True)
        ).order_by("-created_at")

        serializer = CycleReportSerializer(cycles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ======================================================
# Save Symptoms
# ======================================================
class SymptomCreateView(generics.CreateAPIView):
    serializer_class = SymptomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cycle = serializer.validated_data["cycle"]
        if cycle.user != self.request.user:
            raise PermissionDenied("You cannot add symptoms to another user's cycle")
        serializer.save()


# ======================================================
# Signup
# ======================================================
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = request.data.get('password')

        from django.contrib.auth.hashers import make_password  # type: ignore
        hashed_password = make_password(password)

        verification_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        from django.db.models import Q  # type: ignore
        existing_deleted = PendingUser.objects.filter(Q(email=email) | Q(username=username)).delete()
        if existing_deleted[0] > 0:
            print(f"DEBUG: Deleted {existing_deleted[0]} existing pending user(s) for {username}/{email}")

        try:
            pending_user = PendingUser.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                verification_token=verification_token,
                expires_at=expires_at,
            )
        except Exception as e:
            print(f"ERROR: Failed to create PendingUser: {str(e)}")
            return Response(
                {"error": "This username or email is already in use by a verified user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.conf import settings  # type: ignore
        frontend_base = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_base}/verify-email/{verification_token}"

        try:
            send_mail(
                subject="Verify Your YourFlow Account",
                message=f"Hi {username},\n\nPlease click the link below to verify your email address and complete your signup:\n\n{verification_url}\n\nThis link expires in 24 hours.\n\nThank you!",
                from_email="noreply@yourflow.com",
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"ERROR: Failed to send verification email: {str(e)}")
            return Response(
                {"error": "Failed to send verification email. Please check your SMTP settings or try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "Signup successful. Please check your email to verify your account.",
                "username": username,
                "email": email,
            },
            status=status.HTTP_201_CREATED,
        )


# ======================================================
# Verify Email
# ======================================================
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        clean_token = token.strip().rstrip('/')

        with open("verification_log.txt", "a") as f:
            f.write(f"\n[{timezone.now()}] Request for token: {clean_token}\n")

        try:
            pending_user = PendingUser.objects.filter(verification_token=clean_token).first()

            if not pending_user:
                total_pending = PendingUser.objects.count()
                print(f"DEBUG: No pending user found for token. Total pending in DB: {total_pending}")

                similar = PendingUser.objects.filter(verification_token__startswith=clean_token[:10]).first()
                if similar:
                    print(f"DEBUG: Found a similar token for user {similar.username}")

                return Response(
                    {
                        "error": "Invalid verification link.",
                        "details": "This link may be old or was already used. If you just signed up again, please use the most recent email.",
                        "debug_token_received": clean_token if settings.DEBUG else None
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if pending_user.expires_at < timezone.now():
                pending_user.delete()
                return Response(
                    {"error": "Verification link expired. Please sign up again."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(username=pending_user.username).exists():
                User.objects.filter(username=pending_user.username).delete()

            user = User.objects.create(
                username=pending_user.username,
                email=pending_user.email,
                password=pending_user.password,
            )
            user.is_active = True
            user.save()

            pending_user.delete()

            return Response(
                {
                    "message": "Email verified successfully! Your account is now active. Please log in.",
                    "username": user.username,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"ERROR during verification: {str(e)}")
            return Response(
                {"error": f"Internal verification error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ======================================================
# Development: Quick Email Verification (Testing Only)
# ======================================================
class DevQuickVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {"error": "This endpoint is only available in development mode."},
                status=status.HTTP_403_FORBIDDEN
            )

        email = request.data.get("email")
        username = request.data.get("username")

        if not email and not username:
            return Response(
                {"error": "Please provide 'email' (for pending signup) or 'username' (for existing user)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email:
            try:
                pending_user = PendingUser.objects.get(email=email)

                from django.contrib.auth.hashers import make_password  # type: ignore
                user = User.objects.create_user(
                    username=pending_user.username,
                    email=pending_user.email,
                    password=pending_user.password,
                )

                user.is_active = True
                user.save()

                pending_user.delete()

                return Response(
                    {"message": f"✅ PendingUser '{email}' verified and account created for testing!"},
                    status=status.HTTP_200_OK
                )
            except PendingUser.DoesNotExist:
                return Response(
                    {"error": f"No pending signup found for '{email}'"},
                    status=status.HTTP_404_NOT_FOUND
                )

        if username:
            try:
                user = User.objects.get(username=username)
                user.is_active = True
                user.save()
                return Response(
                    {"message": f"✅ User '{username}' activated for testing!"},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"error": f"User '{username}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )