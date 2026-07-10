"""
Care Services business logic layer.
All business rules live here. Views must not contain business logic.
"""

import logging
from django.db import transaction
from common.exceptions import ValidationException, ResourceNotFoundException
from .models import ServiceType, ServicePackage, ServicePricing, ServiceCategory, CareService
from .repositories import (
    ServiceTypeRepository,
    ServicePackageRepository,
    ServicePricingRepository,
    ServiceCategoryRepository,
    CareServiceRepository,
)
from .exceptions import (
    ServiceCategoryNotFoundException,
    CareServiceNotFoundException,
    DuplicateServiceNameException,
    DuplicateServiceCodeException,
    DuplicateCategoryCodeException,
)
from .validators import (
    validate_base_price,
    validate_duration,
    validate_non_negative_money,
    validate_service_code,
)
from . import constants
from django.utils.text import slugify

logger = logging.getLogger('carebridge')


# ── Legacy service classes (kept intact) ──────────────────────────────────────

class ServiceTypeService:
    @staticmethod
    def create(data: dict) -> ServiceType:
        if ServiceType.objects.filter(code=data['code']).exists():
            raise ValidationException(f"Service type with code '{data['code']}' already exists.")
        service_type = ServiceType.objects.create(**data)
        logger.info(f"ServiceType created: {service_type.id}")
        return service_type

    @staticmethod
    def update(pk, data: dict) -> ServiceType:
        service_type = ServiceTypeRepository.get_by_id(pk)
        if not service_type:
            raise ResourceNotFoundException("Service type not found.")
        for field, value in data.items():
            setattr(service_type, field, value)
        service_type.save()
        return service_type

    @staticmethod
    def deactivate(pk) -> ServiceType:
        service_type = ServiceTypeRepository.get_by_id(pk)
        if not service_type:
            raise ResourceNotFoundException("Service type not found.")
        service_type.status = constants.STATUS_INACTIVE
        service_type.save(update_fields=['status'])
        return service_type


class ServicePackageService:
    @staticmethod
    def create(data: dict) -> ServicePackage:
        pricing_data = data.pop('pricing', None)
        if not data.get('slug'):
            data['slug'] = slugify(data.get('name', ''))
        package = ServicePackage.objects.create(**data)
        if pricing_data:
            ServicePricing.objects.create(package=package, **pricing_data)
        logger.info(f"ServicePackage created: {package.id}")
        return package

    @staticmethod
    def update(pk, data: dict) -> ServicePackage:
        package = ServicePackageRepository.get_by_id(pk)
        if not package:
            raise ResourceNotFoundException("Service package not found.")
        pricing_data = data.pop('pricing', None)
        for field, value in data.items():
            setattr(package, field, value)
        package.save()
        if pricing_data and hasattr(package, 'pricing'):
            for field, value in pricing_data.items():
                setattr(package.pricing, field, value)
            package.pricing.save()
        return package

    @staticmethod
    def deactivate(pk) -> ServicePackage:
        package = ServicePackageRepository.get_by_id(pk)
        if not package:
            raise ResourceNotFoundException("Service package not found.")
        package.status = constants.STATUS_INACTIVE
        package.save(update_fields=['status'])
        return package


# ── New service classes ────────────────────────────────────────────────────────

class ServiceCategoryService:
    """Business logic for ServiceCategory management."""

    @staticmethod
    @transaction.atomic
    def create(data: dict) -> ServiceCategory:
        """
        Create a new ServiceCategory.
        Raises DuplicateCategoryCodeException if code already exists.
        """
        code = data.get('code', '')
        if ServiceCategoryRepository.exists_by_code(code):
            raise DuplicateCategoryCodeException(
                f"A category with code '{code}' already exists."
            )
        category = ServiceCategoryRepository.create(data)
        logger.info(f"ServiceCategory created: {category.id} — {category.code}")
        return category

    @staticmethod
    @transaction.atomic
    def update(pk, data: dict) -> ServiceCategory:
        """Update an existing ServiceCategory."""
        category = ServiceCategoryRepository.get_by_id(pk)
        if not category:
            raise ServiceCategoryNotFoundException()
        updated = ServiceCategoryRepository.update(category, data)
        logger.info(f"ServiceCategory updated: {updated.id}")
        return updated

    @staticmethod
    @transaction.atomic
    def activate(pk) -> ServiceCategory:
        """Activate a ServiceCategory."""
        category = ServiceCategoryRepository.get_by_id(pk)
        if not category:
            raise ServiceCategoryNotFoundException()
        category.is_active = True
        category.save(update_fields=['is_active', 'updated_at'])
        logger.info(f"ServiceCategory activated: {category.id}")
        return category

    @staticmethod
    @transaction.atomic
    def deactivate(pk) -> ServiceCategory:
        """Deactivate a ServiceCategory."""
        category = ServiceCategoryRepository.get_by_id(pk)
        if not category:
            raise ServiceCategoryNotFoundException()
        category.is_active = False
        category.save(update_fields=['is_active', 'updated_at'])
        logger.info(f"ServiceCategory deactivated: {category.id}")
        return category


