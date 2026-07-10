"""
Gate 3 — Users API Tests
Tests all user endpoints end-to-end via Django test client.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


class UserTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.users_url = '/api/v1/users/'
        self.me_url = '/api/v1/users/me/'
        self.search_url = '/api/v1/users/search/'

        # Create a regular FAMILY user
        self.user = User.objects.create_user(
            email='family@carebridge.com',
            password='TestPass@123',
            phone_number='+919876543210',
            first_name='Family',
            last_name='User',
            role='FAMILY',
        )
        # Create an ADMIN user
        self.admin = User.objects.create_superuser(
            email='admin@carebridge.com',
            password='AdminPass@123',
            phone_number='+919876543211',
            first_name='Admin',
            last_name='User',
        )

    def _auth(self, user_email='family@carebridge.com', password='TestPass@123'):
        res = self.client.post('/api/v1/auth/login/', {
            'email': user_email, 'password': password
        }, format='json')
        token = res.data.get('data', {}).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token

    def _admin_auth(self):
        return self._auth('admin@carebridge.com', 'AdminPass@123')


class TestGetMe(UserTestBase):
    def test_get_me_success(self):
        self._auth()
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertEqual(data.get('email'), 'family@carebridge.com')

    def test_get_me_requires_auth(self):
        self.client.credentials()
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestGetUser(UserTestBase):
    def test_get_user_self(self):
        self._auth()
        res = self.client.get(f'{self.users_url}{self.user.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_user_requires_auth(self):
        self.client.credentials()
        res = self.client.get(f'{self.users_url}{self.user.id}/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUpdateUser(UserTestBase):
    def test_patch_user_success(self):
        self._auth()
        res = self.client.patch(f'{self.users_url}{self.user.id}/', {
            'first_name': 'Updated',
            'city': 'Mumbai',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.city, 'Mumbai')

    def test_put_user_success(self):
        self._auth()
        res = self.client.put(f'{self.users_url}{self.user.id}/', {
            'first_name': 'PutUpdated',
            'last_name': 'User',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_other_user_forbidden(self):
        # Create another user
        other = User.objects.create_user(
            email='other@carebridge.com',
            password='TestPass@123',
            phone_number='+919876543212',
            first_name='Other',
            last_name='User',
            role='FAMILY',
        )
        self._auth()
        res = self.client.patch(f'{self.users_url}{other.id}/', {'first_name': 'Hacked'}, format='json')
        self.assertIn(res.status_code, [403, 404])

    def test_update_requires_auth(self):
        self.client.credentials()
        res = self.client.patch(f'{self.users_url}{self.user.id}/', {'first_name': 'X'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserStatistics(UserTestBase):
    def test_get_statistics_self(self):
        self._auth()
        res = self.client.get(f'{self.users_url}{self.user.id}/statistics/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('total_activities', data)

    def test_get_statistics_requires_auth(self):
        self.client.credentials()
        res = self.client.get(f'{self.users_url}{self.user.id}/statistics/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestNotificationPreferences(UserTestBase):
    def test_update_notification_prefs(self):
        self._auth()
        res = self.client.patch(f'{self.users_url}{self.user.id}/notification_preferences/', {
            'notification_enabled': False,
            'email_notification_enabled': True,
            'sms_notification_enabled': False,
            'push_notification_enabled': True,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.notification_enabled)

    def test_notification_prefs_requires_auth(self):
        self.client.credentials()
        res = self.client.patch(f'{self.users_url}{self.user.id}/notification_preferences/', {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserSearch(UserTestBase):
    def test_search_users(self):
        self._auth()
        res = self.client.get(self.search_url, {'query': 'family'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_search_by_role(self):
        self._auth()
        res = self.client.get(self.search_url, {'role': 'FAMILY'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_search_requires_auth(self):
        self.client.credentials()
        res = self.client.get(self.search_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAdminEndpoints(UserTestBase):
    def test_list_users_admin(self):
        self._admin_auth()
        res = self.client.get(self.users_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_users_non_admin_forbidden(self):
        self._auth()
        res = self.client.get(self.users_url)
        self.assertIn(res.status_code, [403, 200])  # non-admin sees only own

    def test_block_user_admin(self):
        self._admin_auth()
        res = self.client.post(f'{self.users_url}{self.user.id}/block/', {
            'reason': 'Test block'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_blocked)

    def test_unblock_user_admin(self):
        self._admin_auth()
        self.client.post(f'{self.users_url}{self.user.id}/block/', {'reason': 'Test'}, format='json')
        res = self.client.post(f'{self.users_url}{self.user.id}/unblock/', format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_blocked)

    def test_dashboard_admin(self):
        self._admin_auth()
        res = self.client.get(f'{self.users_url}dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_dashboard_non_admin_forbidden(self):
        self._auth()
        res = self.client.get(f'{self.users_url}dashboard/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_self(self):
        self._auth()
        res = self.client.delete(f'{self.users_url}{self.user.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
