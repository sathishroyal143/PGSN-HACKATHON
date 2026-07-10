"""Tests for the Care Services module."""

import uuid
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.services import constants
from apps.services.exceptions import (
    DuplicateServiceCodeException,
    DuplicateServiceNameException,
    InvalidDurationException,
    InvalidPriceException,
)
from apps.services.models import (
    CareService,
    ServiceCategory,
    ServicePackage,
    ServicePricing,
    ServiceType,
)
from apps.services.permissions import IsAdminOrReadOnly
from apps.services.repositories import CareServiceRepository, ServicePricingRepository
from apps.services.selectors import CareServiceSelectors
from apps.services.serializers import CareServiceCreateSerializer
from apps.services.services import CareServiceService
from apps.services.validators import validate_base_price, validate_duration
from apps.users.models import User, UserRole


def make_user(email: str, role: str = UserRole.FAMILY, phone: str = '+919200000001') -> User:
    return User.objects.create_user(
        email=email,
        password='TestPass@123',
        first_name='Test',
        last_name='User',
        phone_number=phone,
        role=role,
    )


def make_admin() -> User:
    return User.objects.create_superuser(
        email='svc_admin@test.com',
        password='TestPass@123',
        phone_number='+919200000002',
        first_name='Admin',
        last_name='User',
    )


def make_category(code: str = constants.CATEGORY_CODE_SCHEDULED) -> ServiceCategory:
    category, _ = ServiceCategory.objects.get_or_create(
        code=code,
        defaults={
            'name': dict(constants.CATEGORY_CODE_CHOICES)[code],
            'description': 'Care mode',
        },
    )
    return category


def make_care_service(category: ServiceCategory | None = None, **overrides) -> CareService:
    category = category or make_category()
    data = {
        'service_category': category,
        'service_name': f'Care Service {uuid.uuid4()}',
        'service_code': f'CARE_{uuid.uuid4().hex[:8].upper()}',
        'description': 'Reliable care service',
        'estimated_duration': 90,
        'base_price': Decimal('500.00'),
        'home_visit_supported': True,
        'hospital_visit_supported': True,
        'emergency_supported': category.code == constants.CATEGORY_CODE_EMERGENCY,
        'status': constants.STATUS_ACTIVE,
    }
    data.update(overrides)
    return CareService.objects.create(**data)


def make_legacy_package() -> ServicePackage:
    service_type = ServiceType.objects.create(
        name='Hospital Visit',
        code='HOSPITAL_VISIT',
        status=constants.STATUS_ACTIVE,
    )
    package = ServicePackage.objects.create(
        service_type=service_type,
        name='Basic Visit',
        slug=f'basic-visit-{uuid.uuid4().hex[:8]}',
        status=constants.STATUS_ACTIVE,
        is_featured=True,
    )
    ServicePricing.objects.create(
        package=package,
        pricing_type=constants.PRICING_TYPE_HOURLY,
        base_price=Decimal('500.00'),
        price_per_hour=Decimal('200.00'),
        effective_from='2026-01-01',
    )
    return package


class CareServiceTestBase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.family = make_user('svc_family@test.com', phone='+919200000001')
        self.patient = make_user('svc_patient@test.com', phone='+919200000003')
        self.companion = make_user(
            'svc_companion@test.com',
            role=UserRole.COMPANION,
            phone='+919200000004',
        )
        self.admin = make_admin()
        self.category = make_category()

    def authenticate(self, user: User) -> None:
        self.client.force_authenticate(user=user)


