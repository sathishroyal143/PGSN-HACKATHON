"""
URL configuration for authentication module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.authentication.views import AuthenticationViewSet

app_name = 'authentication'

router = DefaultRouter()
router.register(r'', AuthenticationViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]

