"""Gate 3 — Reviews API Tests."""
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
from apps.reviews.models import Review, Complaint


def make_user(email, role='FAMILY', phone='+919900000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


def make_completed_booking(family, companion, patient):
    st = ServiceType.objects.create(name='Review Visit', code='REVIEW_VISIT', status='ACTIVE')
    pkg = ServicePackage.objects.create(
        service_type=st, name='Review Basic', slug='review-basic', status='ACTIVE',
    )
    ServicePricing.objects.create(
        package=pkg, pricing_type='FIXED', base_price=1000, effective_from='2025-01-01',
    )
    start = timezone.now() - timedelta(hours=5)
    return Booking.objects.create(
        family_user=family, patient=patient, companion=companion,
        service_package=pkg, status='COMPLETED',
        scheduled_start=start, scheduled_end=start + timedelta(hours=4),
        pickup_address='Test Address',
    )


class ReviewTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('rv_family@test.com', role='FAMILY', phone='+919900000001')
        self.companion_user = make_user('rv_companion@test.com', role='COMPANION', phone='+919900000002')
        self.admin = User.objects.create_superuser(
            email='rv_admin@test.com', password='TestPass@123',
            phone_number='+919900000003', first_name='Admin', last_name='User',
        )
        self.family_profile, _ = FamilyProfile.objects.get_or_create(user=self.family)
        CompanionProfile.objects.get_or_create(user=self.companion_user, defaults={'status': 'ACTIVE'})
        self.patient = Patient.objects.create(
            family_profile=self.family_profile, first_name='RV', last_name='Patient',
        )
        self.booking = make_completed_booking(self.family, self.companion_user, self.patient)

    def _auth(self, email='rv_family@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('rv_admin@test.com')

    def _create_review(self):
        self._auth()
        return self.client.post('/api/v1/reviews/', {
            'booking_id': str(self.booking.id),
            'reviewee_id': str(self.companion_user.id),
            'rating': 5,
            'title': 'Great service',
            'comment': 'Very professional companion.',
        }, format='json')


class TestReviewCRUD(ReviewTestBase):
    def test_create_review_success(self):
        res = self._create_review()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['rating'], 5)

    def test_create_review_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/reviews/', {
            'booking_id': str(self.booking.id), 'rating': 4,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews(self):
        self._create_review()
        self._auth()
        res = self.client.get('/api/v1/reviews/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_reviews_by_user(self):
        self._create_review()
        self._auth()
        res = self.client.get(f'/api/v1/reviews/user/{self.companion_user.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_duplicate_review_rejected(self):
        self._create_review()
        res = self._create_review()
        self.assertIn(res.status_code, [400, 409])

    def test_invalid_rating_rejected(self):
        self._auth()
        res = self.client.post('/api/v1/reviews/', {
            'booking_id': str(self.booking.id),
            'rating': 6,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestReviewReply(ReviewTestBase):
    def setUp(self):
        super().setUp()
        self._auth()
        create_res = self._create_review()
        self.review_id = create_res.data['data']['id']

    def test_companion_can_reply(self):
        self._auth('rv_companion@test.com')
        res = self.client.post(f'/api/v1/reviews/{self.review_id}/reply/', {
            'comment': 'Thank you for the kind words!',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_family_cannot_reply(self):
        self._auth()
        res = self.client.post(f'/api/v1/reviews/{self.review_id}/reply/', {
            'comment': 'Should fail',
        }, format='json')
        self.assertIn(res.status_code, [403, 400])

    def test_duplicate_reply_rejected(self):
        self._auth('rv_companion@test.com')
        self.client.post(f'/api/v1/reviews/{self.review_id}/reply/', {
            'comment': 'First reply',
        }, format='json')
        res = self.client.post(f'/api/v1/reviews/{self.review_id}/reply/', {
            'comment': 'Second reply',
        }, format='json')
        self.assertIn(res.status_code, [400, 409])


class TestComplaints(ReviewTestBase):
    def test_create_complaint(self):
        self._auth()
        res = self.client.post('/api/v1/reviews/complaints/', {
            'booking_id': str(self.booking.id),
            'subject': 'Late arrival',
            'description': 'Companion arrived 30 minutes late.',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_complaints(self):
        self._auth()
        self.client.post('/api/v1/reviews/complaints/', {
            'booking_id': str(self.booking.id),
            'subject': 'Test', 'description': 'Test complaint',
        }, format='json')
        res = self.client.get('/api/v1/reviews/complaints/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_complaint_detail(self):
        self._auth()
        create_res = self.client.post('/api/v1/reviews/complaints/', {
            'booking_id': str(self.booking.id),
            'subject': 'Test', 'description': 'Test complaint',
        }, format='json')
        cid = create_res.data['data']['id']
        res = self.client.get(f'/api/v1/reviews/complaints/{cid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_complaint_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/reviews/complaints/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
