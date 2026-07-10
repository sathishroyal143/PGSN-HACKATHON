"""Admin-only Analytics API views."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAnalyticsAdmin
from .selectors import (
    AnalyticsEventSelectors,
    DashboardSelectors,
    InsightSelectors,
    ReportSelectors,
)
from .serializers import (
    AnalyticsEventSerializer,
    CreateAnalyticsEventSerializer,
    CreateReportSerializer,
    DateRangeSerializer,
    InsightSerializer,
    ReportSerializer,
)
from .services import AnalyticsEventService, InsightService, ReportService


class AnalyticsDashboardView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def get(self, request):
        serializer = DateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response({
            'data': DashboardSelectors.summary(**serializer.validated_data),
        })


class AnalyticsEventListView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def get(self, request):
        date_serializer = DateRangeSerializer(data=request.query_params)
        date_serializer.is_valid(raise_exception=True)
        events = AnalyticsEventSelectors.list(
            **date_serializer.validated_data,
            event_type=request.query_params.get('event_type'),
        )
        return Response({'data': AnalyticsEventSerializer(events, many=True).data})

    def post(self, request):
        serializer = CreateAnalyticsEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = AnalyticsEventService.track(
            actor_id=request.user.id, **serializer.validated_data,
        )
        return Response(
            {'data': AnalyticsEventSerializer(event).data},
            status=status.HTTP_201_CREATED,
        )


class ReportListView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def get(self, request):
        reports = ReportSelectors.list()
        return Response({'data': ReportSerializer(reports, many=True).data})

    def post(self, request):
        serializer = CreateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.generate(
            requested_by_id=request.user.id, **serializer.validated_data,
        )
        return Response(
            {'data': ReportSerializer(report).data}, status=status.HTTP_201_CREATED,
        )


class ReportDetailView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def get(self, request, pk):
        report = ReportSelectors.get(pk)
        if not report:
            return Response(
                {'error': {'message': 'Report not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': ReportSerializer(report).data})


class InsightListView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def get(self, request):
        insights = InsightSelectors.active()
        return Response({'data': InsightSerializer(insights, many=True).data})


class GenerateInsightsView(APIView):
    permission_classes = [IsAnalyticsAdmin]

    def post(self, request):
        serializer = DateRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        insights = InsightService.generate(**serializer.validated_data)
        return Response({
            'data': InsightSerializer(insights, many=True).data,
        }, status=status.HTTP_201_CREATED)
