"""Gate 3 — Support API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.support.models import FAQ


def make_user(email, role='FAMILY', phone='+919960000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class SupportTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('sup_user@test.com', phone='+919960000001')
        self.admin = User.objects.create_superuser(
            email='sup_admin@test.com', password='TestPass@123',
            phone_number='+919960000002', first_name='Admin', last_name='User',
        )

    def _auth(self, email='sup_user@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('sup_admin@test.com')

    def _create_ticket(self):
        self._auth()
        return self.client.post('/api/v1/support/tickets/', {
            'subject': 'App not loading',
            'description': 'The app crashes on startup.',
            'category': 'TECHNICAL',
            'priority': 'HIGH',
        }, format='json')


class TestTickets(SupportTestBase):
    def test_create_ticket_success(self):
        res = self._create_ticket()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['subject'], 'App not loading')

    def test_create_ticket_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/support/tickets/', {
            'subject': 'Test', 'description': 'Test',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tickets(self):
        self._create_ticket()
        self._auth()
        res = self.client.get('/api/v1/support/tickets/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get('data', [])), 1)

    def test_list_only_own_tickets(self):
        self._create_ticket()
        other = make_user('sup_other@test.com', phone='+919960000003')
        token = get_token(self.client, 'sup_other@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get('/api/v1/support/tickets/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for t in res.data.get('data', []):
            self.assertNotEqual(t.get('user'), str(self.user.id))

    def test_get_ticket_detail(self):
        create_res = self._create_ticket()
        tid = create_res.data['data']['id']
        self._auth()
        res = self.client.get(f'/api/v1/support/tickets/{tid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reply_to_ticket(self):
        create_res = self._create_ticket()
        tid = create_res.data['data']['id']
        self._auth()
        res = self.client.post(f'/api/v1/support/tickets/{tid}/', {
            'body': 'I tried reinstalling but it still crashes.',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_close_ticket(self):
        create_res = self._create_ticket()
        tid = create_res.data['data']['id']
        self._auth()
        res = self.client.patch(f'/api/v1/support/tickets/{tid}/', {
            'status': 'CLOSED',
        }, format='json')
        self.assertIn(res.status_code, [200, 400])  # 400 if only admin can close

    def test_ticket_missing_required_fields(self):
        self._auth()
        res = self.client.post('/api/v1/support/tickets/', {'subject': 'Only subject'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestFAQ(SupportTestBase):
    def setUp(self):
        super().setUp()
        FAQ.objects.create(
            category='GENERAL',
            question='How do I book a companion?',
            answer='Go to the Bookings section and click New Booking.',
            is_published=True,
        )
        FAQ.objects.create(
            category='PAYMENTS',
            question='What payment methods are accepted?',
            answer='We accept cards and wallet.',
            is_published=True,
        )

    def test_list_faqs_authenticated(self):
        self._auth()
        res = self.client.get('/api/v1/support/faqs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get('data', [])), 2)

    def test_list_faqs_unauthenticated(self):
        res = self.client.get('/api/v1/support/faqs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_faqs_by_category(self):
        self._auth()
        res = self.client.get('/api/v1/support/faqs/?category=PAYMENTS')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestChatbot(SupportTestBase):
    def test_chatbot_responds(self):
        self._auth()
        res = self.client.post('/api/v1/support/chatbot/', {
            'message': 'How do I cancel a booking?',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('response', res.data.get('data', {}))

    def test_chatbot_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/support/chatbot/', {'message': 'Hello'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_chatbot_empty_message_rejected(self):
        self._auth()
        res = self.client.post('/api/v1/support/chatbot/', {'message': ''}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
