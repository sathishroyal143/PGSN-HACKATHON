"""Gate 3 — Bookings API Tests."""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.family.models import FamilyProfile
from apps.patients.models import Patient
from apps.services.models import ServiceType, ServicePackage, ServicePricing
from apps.companions.models import CompanionProfile


def make_user(email, role='FAMILY', phone='+919300000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


def make_package():
    st = ServiceType.objects.create(name='Hospital Visit BK', code='HOSPITAL_VISIT', status='ACTIVE')
    pkg = ServicePackage.objects.create(
        service_type=st, name='Basic BK', slug='basic-bk', status='ACTIVE',
    )
    ServicePricing.objects.create(
        package=pkg, pricing_type='FIXED', base_price=1000, effective_from='2025-01-01',
    )
    return pkg


class BookingTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('bk_family@test.com', role='FAMILY', phone='+919300000001')
        self.companion_user = make_user('bk_companion@test.com', role='COMPANION', phone='+919300000002')
        self.admin = User.objects.create_superuser(
            email='bk_admin@test.com', password='TestPass@123',
            phone_number='+919300000003', first_name='Admin', last_name='User',
        )
        FamilyProfile.objects.get_or_create(user=self.family)
        self.companion_profile = CompanionProfile.objects.create(
            user=self.companion_user, status='ACTIVE', availability_status='AVAILABLE',
        )
        self.package = make_package()
        # Create patient via API
        token = get_token(self.client, 'bk_family@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post('/api/v1/patients/', {
            'first_name': 'BK', 'last_name': 'Patient', 'blood_group': 'A+',
        }, format='json')
        self.patient_id = res.data['data']['id']

    def _auth_family(self):
        token = get_token(self.client, 'bk_family@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_companion(self):
        token = get_token(self.client, 'bk_companion@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        token = get_token(self.client, 'bk_admin@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _booking_payload(self, hours_ahead=2):
        start = timezone.now() + timedelta(hours=hours_ahead)
        end = start + timedelta(hours=4)
        return {
            'service_package_id': str(self.package.id),
            'patient_id': str(self.patient_id),
            'scheduled_start': start.isoformat(),
            'scheduled_end': end.isoformat(),
            'pickup_address': '123 Test Street, Mumbai',
            'booking_type': 'SCHEDULED',
        }

    def _create_booking(self):
        self._auth_family()
        return self.client.post('/api/v1/bookings/', self._booking_payload(), format='json')


class TestBookingCreate(BookingTestBase):
    def test_create_booking_success(self):
        res = self._create_booking()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['status'], 'PENDING')

    def test_create_booking_companion_forbidden(self):
        self._auth_companion()
        res = self.client.post('/api/v1/bookings/', self._booking_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_booking_past_start_rejected(self):
        self._auth_family()
        payload = self._booking_payload()
        payload['scheduled_start'] = (timezone.now() - timedelta(hours=1)).isoformat()
        res = self.client.post('/api/v1/bookings/', payload, format='json')
        self.assertIn(res.status_code, [400, 422])

    def test_create_booking_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/bookings/', self._booking_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestBookingList(BookingTestBase):
    def test_list_bookings_family(self):
        self._create_booking()
        self._auth_family()
        res = self.client.get('/api/v1/bookings/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data['data']), 1)

    def test_list_bookings_companion(self):
        self._auth_companion()
        res = self.client.get('/api/v1/bookings/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_by_status(self):
        self._create_booking()
        self._auth_family()
        res = self.client.get('/api/v1/bookings/?status=PENDING')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestBookingDetail(BookingTestBase):
    def test_get_booking_detail(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_family()
        res = self.client.get(f'/api/v1/bookings/{bid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_access_booking(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        stranger = make_user('stranger_bk@test.com', phone='+919300000009')
        token = get_token(self.client, 'stranger_bk@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(f'/api/v1/bookings/{bid}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestBookingStatusTransition(BookingTestBase):
    def test_confirm_booking_admin(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_admin()
        res = self.client.patch(f'/api/v1/bookings/{bid}/status/', {
            'status': 'CONFIRMED', 'notes': 'Confirmed by admin',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['status'], 'CONFIRMED')

    def test_invalid_transition_rejected(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_admin()
        res = self.client.patch(f'/api/v1/bookings/{bid}/status/', {
            'status': 'COMPLETED',
        }, format='json')
        self.assertIn(res.status_code, [400, 422])


class TestBookingCancel(BookingTestBase):
    def test_cancel_booking_family(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_family()
        res = self.client.post(f'/api/v1/bookings/{bid}/cancel/', {
            'reason': 'Change of plans',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['status'], 'CANCELLED')

    def test_cancel_already_cancelled_rejected(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_family()
        self.client.post(f'/api/v1/bookings/{bid}/cancel/', {'reason': 'First cancel'}, format='json')
        res = self.client.post(f'/api/v1/bookings/{bid}/cancel/', {'reason': 'Second cancel'}, format='json')
        self.assertIn(res.status_code, [400, 422])


class TestAssignCompanion(BookingTestBase):
    def test_assign_companion_admin(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        # Confirm first
        self._auth_admin()
        self.client.patch(f'/api/v1/bookings/{bid}/status/', {'status': 'CONFIRMED'}, format='json')
        res = self.client.post(f'/api/v1/bookings/{bid}/assign-companion/', {
            'companion_id': str(self.companion_user.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['status'], 'COMPANION_ASSIGNED')

    def test_assign_companion_non_admin_forbidden(self):
        create_res = self._create_booking()
        bid = create_res.data['data']['id']
        self._auth_family()
        res = self.client.post(f'/api/v1/bookings/{bid}/assign-companion/', {
            'companion_id': str(self.companion_user.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
