"""Gate 3 — Companions API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


def make_user(email, role='COMPANION', phone='+919400000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class CompanionTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.companion_user = make_user('comp1@test.com', role='COMPANION', phone='+919400000001')
        self.family_user = make_user('comp_family@test.com', role='FAMILY', phone='+919400000002')

    def _auth_companion(self):
        token = get_token(self.client, 'comp1@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_family(self):
        token = get_token(self.client, 'comp_family@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _create_profile(self):
        self._auth_companion()
        return self.client.post('/api/v1/companions/profile/', {
            'bio': 'Experienced care companion',
            'experience_years': 3,
            'languages_spoken': ['English', 'Hindi'],
        }, format='json')


class TestCompanionProfileCreate(CompanionTestBase):
    def test_create_profile_success(self):
        res = self._create_profile()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['experience_years'], 3)

    def test_create_profile_family_forbidden(self):
        self._auth_family()
        res = self.client.post('/api/v1/companions/profile/', {
            'bio': 'Should fail',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_profile_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/companions/profile/', {'bio': 'Test'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCompanionList(CompanionTestBase):
    def test_list_companions_authenticated(self):
        self._create_profile()
        self._auth_family()
        res = self.client.get('/api/v1/companions/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_companions_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/companions/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_companions(self):
        self._create_profile()
        self._auth_family()
        res = self.client.get('/api/v1/companions/?q=care')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestMyCompanionProfile(CompanionTestBase):
    def test_get_my_profile(self):
        self._create_profile()
        self._auth_companion()
        res = self.client.get('/api/v1/companions/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_my_profile_no_profile_404(self):
        self._auth_companion()
        res = self.client.get('/api/v1/companions/me/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class TestCompanionAvailability(CompanionTestBase):
    def setUp(self):
        super().setUp()
        self._create_profile()

    def test_update_availability_online(self):
        self._auth_companion()
        res = self.client.patch('/api/v1/companions/me/availability/', {
            'availability_status': 'AVAILABLE',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_availability_offline(self):
        self._auth_companion()
        res = self.client.patch('/api/v1/companions/me/availability/', {
            'availability_status': 'OFFLINE',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_family_cannot_update_availability(self):
        self._auth_family()
        res = self.client.patch('/api/v1/companions/me/availability/', {
            'availability_status': 'AVAILABLE',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestCompanionLocation(CompanionTestBase):
    def setUp(self):
        super().setUp()
        self._create_profile()

    def test_update_location_success(self):
        self._auth_companion()
        res = self.client.post('/api/v1/companions/me/location/', {
            'latitude': '28.7041',
            'longitude': '77.1025',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_family_cannot_update_location(self):
        self._auth_family()
        res = self.client.post('/api/v1/companions/me/location/', {
            'latitude': '28.7041', 'longitude': '77.1025',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestCompanionDetail(CompanionTestBase):
    def test_get_companion_detail(self):
        create_res = self._create_profile()
        profile_id = create_res.data['data']['id']
        self._auth_family()
        res = self.client.get(f'/api/v1/companions/{profile_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_own_profile(self):
        create_res = self._create_profile()
        profile_id = create_res.data['data']['id']
        self._auth_companion()
        res = self.client.patch(f'/api/v1/companions/{profile_id}/', {
            'bio': 'Updated bio',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['bio'], 'Updated bio')
