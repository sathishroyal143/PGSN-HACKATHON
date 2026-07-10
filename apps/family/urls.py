"""
URL configuration for Family module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FamilyProfileViewSet, FamilyMemberViewSet, EmergencyContactViewSet

app_name = 'family'

router = DefaultRouter()
router.register(r'profile', FamilyProfileViewSet, basename='family-profile')
router.register(r'members', FamilyMemberViewSet, basename='family-member')
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergency-contact')

urlpatterns = [
    path('', include(router.urls)),
]
