"""URL configuration for Care Journey module."""
from django.urls import path
from .views import (
    JourneyListView, JourneyDetailView, JourneyByBookingView,
    JourneyAdvanceStepView, JourneyNotesView, JourneyCancelView,
)

app_name = 'care_journey'

urlpatterns = [
    path('', JourneyListView.as_view(), name='journey-list'),
    path('<uuid:pk>/', JourneyDetailView.as_view(), name='journey-detail'),
    path('<uuid:pk>/advance-step/', JourneyAdvanceStepView.as_view(), name='journey-advance-step'),
    path('<uuid:pk>/notes/', JourneyNotesView.as_view(), name='journey-notes'),
    path('<uuid:pk>/cancel/', JourneyCancelView.as_view(), name='journey-cancel'),
    path('booking/<uuid:booking_id>/', JourneyByBookingView.as_view(), name='journey-by-booking'),
]
