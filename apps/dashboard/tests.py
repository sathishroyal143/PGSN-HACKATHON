"""Gate 3 — Dashboard API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


def make_user(email, role='FAMILY', phone='+919950000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class DashboardTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('dash_family@test.com', role='FAMILY', phone='+919950000001')
        self.companion = make_user('dash_companion@test.com', role='COMPANION', phone='+919950000002')
        self.admin = User.objects.create_superuser(
            email='dash_admin@test.com', password='TestPass@123',
            phone_number='+919950000003', first_name='Admin', last_name='User',
        )

    def _auth(self, email):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class TestDashboard(DashboardTestBase):
    def test_family_dashboard(self):
        self._auth('dash_family@test.com')
        res = self.client.get('/api/v1/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIsInstance(data, dict)

    def test_companion_dashboard(self):
        self._auth('dash_companion@test.com')
        res = self.client.get('/api/v1/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_dashboard(self):
        self._auth('dash_admin@test.com')
        res = self.client.get('/api/v1/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_dashboard_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_family_dashboard_has_expected_keys(self):
        self._auth('dash_family@test.com')
        res = self.client.get('/api/v1/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Dashboard should return some structured data
        self.assertIn('data', res.data)
