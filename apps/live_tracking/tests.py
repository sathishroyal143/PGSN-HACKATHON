"""Live Tracking tests."""
import uuid
from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.live_tracking.geofence import haversine_distance, is_inside_geofence
from apps.live_tracking.models import Geofence, GeofenceEvent, LocationUpdate, Route
from apps.live_tracking import constants


# ---------------------------------------------------------------------------
# Geofence math
# ---------------------------------------------------------------------------

class HaversineTests(TestCase):

    def test_same_point_is_zero(self):
        self.assertAlmostEqual(haversine_distance(28.7041, 77.1025, 28.7041, 77.1025), 0, places=1)

    def test_known_distance(self):
        # Delhi to Noida ~18 km
        dist = haversine_distance(28.7041, 77.1025, 28.5355, 77.3910)
        self.assertGreater(dist, 15_000)
        self.assertLess(dist, 25_000)

    def test_inside_geofence(self):
        self.assertTrue(is_inside_geofence(28.7041, 77.1025, 28.7041, 77.1025, 200))

    def test_outside_geofence(self):
        # ~1 km away
        self.assertFalse(is_inside_geofence(28.7041, 77.1025, 28.7140, 77.1025, 200))


# ---------------------------------------------------------------------------
# Model smoke tests
# ---------------------------------------------------------------------------

class LocationUpdateModelTest(TestCase):

    def setUp(self):
        from apps.users.models import User
        from apps.family.models import FamilyProfile
        from apps.patients.models import Patient
        from apps.services.models import ServicePackage, ServiceType

        self.family = User.objects.create_user(
            email='family@test.com', password='pass', first_name='F', last_name='U',
            phone_number='+911111111111', role='FAMILY',
        )
        self.companion = User.objects.create_user(
            email='companion@test.com', password='pass', first_name='C', last_name='U',
            phone_number='+912222222222', role='COMPANION',
        )
        family_profile = FamilyProfile.objects.get_or_create(user=self.family)[0]
        self.patient = Patient.objects.create(
            family_profile=family_profile, first_name='P', last_name='T',
            date_of_birth='1980-01-01', gender='MALE',
        )
        service_type = ServiceType.objects.create(name='General LT', code='GENERAL_LT', status='ACTIVE')
        self.package = ServicePackage.objects.create(
            service_type=service_type, name='Basic', slug='basic-lt',
            status='ACTIVE',
        )
        self.booking = Booking.objects.create(
            family_user=self.family,
            patient=self.patient,
            companion=self.companion,
            service_package=self.package,
            status='IN_PROGRESS',
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=4),
            pickup_address='Test Address',
            pickup_latitude=Decimal('28.7041'),
            pickup_longitude=Decimal('77.1025'),
            hospital_name='Test Hospital',
            hospital_latitude=Decimal('28.6139'),
            hospital_longitude=Decimal('77.2090'),
        )

    def test_create_location_update(self):
        update = LocationUpdate.objects.create(
            booking=self.booking,
            companion=self.companion,
            latitude=Decimal('28.7041'),
            longitude=Decimal('77.1025'),
            recorded_at=timezone.now(),
        )
        self.assertEqual(str(update.booking_id), str(self.booking.id))

    def test_create_geofence(self):
        fence = Geofence.objects.create(
            booking=self.booking,
            fence_type=constants.GEOFENCE_PICKUP,
            name='Pickup Zone',
            latitude=Decimal('28.7041'),
            longitude=Decimal('77.1025'),
            radius_meters=200,
        )
        self.assertTrue(fence.is_active)

    def test_create_route(self):
        route = Route.objects.create(
            booking=self.booking,
            leg=constants.LEG_PICKUP,
            origin_latitude=Decimal('28.7041'),
            origin_longitude=Decimal('77.1025'),
            destination_latitude=Decimal('28.6139'),
            destination_longitude=Decimal('77.2090'),
        )
        self.assertEqual(route.status, constants.ROUTE_STATUS_PLANNED)


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class GeofenceServiceTest(TestCase):

    def setUp(self):
        from apps.users.models import User
        from apps.family.models import FamilyProfile
        from apps.patients.models import Patient
        from apps.services.models import ServicePackage, ServiceType

        self.family = User.objects.create_user(
            email='fam2@test.com', password='pass', first_name='F', last_name='U',
            phone_number='+913333333333', role='FAMILY',
        )
        self.companion = User.objects.create_user(
            email='comp2@test.com', password='pass', first_name='C', last_name='U',
            phone_number='+914444444444', role='COMPANION',
        )
        family_profile = FamilyProfile.objects.get_or_create(user=self.family)[0]
        self.patient = Patient.objects.create(
            family_profile=family_profile, first_name='P', last_name='T',
            date_of_birth='1980-01-01', gender='MALE',
        )
        service_type = ServiceType.objects.create(name='General LT2', code='GENERAL_LT2', status='ACTIVE')
        self.package = ServicePackage.objects.create(
            service_type=service_type, name='Basic2', slug='basic-lt2',
            status='ACTIVE',
        )
        self.booking = Booking.objects.create(
            family_user=self.family,
            patient=self.patient,
            companion=self.companion,
            service_package=self.package,
            status='IN_PROGRESS',
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=4),
            pickup_address='Test',
            pickup_latitude=Decimal('28.7041'),
            pickup_longitude=Decimal('77.1025'),
            hospital_name='Hospital',
            hospital_latitude=Decimal('28.6139'),
            hospital_longitude=Decimal('77.2090'),
        )

    @patch('apps.live_tracking.services._broadcast')
    def test_auto_create_geofences(self, mock_broadcast):
        from apps.live_tracking.services import GeofenceService
        fences = GeofenceService.create_geofences_for_booking(self.booking)
        self.assertEqual(len(fences), 2)
        types = {f.fence_type for f in fences}
        self.assertIn(constants.GEOFENCE_PICKUP, types)
        self.assertIn(constants.GEOFENCE_HOSPITAL, types)

    @patch('apps.live_tracking.services._broadcast')
    def test_geofence_enter_event_created(self, mock_broadcast):
        from apps.live_tracking.services import GeofenceService
        GeofenceService.create_geofences_for_booking(self.booking)
        # Companion is exactly at pickup location → should trigger ENTER
        GeofenceService.evaluate(self.booking, self.companion, 28.7041, 77.1025)
        self.assertTrue(
            GeofenceEvent.objects.filter(
                booking=self.booking,
                event_type=constants.GEOFENCE_EVENT_ENTER,
            ).exists()
        )


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

