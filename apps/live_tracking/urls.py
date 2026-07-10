"""Live Tracking URL configuration."""
from django.urls import path
from .views import (
    GeofenceEventListView,
    GeofenceListCreateView,
    LocationHistoryView,
    LocationUpdateView,
    RouteActivateView,
    RouteCompleteView,
    RouteETAView,
    RouteListCreateView,
    TrackingSummaryView,
)

app_name = 'live_tracking'

urlpatterns = [
    # Tracking summary
    path('<uuid:booking_id>/summary/', TrackingSummaryView.as_view(), name='tracking-summary'),

    # Location
    path('<uuid:booking_id>/location/', LocationUpdateView.as_view(), name='location-update'),
    path('<uuid:booking_id>/location/history/', LocationHistoryView.as_view(), name='location-history'),

    # Routes
    path('<uuid:booking_id>/routes/', RouteListCreateView.as_view(), name='route-list-create'),
    path('<uuid:booking_id>/routes/<uuid:route_id>/activate/', RouteActivateView.as_view(), name='route-activate'),
    path('<uuid:booking_id>/routes/<uuid:route_id>/complete/', RouteCompleteView.as_view(), name='route-complete'),
    path('<uuid:booking_id>/routes/<uuid:route_id>/eta/', RouteETAView.as_view(), name='route-eta'),

    # Geofences
    path('<uuid:booking_id>/geofences/', GeofenceListCreateView.as_view(), name='geofence-list-create'),
    path('<uuid:booking_id>/geofences/events/', GeofenceEventListView.as_view(), name='geofence-events'),
]
