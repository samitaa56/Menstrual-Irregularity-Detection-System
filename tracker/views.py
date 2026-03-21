import numpy as np

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Cycle
from .serializers import (
    CyclePredictionInputSerializer,
    SignupSerializer,
    SaveCycleSerializer,
    CycleListSerializer,
    SymptomSerializer,
    CycleReportSerializer,
)
from .ml_utils import predict_both


# ======================================================
# AI Prediction API
# ======================================================
class CyclePredictionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()

        # ✅ Validate user input FIRST
        serializer = CyclePredictionInputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        cycle_lengths = validated["cycle_lengths"]

        # ==================================================
        # 🔢 AUTO CALCULATIONS (BACKEND AUTHORITY)
        # ==================================================
        avg_cycle = round(sum(cycle_lengths) / len(cycle_lengths))
        variation = max(cycle_lengths) - min(cycle_lengths)
        cvc = round(np.std(cycle_lengths) / avg_cycle, 2)

        # Pattern Disruption Score
        if variation <= 1:
            disruption = 1
        elif variation <= 3:
            disruption = 3
        elif variation <= 5:
            disruption = 6
        else:
            disruption = 9

        # Inject calculated values for ML model
        validated["avg_cycle_length"] = avg_cycle
        validated["cycle_length_variation"] = variation
        validated["cycle_variation_coefficient"] = cvc
        validated["pattern_disruption_score"] = disruption

        # ==================================================
        # 🤖 AI PREDICTION (Regular / Irregular)
        # ==================================================
        result = predict_both(validated)

        # ==================================================
        # 🔍 IRREGULARITY TYPE (CLINICAL RULE-BASED)
        # ==================================================
        irregularity_type = None

        if result["irregularity_prediction"] == "Irregular":

            # 1️⃣ Amenorrhea
            if avg_cycle >= 90:
                irregularity_type = "Amenorrhea"

            # 2️⃣ Polymenorrhea
            elif avg_cycle < 21:
                irregularity_type = "Polymenorrhea"

            # 3️⃣ Oligomenorrhea
            elif avg_cycle > 35:
                irregularity_type = "Oligomenorrhea"

            # 4️⃣ Menorrhagia
            elif (
                validated["avg_bleeding_days"] >= 7
                or validated["bleeding_volume_score"] >= 7
            ):
                irregularity_type = "Menorrhagia"

            # 5️⃣ Intermenstrual Bleeding
            elif validated["intermenstrual_episodes"] > 0:
                irregularity_type = "Intermenstrual Bleeding"

        # ==================================================
        # 🔥 FINAL RESPONSE TO FRONTEND
        # ==================================================
        result.update({
            "avg_cycle_length": avg_cycle,
            "cycle_length_variation": variation,
            "cycle_variation_coefficient": cvc,
            "pattern_disruption_score": disruption,
            "irregularity_type": irregularity_type,
        })

        return Response(result, status=status.HTTP_200_OK)


# ======================================================
# Save Cycle API
# ======================================================
class SaveCycleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SaveCycleSerializer(data=request.data)

        if serializer.is_valid():
            cycle = serializer.save(user=request.user)
            return Response(
                {
                    "message": "Cycle saved successfully",
                    "cycle_id": cycle.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================================================
# Get User Cycles
# ======================================================
class UserCyclesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cycles = Cycle.objects.filter(user=request.user).order_by("-created_at")
        serializer = CycleListSerializer(cycles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ======================================================
# Reports
# ======================================================
class ReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cycles = Cycle.objects.filter(user=request.user).order_by("-created_at")
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
            raise PermissionDenied(
                "You cannot add symptoms to another user's cycle"
            )

        serializer.save()


# ======================================================
# Signup
# ======================================================
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User created successfully",
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )
