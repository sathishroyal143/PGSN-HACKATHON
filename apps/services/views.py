"""
Care Services views.
Thin views — all business logic delegated to services.py and selectors.py.
"""

import logging
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from common.responses import success_response, created_response, error_response
from common.exceptions import ResourceNotFoundException
from .models import ServiceType, ServicePackage
from .serializers import (
    ServiceTypeSerializer,
    ServicePackageListSerializer,
    ServicePackageDetailSerializer,
    ServicePackageWriteSerializer,
    PriceCalculationSerializer,
    ServiceCategorySerializer,
    CareServiceListSerializer,
    CareServiceDetailSerializer,
    CareServiceCreateSerializer,
    CareServiceUpdateSerializer,
    ServiceSearchSerializer,
)
from .selectors import ServiceSelectors, ServiceCategorySelectors, CareServiceSelectors
from .services import ServiceTypeService, ServicePackageService, ServiceCategoryService, CareServiceService
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .exceptions import CareServiceNotFoundException, ServiceCategoryNotFoundException
from .repositories import ServiceTypeRepository

logger = logging.getLogger('carebridge')


# ── Legacy views (kept intact) ─────────────────────────────────────────────────

class ServiceTypeListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=ServiceTypeSerializer(many=True), tags=['Services'])
    def get(self, request):
        types = ServiceSelectors.list_service_types()
        return success_response(ServiceTypeSerializer(types, many=True).data)

    @extend_schema(request=ServiceTypeSerializer, responses=ServiceTypeSerializer, tags=['Services'])
    def post(self, request):
        serializer = ServiceTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service_type = ServiceTypeService.create(serializer.validated_data)
        return created_response(ServiceTypeSerializer(service_type).data, 'Service type created.')


class ServiceTypeDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def _get_object(self, pk):
        obj = ServiceTypeRepository.get_by_id(pk)
        if not obj:
            raise ResourceNotFoundException("Service type not found.")
        return obj

    @extend_schema(responses=ServiceTypeSerializer, tags=['Services'])
    def get(self, request, pk):
        return success_response(ServiceTypeSerializer(self._get_object(pk)).data)

    @extend_schema(request=ServiceTypeSerializer, responses=ServiceTypeSerializer, tags=['Services'])
    def patch(self, request, pk):
        obj = self._get_object(pk)
        serializer = ServiceTypeSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = ServiceTypeService.update(pk, serializer.validated_data)
        return success_response(ServiceTypeSerializer(updated).data, 'Service type updated.')

    @extend_schema(tags=['Services'])
    def delete(self, request, pk):
        ServiceTypeService.deactivate(pk)
        return success_response(message='Service type deactivated.')


class ServicePackageListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        parameters=[OpenApiParameter('service_type', str, description='Filter by service type ID')],
        responses=ServicePackageListSerializer(many=True),
        tags=['Services'],
    )
    def get(self, request):
        service_type_id = request.query_params.get('service_type')
        if service_type_id:
            packages = ServiceSelectors.list_packages_for_type(service_type_id)
        else:
            packages = ServiceSelectors.list_featured_packages()
        return success_response(ServicePackageListSerializer(packages, many=True).data)

    @extend_schema(request=ServicePackageWriteSerializer, responses=ServicePackageDetailSerializer, tags=['Services'])
    def post(self, request):
        serializer = ServicePackageWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = ServicePackageService.create(serializer.validated_data)
        return created_response(ServicePackageDetailSerializer(package).data, 'Package created.')


class ServicePackageDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def _get_object(self, pk):
        obj = ServiceSelectors.get_package_detail(pk)
        if not obj:
            raise ResourceNotFoundException("Service package not found.")
        return obj

    @extend_schema(responses=ServicePackageDetailSerializer, tags=['Services'])
    def get(self, request, pk):
        return success_response(ServicePackageDetailSerializer(self._get_object(pk)).data)

    @extend_schema(request=ServicePackageWriteSerializer, responses=ServicePackageDetailSerializer, tags=['Services'])
    def patch(self, request, pk):
        obj = self._get_object(pk)
        serializer = ServicePackageWriteSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = ServicePackageService.update(pk, serializer.validated_data)
        return success_response(ServicePackageDetailSerializer(updated).data, 'Package updated.')

    @extend_schema(tags=['Services'])
    def delete(self, request, pk):
        ServicePackageService.deactivate(pk)
        return success_response(message='Package deactivated.')


class PriceCalculationView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(request=PriceCalculationSerializer, tags=['Services'])
    def post(self, request):
        serializer = PriceCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        breakdown = ServiceSelectors.calculate_price(
            d['package_id'], d['hours'], d['is_emergency'], d['is_night']
        )
        if not breakdown:
            return error_response('Package or pricing not found.', status_code=404)
        return success_response(breakdown, 'Price calculated.')


