"""URL configuration for AI Engine module."""
from django.urls import path
from .views import (
    CompanionMatchView, TrustScoreView,
    PriorityView, MedicalSummaryView,
    AIRequestHistoryView, AIRequestDetailView,
)

app_name = 'ai_engine'

urlpatterns = [
    path('match/',           CompanionMatchView.as_view(),    name='companion-match'),
    path('trust-score/',     TrustScoreView.as_view(),        name='trust-score'),
    path('priority/',        PriorityView.as_view(),          name='priority'),
    path('medical-summary/', MedicalSummaryView.as_view(),    name='medical-summary'),
    path('history/',         AIRequestHistoryView.as_view(),  name='history'),
    path('history/<uuid:pk>/', AIRequestDetailView.as_view(), name='history-detail'),
]