class TrackingAPITest(APITestCase):

    def setUp(self):
        from apps.users.models import User
        from apps.family.models import FamilyProfile
        from apps.patients.models import Patient
        from apps.services.models import ServicePackage, ServiceType

        self.family = User.objects.create_user(
            email='apifam@test.com', password='pass', first_name='F', last_name='U',
            phone_number='+915555555555', role='FAMILY',
        )
        self.companion = User.objects.create_user(
            email='apicomp@test.com', password='pass', first_name='C', last_name='U',
            phone_number='+916666666666', role='COMPANION',
        )
        family_profile = FamilyProfile.objects.get_or_create(user=self.family)[0]
        self.patient = Patient.objects.create(
            family_profile=family_profile, first_name='P', last_name='T',
            date_of_birth='1980-01-01', gender='MALE',
        )
        service_type = ServiceType.objects.create(name='API Cat', code='API_CAT', status='ACTIVE')
        self.package = ServicePackage.objects.create(
            service_type=service_type, name='API Pkg', slug='api-pkg-lt',
            status='ACTIVE',
        )
        self.booking = Booking.objects.create(
            family_user=self.family,
            patient=self.patient,
            companion=self.companion,
            service_package=self.package,
            status='IN_PROGRESS',
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=4),
            pickup_address='Test',
            pickup_latitude=Decimal('28.7041'),
            pickup_longitude=Decimal('77.1025'),
            hospital_name='Hospital',
            hospital_latitude=Decimal('28.6139'),
            hospital_longitude=Decimal('77.2090'),
        )

    def _auth(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    @patch('apps.live_tracking.services._broadcast')
    def test_companion_can_post_location(self, mock_broadcast):
        self._auth(self.companion)
        url = f'/api/v1/tracking/{self.booking.id}/location/'
        payload = {
            'latitude': '28.7041',
            'longitude': '77.1025',
            'recorded_at': timezone.now().isoformat(),
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(LocationUpdate.objects.filter(booking=self.booking).exists())

    @patch('apps.live_tracking.services._broadcast')
    def test_family_can_get_live_location(self, mock_broadcast):
        self._auth(self.family)
        url = f'/api/v1/tracking/{self.booking.id}/location/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.live_tracking.services._broadcast')
    def test_family_can_get_summary(self, mock_broadcast):
        self._auth(self.family)
        url = f'/api/v1/tracking/{self.booking.id}/summary/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.live_tracking.services._broadcast')
    def test_unauthorized_user_cannot_access_tracking(self, mock_broadcast):
        from apps.users.models import User
        stranger = User.objects.create_user(
            email='stranger@test.com', password='pass', first_name='S', last_name='T',
            phone_number='+917777777777', role='FAMILY',
        )
        self._auth(stranger)
        url = f'/api/v1/tracking/{self.booking.id}/location/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
