"""AI Engine views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    AIRequestSerializer, MatchScoreSerializer,
    CompanionMatchInputSerializer, TrustScoreInputSerializer,
    PriorityInputSerializer, MedicalSummaryInputSerializer,
)
from .selectors import AIRequestSelectors, MatchScoreSelectors
from .services import (
    CompanionMatchService, TrustScoreService,
    PriorityService, MedicalSummaryService,
)


class CompanionMatchView(APIView):
    """POST /api/v1/ai/match/ — rank companions for a patient."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = CompanionMatchInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        _, output = CompanionMatchService.run(
            user_id=request.user.id,
            patient_id=d['patient_id'],
            required_skills=d.get('required_skills'),
            top_n=d.get('top_n', 10),
        )
        return Response({'data': output}, status=status.HTTP_200_OK)


class TrustScoreView(APIView):
    """POST /api/v1/ai/trust-score/ — compute/refresh companion trust score."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = TrustScoreInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        _, output = TrustScoreService.run(
            user_id=request.user.id,
            companion_id=ser.validated_data['companion_id'],
        )
        return Response({'data': output}, status=status.HTTP_200_OK)


class PriorityView(APIView):
    """POST /api/v1/ai/priority/ — assess care priority for a patient."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PriorityInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        _, output = PriorityService.run(
            user_id=request.user.id,
            patient_id=d['patient_id'],
            is_emergency=d.get('is_emergency', False),
        )
        return Response({'data': output}, status=status.HTTP_200_OK)


class MedicalSummaryView(APIView):
    """POST /api/v1/ai/medical-summary/ — generate plain-text medical summary."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = MedicalSummaryInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        _, output = MedicalSummaryService.run(
            user_id=request.user.id,
            patient_id=ser.validated_data['patient_id'],
        )
        return Response({'data': output}, status=status.HTTP_200_OK)


class AIRequestHistoryView(APIView):
    """GET /api/v1/ai/history/ — list current user's AI requests."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = AIRequestSelectors.for_user(request.user.id)
        ser = AIRequestSerializer(requests, many=True)
        return Response({'data': ser.data}, status=status.HTTP_200_OK)


class AIRequestDetailView(APIView):
    """GET /api/v1/ai/history/<pk>/ — detail + match scores if applicable."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ai_request = AIRequestSelectors.get_by_id(pk)
        if not ai_request or ai_request.user_id != request.user.id:
            return Response({'error': {'message': 'Not found.'}}, status=status.HTTP_404_NOT_FOUND)

        data = AIRequestSerializer(ai_request).data
        if ai_request.request_type == 'companion_match':
            scores = MatchScoreSelectors.for_request(pk)
            data['match_scores'] = MatchScoreSerializer(scores, many=True).data

        return Response({'data': data}, status=status.HTTP_200_OK)
