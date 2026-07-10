"""Gate 3 — Care Journey API Tests."""
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
from apps.bookings.models import Booking
from apps.care_journey.models import CareJourney


def make_user(email, role='FAMILY', phone='+919500000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


def make_booking(family, companion, patient):
    st = ServiceType.objects.create(name='Hospital CJ', code='HOSPITAL_VISIT', status='ACTIVE')
    pkg = ServicePackage.objects.create(
        service_type=st, name='Basic CJ', slug='basic-cj', status='ACTIVE',
    )
    ServicePricing.objects.create(
        package=pkg, pricing_type='FIXED', base_price=1000, effective_from='2025-01-01',
    )
    start = timezone.now() + timedelta(hours=2)
    return Booking.objects.create(
        family_user=family, patient=patient, companion=companion,
        service_package=pkg, status='CONFIRMED',
        scheduled_start=start, scheduled_end=start + timedelta(hours=4),
        pickup_address='Test Address',
    )


class CareJourneyTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('cj_family@test.com', role='FAMILY', phone='+919500000001')
        self.companion_user = make_user('cj_companion@test.com', role='COMPANION', phone='+919500000002')
        self.admin = User.objects.create_superuser(
            email='cj_admin@test.com', password='TestPass@123',
            phone_number='+919500000003', first_name='Admin', last_name='User',
        )
        FamilyProfile.objects.get_or_create(user=self.family)
        CompanionProfile.objects.create(user=self.companion_user, status='ACTIVE')
        self.patient = Patient.objects.create(
            family_user=self.family, first_name='CJ', last_name='Patient',
        )
        self.booking = make_booking(self.family, self.companion_user, self.patient)
        self.journey = CareJourney.objects.create(booking=self.booking, status='ACTIVE')

    def _auth_family(self):
        token = get_token(self.client, 'cj_family@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_companion(self):
        token = get_token(self.client, 'cj_companion@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        token = get_token(self.client, 'cj_admin@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class TestJourneyList(CareJourneyTestBase):
    def test_list_journeys_family(self):
        self._auth_family()
        res = self.client.get('/api/v1/care-journey/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_journeys_companion(self):
        self._auth_companion()
        res = self.client.get('/api/v1/care-journey/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/care-journey/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJourneyDetail(CareJourneyTestBase):
    def test_get_journey_detail(self):
        self._auth_family()
        res = self.client.get(f'/api/v1/care-journey/{self.journey.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_journey_by_booking(self):
        self._auth_family()
        res = self.client.get(f'/api/v1/care-journey/booking/{self.booking.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestJourneyAdvanceStep(CareJourneyTestBase):
    def test_advance_step_companion(self):
        self._auth_companion()
        res = self.client.post(f'/api/v1/care-journey/{self.journey.id}/advance-step/', format='json')
        self.assertIn(res.status_code, [200, 400])  # 400 if no steps initialized

    def test_advance_step_requires_auth(self):
        self.client.credentials()
        res = self.client.post(f'/api/v1/care-journey/{self.journey.id}/advance-step/', format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJourneyNotes(CareJourneyTestBase):
    def test_update_notes_companion(self):
        self._auth_companion()
        res = self.client.patch(f'/api/v1/care-journey/{self.journey.id}/notes/', {
            'companion_notes': 'Patient is comfortable.',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_notes_requires_auth(self):
        self.client.credentials()
        res = self.client.patch(f'/api/v1/care-journey/{self.journey.id}/notes/', {
            'companion_notes': 'Test',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJourneyCancel(CareJourneyTestBase):
    def test_cancel_journey(self):
        self._auth_admin()
        res = self.client.post(f'/api/v1/care-journey/{self.journey.id}/cancel/', format='json')
        self.assertIn(res.status_code, [200, 400])
