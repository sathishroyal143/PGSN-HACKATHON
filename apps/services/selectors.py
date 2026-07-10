"""
Care Services selectors.
Read-only query helpers. No business logic, no writes.
"""

from typing import Optional
from django.db.models import QuerySet
from .repositories import (
    ServiceTypeRepository,
    ServicePackageRepository,
    ServiceCategoryRepository,
    CareServiceRepository,
)
from . import constants


# ── Legacy selectors ───────────────────────────────────────────────────────────

class ServiceSelectors:
    @staticmethod
    def list_service_types() -> QuerySet:
        return ServiceTypeRepository.get_all_active()

    @staticmethod
    def list_packages_for_type(service_type_id) -> QuerySet:
        return ServicePackageRepository.get_active_by_type(service_type_id)

    @staticmethod
    def get_package_detail(package_id):
        return ServicePackageRepository.get_by_id(package_id)

    @staticmethod
    def list_featured_packages() -> QuerySet:
        return ServicePackageRepository.get_featured()

    @staticmethod
    def calculate_price(package_id, hours: float = 1.0, is_emergency: bool = False, is_night: bool = False):
        package = ServicePackageRepository.get_by_id(package_id)
        if not package or not hasattr(package, 'pricing'):
            return None
        return package.pricing.calculate_total(hours, is_emergency, is_night)


# ── New selectors ──────────────────────────────────────────────────────────────

class ServiceCategorySelectors:
    @staticmethod
    def list_active() -> QuerySet:
        return ServiceCategoryRepository.get_all_active()

    @staticmethod
    def get_by_id(pk) -> Optional[object]:
        return ServiceCategoryRepository.get_by_id(pk)

    @staticmethod
    def get_by_code(code: str) -> Optional[object]:
        return ServiceCategoryRepository.get_by_code(code)


class CareServiceSelectors:
    @staticmethod
    def list_all() -> QuerySet:
        """All non-deleted services (admin view)."""
        return CareServiceRepository.get_all_non_deleted()

    @staticmethod
    def list_active() -> QuerySet:
        """Active non-deleted services (public view)."""
        return CareServiceRepository.get_all_active()

    @staticmethod
    def get_by_id(pk) -> Optional[object]:
        return CareServiceRepository.get_by_id(pk)

    @staticmethod
    def list_scheduled() -> QuerySet:
        return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_SCHEDULED)

    @staticmethod
    def list_instant() -> QuerySet:
        return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_INSTANT)

    @staticmethod
    def list_emergency() -> QuerySet:
        return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_EMERGENCY)

    @staticmethod
    def search(query: str) -> QuerySet:
        return CareServiceRepository.search(query)
