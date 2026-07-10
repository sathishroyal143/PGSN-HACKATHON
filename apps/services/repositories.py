"""
Care Services repositories.
All database read/write operations are isolated here.
Views and services must not query the ORM directly.
"""

from typing import Optional
from django.db.models import QuerySet
from .models import ServiceType, ServicePackage, ServicePricing, ServiceCategory, CareService
from . import constants


# ── Legacy repositories (kept intact) ─────────────────────────────────────────

class ServiceTypeRepository:
    @staticmethod
    def get_all_active() -> QuerySet:
        return ServiceType.objects.filter(status=constants.STATUS_ACTIVE).order_by('sort_order')

    @staticmethod
    def get_by_id(pk) -> Optional[ServiceType]:
        return ServiceType.objects.filter(pk=pk).first()

    @staticmethod
    def get_by_code(code: str) -> Optional[ServiceType]:
        return ServiceType.objects.filter(code=code).first()

    @staticmethod
    def get_emergency_types() -> QuerySet:
        return ServiceType.objects.filter(is_emergency=True, status=constants.STATUS_ACTIVE)


class ServicePackageRepository:
    @staticmethod
    def get_active_by_type(service_type_id) -> QuerySet:
        return ServicePackage.objects.select_related('service_type', 'pricing').filter(
            service_type_id=service_type_id,
            status=constants.STATUS_ACTIVE,
        ).order_by('sort_order')

    @staticmethod
    def get_by_id(pk) -> Optional[ServicePackage]:
        return ServicePackage.objects.select_related('service_type', 'pricing').filter(pk=pk).first()

    @staticmethod
    def get_featured() -> QuerySet:
        return ServicePackage.objects.select_related('service_type', 'pricing').filter(
            is_featured=True,
            status=constants.STATUS_ACTIVE,
        ).order_by('sort_order')

    @staticmethod
    def get_all_active() -> QuerySet:
        return ServicePackage.objects.select_related('service_type', 'pricing').filter(
            status=constants.STATUS_ACTIVE,
        ).order_by('service_type__sort_order', 'sort_order')


class ServicePricingRepository:
    @staticmethod
    def get_by_package(package_id) -> Optional[ServicePricing]:
        return ServicePricing.objects.filter(package_id=package_id, is_active=True).first()

    @staticmethod
    def get_current_for_service(service_id) -> Optional[ServicePricing]:
        return ServicePricing.objects.filter(
            service_id=service_id,
            is_active=True,
        ).order_by('-effective_from').first()

    @staticmethod
    def create_for_service(service: CareService, data: dict) -> ServicePricing:
        return ServicePricing.objects.create(service=service, package=None, **data)

    @staticmethod
    def replace_for_service(service: CareService, data: dict) -> ServicePricing:
        ServicePricing.objects.filter(service=service, is_active=True).update(is_active=False)
        return ServicePricingRepository.create_for_service(service, data)


# ── New repositories ───────────────────────────────────────────────────────────

class ServiceCategoryRepository:
    @staticmethod
    def get_all_active() -> QuerySet:
        return ServiceCategory.objects.filter(is_active=True).order_by('name')

    @staticmethod
    def get_all() -> QuerySet:
        return ServiceCategory.objects.all().order_by('name')

    @staticmethod
    def get_by_id(pk) -> Optional[ServiceCategory]:
        return ServiceCategory.objects.filter(pk=pk).first()

    @staticmethod
    def get_by_code(code: str) -> Optional[ServiceCategory]:
        return ServiceCategory.objects.filter(code=code).first()

    @staticmethod
    def exists_by_code(code: str) -> bool:
        return ServiceCategory.objects.filter(code=code).exists()

    @staticmethod
    def create(data: dict) -> ServiceCategory:
        return ServiceCategory.objects.create(**data)

    @staticmethod
    def update(instance: ServiceCategory, data: dict) -> ServiceCategory:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class CareServiceRepository:
    _base_qs = lambda: CareService.objects.select_related(  # noqa: E731
        'service_category', 'created_by', 'updated_by'
    ).filter(is_deleted=False)

    @staticmethod
    def get_all_active() -> QuerySet:
        return CareService.objects.select_related(
            'service_category', 'created_by', 'updated_by'
        ).filter(is_deleted=False, status=constants.STATUS_ACTIVE).order_by('service_name')

    @staticmethod
    def get_all_non_deleted() -> QuerySet:
        return CareService.objects.select_related(
            'service_category', 'created_by', 'updated_by'
        ).filter(is_deleted=False).order_by('service_name')

    @staticmethod
    def get_by_id(pk) -> Optional[CareService]:
        return CareService.objects.select_related(
            'service_category', 'created_by', 'updated_by'
        ).filter(pk=pk, is_deleted=False).first()

    @staticmethod
    def get_by_code(code: str) -> Optional[CareService]:
        return CareService.objects.filter(service_code=code, is_deleted=False).first()

    @staticmethod
    def exists_by_name(name: str, exclude_pk=None) -> bool:
        qs = CareService.objects.filter(service_name__iexact=name, is_deleted=False)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @staticmethod
    def exists_by_code(code: str, exclude_pk=None) -> bool:
        qs = CareService.objects.filter(service_code=code, is_deleted=False)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @staticmethod
    def get_by_category_code(category_code: str) -> QuerySet:
        return CareService.objects.select_related('service_category').filter(
            service_category__code=category_code,
            is_deleted=False,
            status=constants.STATUS_ACTIVE,
        ).order_by('service_name')

    @staticmethod
    def search(query: str) -> QuerySet:
        from django.db.models import Q
        return CareService.objects.select_related('service_category').filter(
            Q(service_name__icontains=query) | Q(description__icontains=query),
            is_deleted=False,
            status=constants.STATUS_ACTIVE,
        ).order_by('service_name')[:constants.SEARCH_MAX_RESULTS]

    @staticmethod
    def create(data: dict) -> CareService:
        return CareService.objects.create(**data)

    @staticmethod
    def update(instance: CareService, data: dict) -> CareService:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
