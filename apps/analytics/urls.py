"""URL configuration for Analytics module."""
from django.urls import path
from .views import (
    AnalyticsDashboardView,
    AnalyticsEventListView,
    GenerateInsightsView,
    InsightListView,
    ReportDetailView,
    ReportListView,
)

app_name = 'analytics'
urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('events/', AnalyticsEventListView.as_view(), name='events'),
    path('reports/', ReportListView.as_view(), name='reports'),
    path('reports/<uuid:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('insights/', InsightListView.as_view(), name='insights'),
    path('insights/generate/', GenerateInsightsView.as_view(), name='generate-insights'),
]
