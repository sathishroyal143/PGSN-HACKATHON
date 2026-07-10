"""Default CareBridge service catalog seed data and upsert helpers."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from django.db import transaction

from . import constants
from .models import CareService, ServiceCategory, ServicePackage, ServicePricing, ServiceType

logger = logging.getLogger('carebridge')


CATALOG_EFFECTIVE_FROM = date(2026, 1, 1)


DEFAULT_SERVICE_TYPES: list[dict[str, Any]] = [
    {
        'name': 'Hospital Visit',
        'code': constants.SERVICE_TYPE_HOSPITAL_VISIT,
        'description': 'Companion-assisted planned and urgent hospital visits.',
        'icon': 'hospital',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 10,
    },
    {
        'name': 'Home Care',
        'code': constants.SERVICE_TYPE_HOME_CARE,
        'description': 'At-home care assistance, recovery support, and routine check-ins.',
        'icon': 'home',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 20,
    },
    {
        'name': 'Emergency',
        'code': constants.SERVICE_TYPE_EMERGENCY,
        'description': 'Priority companion assignment for critical care situations.',
        'icon': 'siren',
        'is_emergency': True,
        'requires_companion': True,
        'sort_order': 30,
    },
    {
        'name': 'Diagnostic',
        'code': constants.SERVICE_TYPE_DIAGNOSTIC,
        'description': 'Diagnostic test visits, lab coordination, and report pickup.',
        'icon': 'clipboard-list',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 40,
    },
    {
        'name': 'Pharmacy Run',
        'code': constants.SERVICE_TYPE_PHARMACY,
        'description': 'Medication pickup and delivery coordination.',
        'icon': 'pill',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 50,
    },
    {
        'name': 'Physiotherapy',
        'code': constants.SERVICE_TYPE_PHYSIOTHERAPY,
        'description': 'Physiotherapy appointment and mobility assistance.',
        'icon': 'activity',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 60,
    },
    {
        'name': 'Nursing',
        'code': constants.SERVICE_TYPE_NURSING,
        'description': 'Nursing support for home or hospital care journeys.',
        'icon': 'stethoscope',
        'is_emergency': False,
        'requires_companion': True,
        'sort_order': 70,
    },
]


DEFAULT_SERVICE_CATEGORIES: list[dict[str, str]] = [
    {
        'name': 'Scheduled Care',
        'code': constants.CATEGORY_CODE_SCHEDULED,
        'description': 'Advance booking for planned hospital visits, appointments, follow-ups, and diagnostics.',
    },
    {
        'name': 'Instant Care',
        'code': constants.CATEGORY_CODE_INSTANT,
        'description': 'Same-day assistance for quick hospital visits and immediate care coordination.',
    },
    {
        'name': 'Emergency Care',
        'code': constants.CATEGORY_CODE_EMERGENCY,
        'description': 'Urgent assistance with priority companion assignment and immediate support.',
    },
]


DEFAULT_PACKAGES: list[dict[str, Any]] = [
    {
        'service_type_code': constants.SERVICE_TYPE_HOSPITAL_VISIT,
        'category_code': constants.CATEGORY_CODE_SCHEDULED,
        'name': 'Scheduled Hospital Visit',
        'slug': 'scheduled-hospital-visit',
        'description': 'Planned hospital visit support with appointment coordination, patient pickup, queue assistance, and drop home.',
        'inclusions': ['Appointment coordination', 'Patient pickup', 'Hospital navigation', 'Family updates', 'Drop home'],
        'exclusions': ['Medical consultation fees', 'Diagnostics fees', 'Medicine cost'],
        'min_duration_hours': Decimal('2.0'),
        'max_duration_hours': Decimal('8.0'),
        'companion_count': 1,
        'requires_vehicle': True,
        'requires_medical_training': False,
        'is_featured': True,
        'sort_order': 10,
        'base_price': Decimal('799.00'),
        'price_per_hour': Decimal('299.00'),
        'care_service': {
            'service_name': 'Scheduled Care Companion',
            'service_code': 'SCHEDULED_CARE_COMPANION',
            'estimated_duration': 180,
            'home_visit_supported': False,
            'hospital_visit_supported': True,
            'emergency_supported': False,
            'ai_recommended': True,
            'icon': 'calendar-days',
            'pricing': {'tax': Decimal('144.00'), 'discount': Decimal('50.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_HOME_CARE,
        'category_code': constants.CATEGORY_CODE_SCHEDULED,
        'name': 'Scheduled Home Care Visit',
        'slug': 'scheduled-home-care-visit',
        'description': 'Advance-booked home visit for recovery check-ins, elderly assistance, medication reminders, and family updates.',
        'inclusions': ['Home visit support', 'Medication reminder', 'Vitals coordination', 'Care notes', 'Family update'],
        'exclusions': ['Nursing procedure fees', 'Medical equipment', 'Medicines'],
        'min_duration_hours': Decimal('2.0'),
        'max_duration_hours': Decimal('6.0'),
        'companion_count': 1,
        'requires_vehicle': False,
        'requires_medical_training': False,
        'is_featured': True,
        'sort_order': 20,
        'base_price': Decimal('699.00'),
        'price_per_hour': Decimal('249.00'),
        'care_service': {
            'service_name': 'Scheduled Home Care',
            'service_code': 'SCHEDULED_HOME_CARE',
            'estimated_duration': 120,
            'home_visit_supported': True,
            'hospital_visit_supported': False,
            'emergency_supported': False,
            'ai_recommended': True,
            'icon': 'home',
            'pricing': {'tax': Decimal('126.00'), 'discount': Decimal('40.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_DIAGNOSTIC,
        'category_code': constants.CATEGORY_CODE_SCHEDULED,
        'name': 'Diagnostics and Report Support',
        'slug': 'diagnostics-report-support',
        'description': 'Support for planned diagnostic tests, lab visit coordination, sample logistics, and report collection.',
        'inclusions': ['Diagnostic visit assistance', 'Lab coordination', 'Report pickup', 'Document upload support'],
        'exclusions': ['Lab test charges', 'Doctor consultation fees'],
        'min_duration_hours': Decimal('1.5'),
        'max_duration_hours': Decimal('5.0'),
        'companion_count': 1,
        'requires_vehicle': True,
        'requires_medical_training': False,
        'is_featured': True,
        'sort_order': 30,
        'base_price': Decimal('599.00'),
        'price_per_hour': Decimal('249.00'),
        'care_service': {
            'service_name': 'Diagnostics Care Support',
            'service_code': 'DIAGNOSTICS_CARE_SUPPORT',
            'estimated_duration': 120,
            'home_visit_supported': True,
            'hospital_visit_supported': True,
            'emergency_supported': False,
            'ai_recommended': False,
            'icon': 'clipboard-list',
            'pricing': {'tax': Decimal('108.00'), 'discount': Decimal('30.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_PHARMACY,
        'category_code': constants.CATEGORY_CODE_SCHEDULED,
        'name': 'Medicine Pickup and Delivery',
        'slug': 'medicine-pickup-delivery',
        'description': 'Prescription medicine pickup, pharmacy coordination, and delivery updates for family members.',
        'inclusions': ['Prescription pickup', 'Pharmacy coordination', 'Delivery status update'],
        'exclusions': ['Medicine cost', 'Cold-chain logistics'],
        'min_duration_hours': Decimal('1.0'),
        'max_duration_hours': Decimal('3.0'),
        'companion_count': 1,
        'requires_vehicle': True,
        'requires_medical_training': False,
        'is_featured': False,
        'sort_order': 40,
        'base_price': Decimal('299.00'),
        'price_per_hour': Decimal('199.00'),
        'care_service': {
            'service_name': 'Medicine Pickup Support',
            'service_code': 'MEDICINE_PICKUP_SUPPORT',
            'estimated_duration': 60,
            'home_visit_supported': True,
            'hospital_visit_supported': True,
            'emergency_supported': False,
            'ai_recommended': False,
            'icon': 'pill',
            'pricing': {'tax': Decimal('54.00'), 'discount': Decimal('0.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_HOSPITAL_VISIT,
        'category_code': constants.CATEGORY_CODE_INSTANT,
        'name': 'Instant Hospital Assistance',
        'slug': 'instant-hospital-assistance',
        'description': 'Same-day companion assistance for quick hospital visits, admissions help, and live family updates.',
        'inclusions': ['Immediate companion matching', 'Estimated arrival updates', 'Hospital assistance', 'Live family updates'],
        'exclusions': ['Ambulance charges', 'Hospital charges', 'Doctor consultation fees'],
        'min_duration_hours': Decimal('2.0'),
        'max_duration_hours': Decimal('6.0'),
        'companion_count': 1,
        'requires_vehicle': True,
        'requires_medical_training': False,
        'is_featured': True,
        'sort_order': 50,
        'base_price': Decimal('999.00'),
        'price_per_hour': Decimal('349.00'),
        'care_service': {
            'service_name': 'Instant Care Companion',
            'service_code': 'INSTANT_CARE_COMPANION',
            'estimated_duration': 120,
            'home_visit_supported': False,
            'hospital_visit_supported': True,
            'emergency_supported': False,
            'ai_recommended': True,
            'icon': 'zap',
            'pricing': {'instant_charge': Decimal('200.00'), 'tax': Decimal('180.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_HOME_CARE,
        'category_code': constants.CATEGORY_CODE_INSTANT,
        'name': 'Instant Home Visit Assistance',
        'slug': 'instant-home-visit-assistance',
        'description': 'Immediate home visit support for non-life-threatening assistance and care coordination.',
        'inclusions': ['Live availability check', 'Auto companion matching', 'Home visit assistance', 'Family notification'],
        'exclusions': ['Emergency ambulance', 'Medical procedure fees', 'Medicines'],
        'min_duration_hours': Decimal('1.5'),
        'max_duration_hours': Decimal('5.0'),
        'companion_count': 1,
        'requires_vehicle': False,
        'requires_medical_training': False,
        'is_featured': True,
        'sort_order': 60,
        'base_price': Decimal('899.00'),
        'price_per_hour': Decimal('329.00'),
        'care_service': {
            'service_name': 'Instant Home Care',
            'service_code': 'INSTANT_HOME_CARE',
            'estimated_duration': 90,
            'home_visit_supported': True,
            'hospital_visit_supported': False,
            'emergency_supported': False,
            'ai_recommended': True,
            'icon': 'zap',
            'pricing': {'instant_charge': Decimal('180.00'), 'tax': Decimal('162.00')},
        },
    },
    {
        'service_type_code': constants.SERVICE_TYPE_EMERGENCY,
        'category_code': constants.CATEGORY_CODE_EMERGENCY,
        'name': 'Emergency Priority Companion',
        'slug': 'emergency-priority-companion',
        'description': 'Highest-priority companion assignment with emergency contact notification, hospital recommendation, and live tracking.',
        'inclusions': ['Priority assignment', 'Emergency escalation', 'Hospital recommendation', 'Live tracking', 'Emergency contact notification'],
        'exclusions': ['Ambulance charges', 'Hospital charges', 'Medical treatment fees'],
        'min_duration_hours': Decimal('2.0'),
        'max_duration_hours': Decimal('12.0'),
        'companion_count': 1,
        'requires_vehicle': True,
        'requires_medical_training': True,
        'is_featured': True,
        'sort_order': 70,
        'base_price': Decimal('1499.00'),
        'price_per_hour': Decimal('499.00'),
        'care_service': {
            'service_name': 'Emergency Care Companion',
            'service_code': 'EMERGENCY_CARE_COMPANION',
            'estimated_duration': 180,
            'home_visit_supported': True,
            'hospital_visit_supported': True,
            'emergency_supported': True,
            'ai_recommended': True,
            'icon': 'siren',
            'pricing': {'emergency_charge': Decimal('500.00'), 'tax': Decimal('270.00')},
        },
    },
]


@transaction.atomic
def seed_default_service_catalog() -> dict[str, int]:
    """Create or update the MVP service catalog required by the architecture."""
    created = {'service_types': 0, 'categories': 0, 'packages': 0, 'care_services': 0, 'pricing': 0}
    service_types: dict[str, ServiceType] = {}
    categories: dict[str, ServiceCategory] = {}

    for item in DEFAULT_SERVICE_TYPES:
        service_type, was_created = ServiceType.objects.update_or_create(
            code=item['code'],
            defaults={**item, 'status': constants.STATUS_ACTIVE},
        )
        service_types[item['code']] = service_type
        created['service_types'] += int(was_created)

    for item in DEFAULT_SERVICE_CATEGORIES:
        category, was_created = ServiceCategory.objects.update_or_create(
            code=item['code'],
            defaults={**item, 'is_active': True},
        )
        categories[item['code']] = category
        created['categories'] += int(was_created)

    for item in DEFAULT_PACKAGES:
        package_defaults = {
            'service_type': service_types[item['service_type_code']],
            'name': item['name'],
            'description': item['description'],
            'inclusions': item['inclusions'],
            'exclusions': item['exclusions'],
            'min_duration_hours': item['min_duration_hours'],
            'max_duration_hours': item['max_duration_hours'],
            'companion_count': item['companion_count'],
            'requires_vehicle': item['requires_vehicle'],
            'requires_medical_training': item['requires_medical_training'],
            'status': constants.STATUS_ACTIVE,
            'is_featured': item['is_featured'],
            'sort_order': item['sort_order'],
        }
        package, was_package_created = ServicePackage.objects.update_or_create(
            slug=item['slug'],
            defaults=package_defaults,
        )
        created['packages'] += int(was_package_created)
        pricing, was_pricing_created = ServicePricing.objects.update_or_create(
            package=package,
            defaults={
                'service': None,
                'pricing_type': constants.PRICING_TYPE_HOURLY,
                'base_price': item['base_price'],
                'price_per_hour': item['price_per_hour'],
                'emergency_surcharge_pct': Decimal(str(constants.EMERGENCY_SURCHARGE_DEFAULT_PCT)),
                'night_surcharge_pct': Decimal(str(constants.NIGHT_SURCHARGE_DEFAULT_PCT)),
                'platform_commission_pct': Decimal(str(constants.PLATFORM_COMMISSION_DEFAULT_PCT)),
                'gst_pct': Decimal(str(constants.GST_DEFAULT_PCT)),
                'is_active': True,
                'effective_from': CATALOG_EFFECTIVE_FROM,
                'effective_until': None,
                'effective_to': None,
            },
        )
        created['pricing'] += int(was_pricing_created)

        care = item['care_service']
        care_service, was_care_created = CareService.objects.update_or_create(
            service_code=care['service_code'],
            defaults={
                'service_category': categories[item['category_code']],
                'service_name': care['service_name'],
                'description': item['description'],
                'estimated_duration': care['estimated_duration'],
                'base_price': item['base_price'],
                'home_visit_supported': care['home_visit_supported'],
                'hospital_visit_supported': care['hospital_visit_supported'],
                'emergency_supported': care['emergency_supported'],
                'ai_recommended': care['ai_recommended'],
                'icon': care['icon'],
                'status': constants.STATUS_ACTIVE,
                'is_deleted': False,
                'deleted_at': None,
            },
        )
        created['care_services'] += int(was_care_created)
        service_pricing_defaults = {
            'package': None,
            'pricing_type': constants.PRICING_TYPE_PACKAGE,
            'base_price': item['base_price'],
            'price_per_hour': item['price_per_hour'],
            'emergency_charge': care['pricing'].get('emergency_charge', Decimal('0.00')),
            'instant_charge': care['pricing'].get('instant_charge', Decimal('0.00')),
            'tax': care['pricing'].get('tax', Decimal('0.00')),
            'discount': care['pricing'].get('discount', Decimal('0.00')),
            'is_active': True,
            'effective_from': CATALOG_EFFECTIVE_FROM,
            'effective_until': None,
            'effective_to': None,
        }
        service_pricing = ServicePricing.objects.filter(
            service=care_service,
            effective_from=CATALOG_EFFECTIVE_FROM,
        ).first()
        if service_pricing:
            for field, value in service_pricing_defaults.items():
                setattr(service_pricing, field, value)
            service_pricing.save()
        else:
            ServicePricing.objects.create(service=care_service, **service_pricing_defaults)
            created['pricing'] += 1

        logger.debug('Catalog package %s linked to pricing %s', package.slug, pricing.id)

    logger.info('Care services catalog seed complete: %s', created)
    return created
