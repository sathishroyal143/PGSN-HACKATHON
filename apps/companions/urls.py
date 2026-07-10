"""Companions URLs."""
from django.urls import path
from .views import (
    CompanionListView, CompanionProfileCreateView, CompanionProfileDetailView,
    MyCompanionProfileView, CompanionAvailabilityView, CompanionLocationView,
    CompanionSkillListView, CompanionSkillDetailView,
    CompanionSlotListView, CompanionSlotDetailView,
)

app_name = 'companions'

urlpatterns = [
    path('', CompanionListView.as_view(), name='companion-list'),
    path('profile/', CompanionProfileCreateView.as_view(), name='companion-create'),
    path('me/', MyCompanionProfileView.as_view(), name='companion-me'),
    path('me/availability/', CompanionAvailabilityView.as_view(), name='companion-availability'),
    path('me/location/', CompanionLocationView.as_view(), name='companion-location'),
    path('me/skills/', CompanionSkillListView.as_view(), name='companion-skill-list'),
    path('me/skills/<uuid:skill_id>/', CompanionSkillDetailView.as_view(), name='companion-skill-detail'),
    path('me/slots/', CompanionSlotListView.as_view(), name='companion-slot-list'),
    path('me/slots/<uuid:slot_id>/', CompanionSlotDetailView.as_view(), name='companion-slot-detail'),
    path('<uuid:pk>/', CompanionProfileDetailView.as_view(), name='companion-detail'),
]
