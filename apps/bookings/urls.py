"""Bookings URLs."""
from django.urls import path
from .views import (
    BookingListCreateView, BookingDetailView,
    BookingStatusView, BookingCancelView, AssignCompanionView,
    CompanionAcceptView, CompanionRejectView, CompanionPendingRequestsView,
)

app_name = 'bookings'

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list'),
    path('pending-requests/', CompanionPendingRequestsView.as_view(), name='booking-pending-requests'),
    path('<uuid:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<uuid:pk>/status/', BookingStatusView.as_view(), name='booking-status'),
    path('<uuid:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    path('<uuid:pk>/assign-companion/', AssignCompanionView.as_view(), name='assign-companion'),
    path('<uuid:pk>/accept/', CompanionAcceptView.as_view(), name='booking-accept'),
    path('<uuid:pk>/reject/', CompanionRejectView.as_view(), name='booking-reject'),
]