class CareServiceService:
    """Business logic for CareService management."""

    @staticmethod
    @transaction.atomic
    def create(data: dict, created_by=None) -> CareService:
        """
        Create a new CareService.

        Validates:
        - Unique service_name (case-insensitive)
        - Unique service_code
        - base_price >= 0
        - estimated_duration >= MIN_DURATION_MINUTES
        - service_category exists and is active
        """
        pricing_data = data.pop('pricing', None)
        service_name = data.get('service_name', '')
        service_code = data.get('service_code', '')
        base_price = data.get('base_price')
        estimated_duration = data.get('estimated_duration')
        category_id = data.get('service_category_id') or (
            data['service_category'].pk if 'service_category' in data else None
        )

        if CareServiceRepository.exists_by_name(service_name):
            raise DuplicateServiceNameException(
                f"A service named '{service_name}' already exists."
            )
        if CareServiceRepository.exists_by_code(service_code):
            raise DuplicateServiceCodeException(
                f"A service with code '{service_code}' already exists."
            )

        validate_service_code(service_code)
        validate_base_price(base_price)
        validate_duration(estimated_duration)

        # Verify category exists
        category = ServiceCategoryRepository.get_by_id(category_id)
        if not category:
            raise ServiceCategoryNotFoundException()

        data['created_by'] = created_by
        data['updated_by'] = created_by
        service = CareServiceRepository.create(data)
        if pricing_data:
            CareServiceService._validate_pricing_data(pricing_data)
            ServicePricingRepository.create_for_service(service, pricing_data)
        logger.info(f"CareService created: {service.id} — {service.service_code}")
        return service

    @staticmethod
    @transaction.atomic
    def update(pk, data: dict, updated_by=None) -> CareService:
        """
        Update an existing CareService.
        Validates uniqueness constraints excluding the current instance.
        """
        pricing_data = data.pop('pricing', None)
        service = CareServiceRepository.get_by_id(pk)
        if not service:
            raise CareServiceNotFoundException()

        if 'service_name' in data:
            if CareServiceRepository.exists_by_name(data['service_name'], exclude_pk=pk):
                raise DuplicateServiceNameException(
                    f"A service named '{data['service_name']}' already exists."
                )

        if 'service_code' in data:
            validate_service_code(data['service_code'])
            if CareServiceRepository.exists_by_code(data['service_code'], exclude_pk=pk):
                raise DuplicateServiceCodeException(
                    f"A service with code '{data['service_code']}' already exists."
                )

        if 'base_price' in data:
            validate_base_price(data['base_price'])

        if 'estimated_duration' in data:
            validate_duration(data['estimated_duration'])

        if 'service_category' in data:
            category = ServiceCategoryRepository.get_by_id(data['service_category'].pk)
            if not category:
                raise ServiceCategoryNotFoundException()

        data['updated_by'] = updated_by
        updated = CareServiceRepository.update(service, data)
        if pricing_data:
            CareServiceService._validate_pricing_data(pricing_data)
            ServicePricingRepository.replace_for_service(updated, pricing_data)
        logger.info(f"CareService updated: {updated.id}")
        return updated

    @staticmethod
    def _validate_pricing_data(data: dict) -> None:
        """Validate prompt-required service pricing components."""
        validate_base_price(data.get('base_price'))
        for field in ['emergency_charge', 'instant_charge', 'tax', 'discount']:
            validate_non_negative_money(data.get(field), field.replace('_', ' ').title())

    @staticmethod
    @transaction.atomic
    def activate(pk, updated_by=None) -> CareService:
        """Activate a CareService."""
        service = CareServiceRepository.get_by_id(pk)
        if not service:
            raise CareServiceNotFoundException()
        service.activate(updated_by=updated_by)
        logger.info(f"CareService activated: {service.id}")
        return service

    @staticmethod
    @transaction.atomic
    def deactivate(pk, updated_by=None) -> CareService:
        """Deactivate a CareService without deleting it."""
        service = CareServiceRepository.get_by_id(pk)
        if not service:
            raise CareServiceNotFoundException()
        service.deactivate(updated_by=updated_by)
        logger.info(f"CareService deactivated: {service.id}")
        return service

    @staticmethod
    @transaction.atomic
    def soft_delete(pk, deleted_by=None) -> None:
        """Soft-delete a CareService. Never hard-deletes."""
        service = CareServiceRepository.get_by_id(pk)
        if not service:
            raise CareServiceNotFoundException()
        service.soft_delete(deleted_by=deleted_by)
        logger.info(f"CareService soft-deleted: {service.id}")

    @staticmethod
    @transaction.atomic
    def bulk_activate(pks: list, updated_by=None) -> int:
        """Bulk activate services. Returns count of activated services."""
        services = CareService.objects.filter(pk__in=pks, is_deleted=False)
        count = services.update(status=constants.STATUS_ACTIVE)
        logger.info(f"Bulk activated {count} CareServices by {updated_by}")
        return count

    @staticmethod
    @transaction.atomic
    def bulk_deactivate(pks: list, updated_by=None) -> int:
        """Bulk deactivate services. Returns count of deactivated services."""
        services = CareService.objects.filter(pk__in=pks, is_deleted=False)
        count = services.update(status=constants.STATUS_INACTIVE)
        logger.info(f"Bulk deactivated {count} CareServices by {updated_by}")
        return count
