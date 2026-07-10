"""URL configuration for Care Services module."""

from django.urls import path
from .views import (
    # Legacy
    ServiceTypeListView,
    ServiceTypeDetailView,
    ServicePackageListView,
    ServicePackageDetailView,
    PriceCalculationView,
    AllPackagesView,
    # New
    ServiceCategoryListView,
    CareServiceListView,
    CareServiceDetailView,
    ScheduledServicesView,
    InstantServicesView,
    EmergencyServicesView,
    ServiceSearchView,
)

app_name = 'services'

urlpatterns = [
    # ── New CareService endpoints ──────────────────────────────────────────────
    # Order matters: specific paths before parameterised paths
    path('categories/', ServiceCategoryListView.as_view(), name='category-list'),
    path('scheduled/', ScheduledServicesView.as_view(), name='scheduled-services'),
    path('instant/', InstantServicesView.as_view(), name='instant-services'),
    path('emergency/', EmergencyServicesView.as_view(), name='emergency-services'),
    path('search/', ServiceSearchView.as_view(), name='service-search'),
    path('', CareServiceListView.as_view(), name='care-service-list'),
    path('<uuid:pk>/', CareServiceDetailView.as_view(), name='care-service-detail'),

    # ── Legacy endpoints (kept intact) ────────────────────────────────────────
    path('types/', ServiceTypeListView.as_view(), name='service-type-list'),
    path('types/<uuid:pk>/', ServiceTypeDetailView.as_view(), name='service-type-detail'),
    path('packages/', ServicePackageListView.as_view(), name='package-list'),
    path('packages/all/', AllPackagesView.as_view(), name='package-all'),
    path('packages/<uuid:pk>/', ServicePackageDetailView.as_view(), name='package-detail'),
    path('calculate-price/', PriceCalculationView.as_view(), name='calculate-price'),
]