class CareServiceModelTests(TestCase):
    def test_soft_delete_marks_service_inactive(self):
        service = make_care_service()

        service.soft_delete()

        service.refresh_from_db()
        self.assertTrue(service.is_deleted)
        self.assertEqual(service.status, constants.STATUS_INACTIVE)
        self.assertIsNotNone(service.deleted_at)

    def test_service_pricing_calculates_flat_total(self):
        service = make_care_service()
        pricing = ServicePricing.objects.create(
            service=service,
            base_price=Decimal('100.00'),
            emergency_charge=Decimal('25.00'),
            instant_charge=Decimal('10.00'),
            tax=Decimal('18.00'),
            discount=Decimal('8.00'),
            effective_from='2026-01-01',
        )

        self.assertEqual(pricing.total_price, Decimal('145.00'))

    def test_legacy_package_pricing_still_calculates_hourly_total(self):
        package = make_legacy_package()

        breakdown = package.pricing.calculate_total(hours=2)

        self.assertEqual(breakdown['base_price'], 400.0)
        self.assertGreater(breakdown['total'], breakdown['base_price'])


class CareServiceSerializerTests(TestCase):
    def test_create_serializer_accepts_nested_pricing(self):
        category = make_category()
        serializer = CareServiceCreateSerializer(data={
            'service_category': str(category.id),
            'service_name': 'Home Nursing',
            'service_code': 'HOME_NURSING',
            'estimated_duration': 60,
            'base_price': '750.00',
            'home_visit_supported': True,
            'hospital_visit_supported': False,
            'emergency_supported': False,
            'pricing': {
                'base_price': '750.00',
                'instant_charge': '50.00',
                'tax': '90.00',
                'discount': '25.00',
                'effective_from': '2026-01-01',
            },
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_rejects_negative_price(self):
        category = make_category()
        serializer = CareServiceCreateSerializer(data={
            'service_category': str(category.id),
            'service_name': 'Invalid Price',
            'service_code': 'INVALID_PRICE',
            'estimated_duration': 60,
            'base_price': '-1.00',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('base_price', serializer.errors)


class CareServiceServiceTests(TestCase):
    def test_create_service_with_pricing(self):
        category = make_category()

        service = CareServiceService.create({
            'service_category': category,
            'service_name': 'Scheduled Hospital Visit',
            'service_code': 'SCHEDULED_HOSPITAL_VISIT',
            'estimated_duration': 120,
            'base_price': Decimal('1000.00'),
            'hospital_visit_supported': True,
            'pricing': {
                'base_price': Decimal('1000.00'),
                'tax': Decimal('180.00'),
                'discount': Decimal('100.00'),
                'effective_from': '2026-01-01',
            },
        })

        pricing = ServicePricingRepository.get_current_for_service(service.id)
        self.assertIsNotNone(pricing)
        self.assertEqual(pricing.total_price, Decimal('1080.00'))

    def test_duplicate_name_raises_domain_exception(self):
        category = make_category()
        make_care_service(category, service_name='Duplicate Care', service_code='DUPLICATE_CARE')

        with self.assertRaises(DuplicateServiceNameException):
            CareServiceService.create({
                'service_category': category,
                'service_name': 'duplicate care',
                'service_code': 'DUPLICATE_CARE_TWO',
                'estimated_duration': 60,
                'base_price': Decimal('100.00'),
            })

    def test_duplicate_code_raises_domain_exception(self):
        category = make_category()
        make_care_service(category, service_name='Code One', service_code='DUPLICATE_CODE')

        with self.assertRaises(DuplicateServiceCodeException):
            CareServiceService.create({
                'service_category': category,
                'service_name': 'Code Two',
                'service_code': 'DUPLICATE_CODE',
                'estimated_duration': 60,
                'base_price': Decimal('100.00'),
            })


class CareServiceRepositorySelectorTests(TestCase):
    def test_repository_excludes_soft_deleted_services(self):
        active = make_care_service(service_name='Active Service', service_code='ACTIVE_SERVICE')
        deleted = make_care_service(service_name='Deleted Service', service_code='DELETED_SERVICE')
        deleted.soft_delete()

        ids = set(CareServiceRepository.get_all_active().values_list('id', flat=True))

        self.assertIn(active.id, ids)
        self.assertNotIn(deleted.id, ids)

    def test_selector_filters_emergency_services(self):
        emergency_category = make_category(constants.CATEGORY_CODE_EMERGENCY)
        emergency = make_care_service(
            emergency_category,
            service_name='Emergency Escort',
            service_code='EMERGENCY_ESCORT',
            emergency_supported=True,
        )

        ids = set(CareServiceSelectors.list_emergency().values_list('id', flat=True))

        self.assertIn(emergency.id, ids)


class CareServicePermissionTests(TestCase):
    def test_admin_can_write_and_family_can_only_read(self):
        permission = IsAdminOrReadOnly()
        admin = make_admin()
        family = make_user('permission_family@test.com', phone='+919200000005')

        class Request:
            user = family
            method = 'POST'

        self.assertFalse(permission.has_permission(Request, None))
        Request.user = admin
        self.assertTrue(permission.has_permission(Request, None))
        Request.user = family
        Request.method = 'GET'
        self.assertTrue(permission.has_permission(Request, None))


class CareServiceValidationTests(TestCase):
    def test_price_cannot_be_negative(self):
        with self.assertRaises(InvalidPriceException):
            validate_base_price(Decimal('-0.01'))

    def test_duration_must_be_positive(self):
        with self.assertRaises(InvalidDurationException):
            validate_duration(0)


class CareServiceViewTests(CareServiceTestBase):
    def test_family_can_list_services(self):
        make_care_service(self.category, service_name='Family Visible', service_code='FAMILY_VISIBLE')
        self.authenticate(self.family)

        response = self.client.get('/api/v1/services/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)

    def test_patient_role_can_view_services(self):
        make_care_service(self.category, service_name='Patient Visible', service_code='PATIENT_VISIBLE')
        self.authenticate(self.patient)

        response = self.client.get('/api/v1/services/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_companion_can_view_assigned_service_categories(self):
        self.authenticate(self.companion)

        response = self.client.get('/api/v1/services/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['code'], constants.CATEGORY_CODE_SCHEDULED)

    def test_admin_can_create_update_and_soft_delete_service(self):
        self.authenticate(self.admin)
        create_response = self.client.post('/api/v1/services/', {
            'service_category': str(self.category.id),
            'service_name': 'Admin Created Care',
            'service_code': 'ADMIN_CREATED_CARE',
            'estimated_duration': 75,
            'base_price': '900.00',
            'home_visit_supported': True,
            'pricing': {
                'base_price': '900.00',
                'tax': '108.00',
                'effective_from': '2026-01-01',
            },
        }, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        service_id = create_response.data['data']['id']
        self.assertEqual(create_response.data['data']['pricing']['total_price'], '1008.00')

        update_response = self.client.patch(f'/api/v1/services/{service_id}/', {
            'base_price': '950.00',
        }, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(f'/api/v1/services/{service_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertTrue(CareService.objects.get(id=service_id).is_deleted)

    def test_non_admin_cannot_create_service(self):
        self.authenticate(self.family)

        response = self.client.post('/api/v1/services/', {
            'service_category': str(self.category.id),
            'service_name': 'Forbidden Care',
            'service_code': 'FORBIDDEN_CARE',
            'estimated_duration': 60,
            'base_price': '100.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_filter_endpoints(self):
        instant = make_category(constants.CATEGORY_CODE_INSTANT)
        emergency = make_category(constants.CATEGORY_CODE_EMERGENCY)
        make_care_service(self.category, service_name='Scheduled Care', service_code='SCHEDULED_FILTER')
        make_care_service(instant, service_name='Instant Care', service_code='INSTANT_FILTER')
        make_care_service(emergency, service_name='Emergency Care', service_code='EMERGENCY_FILTER')
        self.authenticate(self.family)

        self.assertEqual(self.client.get('/api/v1/services/scheduled/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/v1/services/instant/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/v1/services/emergency/').status_code, status.HTTP_200_OK)

    def test_search_services(self):
        make_care_service(self.category, service_name='Searchable Nursing', service_code='SEARCHABLE_NURSING')
        self.authenticate(self.family)

        response = self.client.get('/api/v1/services/search/?q=Nursing')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_unauthenticated_user_cannot_access_services(self):
        response = self.client.get('/api/v1/services/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
