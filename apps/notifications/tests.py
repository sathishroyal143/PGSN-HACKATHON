"""Gate 3 — Notifications API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.notifications.models import Notification


def make_user(email, role='FAMILY', phone='+919700000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class NotificationTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('notif1@test.com', phone='+919700000001')
        self.other = make_user('notif2@test.com', phone='+919700000002')

    def _auth(self, email='notif1@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _create_notification(self, user=None):
        u = user or self.user
        return Notification.objects.create(
            user=u,
            notification_type='BOOKING_CONFIRMED',
            title='Test Notification',
            body='Your booking has been confirmed.',
        )


class TestNotificationList(NotificationTestBase):
    def test_list_notifications(self):
        self._create_notification()
        self._auth()
        res = self.client.get('/api/v1/notifications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_only_own_notifications(self):
        self._create_notification(self.user)
        self._create_notification(self.other)
        self._auth()
        res = self.client.get('/api/v1/notifications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for n in res.data.get('data', []):
            self.assertNotEqual(n.get('user'), str(self.other.id))

    def test_list_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/notifications/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_unread(self):
        self._create_notification()
        self._auth()
        res = self.client.get('/api/v1/notifications/?is_read=false')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestMarkRead(NotificationTestBase):
    def test_mark_single_read(self):
        n = self._create_notification()
        self._auth()
        res = self.client.post(f'/api/v1/notifications/{n.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_all_read(self):
        self._create_notification()
        self._create_notification()
        self._auth()
        res = self.client.post('/api/v1/notifications/read-all/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_mark_read_requires_auth(self):
        n = self._create_notification()
        self.client.credentials()
        res = self.client.post(f'/api/v1/notifications/{n.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_mark_other_users_notification(self):
        n = self._create_notification(self.other)
        self._auth()
        res = self.client.post(f'/api/v1/notifications/{n.id}/read/')
        self.assertIn(res.status_code, [403, 404])


class TestNotificationDelete(NotificationTestBase):
    def test_delete_own_notification(self):
        n = self._create_notification()
        self._auth()
        res = self.client.delete(f'/api/v1/notifications/{n.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Notification.objects.filter(id=n.id).exists())

    def test_cannot_delete_other_users_notification(self):
        n = self._create_notification(self.other)
        self._auth()
        res = self.client.delete(f'/api/v1/notifications/{n.id}/')
        self.assertIn(res.status_code, [403, 404])


class TestNotificationPreferences(NotificationTestBase):
    def test_get_preferences(self):
        self._auth()
        res = self.client.get('/api/v1/notifications/preferences/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_preferences(self):
        self._auth()
        res = self.client.patch('/api/v1/notifications/preferences/', {
            'email_enabled': False,
            'sms_enabled': True,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_preferences_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/notifications/preferences/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
