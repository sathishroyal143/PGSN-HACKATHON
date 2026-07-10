"""Gate 3 — Communication API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.communication.models import Conversation, ConversationParticipant, Message


def make_user(email, role='FAMILY', phone='+919600000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class CommunicationTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = make_user('comm1@test.com', role='FAMILY', phone='+919600000001')
        self.user2 = make_user('comm2@test.com', role='COMPANION', phone='+919600000002')

    def _auth(self, email='comm1@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _create_direct_conversation(self):
        self._auth('comm1@test.com')
        return self.client.post('/api/v1/communication/conversations/direct/', {
            'participant_id': str(self.user2.id),
        }, format='json')


class TestConversations(CommunicationTestBase):
    def test_list_conversations(self):
        self._auth()
        res = self.client.get('/api/v1/communication/conversations/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_direct_conversation(self):
        res = self._create_direct_conversation()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_direct_conversation_idempotent(self):
        self._create_direct_conversation()
        res = self._create_direct_conversation()
        self.assertIn(res.status_code, [200, 201])

    def test_get_conversation_detail(self):
        create_res = self._create_direct_conversation()
        conv_id = create_res.data['data']['id']
        self._auth()
        res = self.client.get(f'/api/v1/communication/conversations/{conv_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/communication/conversations/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestMessages(CommunicationTestBase):
    def setUp(self):
        super().setUp()
        self._auth()
        create_res = self._create_direct_conversation()
        self.conv_id = create_res.data['data']['id']

    def test_send_message(self):
        self._auth()
        res = self.client.post(
            f'/api/v1/communication/conversations/{self.conv_id}/messages/',
            {'content': 'Hello there!', 'message_type': 'TEXT'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_messages(self):
        self._auth()
        self.client.post(
            f'/api/v1/communication/conversations/{self.conv_id}/messages/',
            {'content': 'Test message', 'message_type': 'TEXT'},
            format='json',
        )
        res = self.client.get(f'/api/v1/communication/conversations/{self.conv_id}/messages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_own_message(self):
        self._auth()
        send_res = self.client.post(
            f'/api/v1/communication/conversations/{self.conv_id}/messages/',
            {'content': 'Delete me', 'message_type': 'TEXT'},
            format='json',
        )
        msg_id = send_res.data['data']['id']
        res = self.client.delete(
            f'/api/v1/communication/conversations/{self.conv_id}/messages/{msg_id}/'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mark_conversation_read(self):
        self._auth()
        res = self.client.post(f'/api/v1/communication/conversations/{self.conv_id}/read/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_typing_indicator(self):
        self._auth()
        res = self.client.post(f'/api/v1/communication/conversations/{self.conv_id}/typing/', {
            'is_typing': True,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestCallLogs(CommunicationTestBase):
    def setUp(self):
        super().setUp()
        self._auth()
        create_res = self._create_direct_conversation()
        self.conv_id = create_res.data['data']['id']

    def test_list_call_logs(self):
        self._auth()
        res = self.client.get(f'/api/v1/communication/conversations/{self.conv_id}/calls/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
