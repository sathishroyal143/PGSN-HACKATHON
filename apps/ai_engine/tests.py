"""Gate 3 — AI Engine API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.family.models import FamilyProfile
from apps.patients.models import Patient
from apps.companions.models import CompanionProfile


def make_user(email, role='FAMILY', phone='+919980000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class AITestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('ai_family@test.com', role='FAMILY', phone='+919980000001')
        self.companion_user = make_user('ai_companion@test.com', role='COMPANION', phone='+919980000002')
        self.admin = User.objects.create_superuser(
            email='ai_admin@test.com', password='TestPass@123',
            phone_number='+919980000003', first_name='Admin', last_name='User',
        )
        FamilyProfile.objects.get_or_create(user=self.family)
        self.companion_profile = CompanionProfile.objects.create(
            user=self.companion_user, status='ACTIVE', availability_status='AVAILABLE',
            experience_years=3,
        )
        self.patient = Patient.objects.create(
            family_user=self.family, first_name='AI', last_name='Patient',
        )

    def _auth(self, email='ai_family@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('ai_admin@test.com')


class TestCompanionMatch(AITestBase):
    def test_match_returns_results(self):
        self._auth()
        res = self.client.post('/api/v1/ai/match/', {
            'patient_id': str(self.patient.id),
            'required_skills': [],
            'preferred_language': 'English',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('matches', data)

    def test_match_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/ai/match/', {
            'patient_id': str(self.patient.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_match_invalid_patient_rejected(self):
        self._auth()
        import uuid
        res = self.client.post('/api/v1/ai/match/', {
            'patient_id': str(uuid.uuid4()),
        }, format='json')
        self.assertIn(res.status_code, [400, 403, 404])


class TestTrustScore(AITestBase):
    def test_trust_score_success(self):
        self._auth()
        res = self.client.post('/api/v1/ai/trust-score/', {
            'companion_id': str(self.companion_user.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('trust_score', data)

    def test_trust_score_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/ai/trust-score/', {
            'companion_id': str(self.companion_user.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPriorityEngine(AITestBase):
    def test_priority_success(self):
        self._auth()
        res = self.client.post('/api/v1/ai/priority/', {
            'patient_id': str(self.patient.id),
            'symptoms': ['chest pain', 'shortness of breath'],
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('priority_level', data)

    def test_priority_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/ai/priority/', {
            'patient_id': str(self.patient.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestMedicalSummary(AITestBase):
    def test_medical_summary_success(self):
        self._auth()
        res = self.client.post('/api/v1/ai/medical-summary/', {
            'patient_id': str(self.patient.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('summary', data)

    def test_medical_summary_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/ai/medical-summary/', {
            'patient_id': str(self.patient.id),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAIHistory(AITestBase):
    def setUp(self):
        super().setUp()
        # Create a request via the match endpoint
        self._auth()
        self.client.post('/api/v1/ai/match/', {
            'patient_id': str(self.patient.id),
        }, format='json')

    def test_list_history(self):
        self._auth()
        res = self.client.get('/api/v1/ai/history/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_history_only_own(self):
        self._auth()
        res = self.client.get('/api/v1/ai/history/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data.get('data', []):
            self.assertEqual(item.get('user'), str(self.family.id))

    def test_history_detail(self):
        self._auth()
        list_res = self.client.get('/api/v1/ai/history/')
        items = list_res.data.get('data', [])
        if items:
            rid = items[0]['id']
            res = self.client.get(f'/api/v1/ai/history/{rid}/')
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_history_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/ai/history/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
