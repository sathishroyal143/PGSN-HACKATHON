"""URL configuration for the Patients module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, PatientVitalViewSet, PatientInsuranceViewSet

app_name = 'patients'

router = DefaultRouter()
router.register(r'', PatientViewSet, basename='patient')

urlpatterns = [
    # Nested vitals: /api/v1/patients/{patient_pk}/vitals/
    path(
        '<str:patient_pk>/vitals/',
        PatientVitalViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='patient-vitals-list',
    ),
    path(
        '<str:patient_pk>/vitals/<str:pk>/',
        PatientVitalViewSet.as_view({
            'get': 'retrieve',
            'delete': 'destroy',
        }),
        name='patient-vitals-detail',
    ),
    # Nested insurance: /api/v1/patients/{patient_pk}/insurance/
    path(
        '<str:patient_pk>/insurance/',
        PatientInsuranceViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='patient-insurance-list',
    ),
    path(
        '<str:patient_pk>/insurance/<str:pk>/',
        PatientInsuranceViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='patient-insurance-detail',
    ),
    # Main patient router (includes summary + set-primary actions)
    path('', include(router.urls)),
]