class AllPackagesView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=ServicePackageListSerializer(many=True), tags=['Services'])
    def get(self, request):
        from .repositories import ServicePackageRepository
        packages = ServicePackageRepository.get_all_active()
        return success_response(ServicePackageListSerializer(packages, many=True).data)


# ── New views ──────────────────────────────────────────────────────────────────

class ServiceCategoryListView(APIView):
    """
    GET  /api/v1/services/categories/  — list all active categories (all authenticated users)
    POST /api/v1/services/categories/  — create category (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=ServiceCategorySerializer(many=True), tags=['Services'])
    def get(self, request):
        categories = ServiceCategorySelectors.list_active()
        return success_response(ServiceCategorySerializer(categories, many=True).data)

    @extend_schema(request=ServiceCategorySerializer, responses=ServiceCategorySerializer, tags=['Services'])
    def post(self, request):
        serializer = ServiceCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = ServiceCategoryService.create(serializer.validated_data)
        return created_response(ServiceCategorySerializer(category).data, 'Category created.')


class CareServiceListView(APIView):
    """
    GET  /api/v1/services/          — list all active care services
    POST /api/v1/services/          — create care service (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=CareServiceListSerializer(many=True), tags=['Services'])
    def get(self, request):
        services = CareServiceSelectors.list_active()
        return success_response(CareServiceListSerializer(services, many=True).data)

    @extend_schema(request=CareServiceCreateSerializer, responses=CareServiceDetailSerializer, tags=['Services'])
    def post(self, request):
        serializer = CareServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = CareServiceService.create(
            serializer.validated_data, created_by=request.user
        )
        return created_response(CareServiceDetailSerializer(service).data, 'Care service created.')


class CareServiceDetailView(APIView):
    """
    GET    /api/v1/services/{id}/  — retrieve care service
    PUT    /api/v1/services/{id}/  — full update (admin only)
    PATCH  /api/v1/services/{id}/  — partial update (admin only)
    DELETE /api/v1/services/{id}/  — soft delete (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]

    def _get_object(self, pk):
        obj = CareServiceSelectors.get_by_id(pk)
        if not obj:
            raise CareServiceNotFoundException()
        return obj

    @extend_schema(responses=CareServiceDetailSerializer, tags=['Services'])
    def get(self, request, pk):
        return success_response(CareServiceDetailSerializer(self._get_object(pk)).data)

    @extend_schema(request=CareServiceCreateSerializer, responses=CareServiceDetailSerializer, tags=['Services'])
    def put(self, request, pk):
        self._get_object(pk)
        serializer = CareServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = CareServiceService.update(pk, serializer.validated_data, updated_by=request.user)
        return success_response(CareServiceDetailSerializer(updated).data, 'Care service updated.')

    @extend_schema(request=CareServiceUpdateSerializer, responses=CareServiceDetailSerializer, tags=['Services'])
    def patch(self, request, pk):
        self._get_object(pk)
        serializer = CareServiceUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = CareServiceService.update(pk, serializer.validated_data, updated_by=request.user)
        return success_response(CareServiceDetailSerializer(updated).data, 'Care service updated.')

    @extend_schema(tags=['Services'])
    def delete(self, request, pk):
        CareServiceService.soft_delete(pk, deleted_by=request.user)
        return success_response(message='Care service deleted.')


class ScheduledServicesView(APIView):
    """GET /api/v1/services/scheduled/ — list all Scheduled Care services."""
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=CareServiceListSerializer(many=True), tags=['Services'])
    def get(self, request):
        services = CareServiceSelectors.list_scheduled()
        return success_response(CareServiceListSerializer(services, many=True).data)


class InstantServicesView(APIView):
    """GET /api/v1/services/instant/ — list all Instant Care services."""
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=CareServiceListSerializer(many=True), tags=['Services'])
    def get(self, request):
        services = CareServiceSelectors.list_instant()
        return success_response(CareServiceListSerializer(services, many=True).data)


class EmergencyServicesView(APIView):
    """GET /api/v1/services/emergency/ — list all Emergency Care services."""
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(responses=CareServiceListSerializer(many=True), tags=['Services'])
    def get(self, request):
        services = CareServiceSelectors.list_emergency()
        return success_response(CareServiceListSerializer(services, many=True).data)


class ServiceSearchView(APIView):
    """GET /api/v1/services/search/?q=<query> — full-text search across care services."""
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        parameters=[OpenApiParameter('q', str, description='Search query (min 2 characters)')],
        responses=CareServiceListSerializer(many=True),
        tags=['Services'],
    )
    def get(self, request):
        serializer = ServiceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        results = CareServiceSelectors.search(serializer.validated_data['q'])
        return success_response(CareServiceListSerializer(results, many=True).data)
