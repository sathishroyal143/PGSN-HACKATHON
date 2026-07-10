"""Gate 3 — Document Verification API Tests."""
import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.document_verification.models import Document, KYCRecord


def make_user(email, role='COMPANION', phone='+919970000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


def fake_file(name='test.pdf', content=b'%PDF-1.4 fake content', content_type='application/pdf'):
    return SimpleUploadedFile(name, content, content_type=content_type)


class VerificationTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.companion = make_user('ver_companion@test.com', role='COMPANION', phone='+919970000001')
        self.admin = User.objects.create_superuser(
            email='ver_admin@test.com', password='TestPass@123',
            phone_number='+919970000002', first_name='Admin', last_name='User',
        )

    def _auth(self, email='ver_companion@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('ver_admin@test.com')

    def _upload_document(self):
        self._auth()
        return self.client.post('/api/v1/verification/documents/', {
            'doc_type': 'AADHAAR',
            'document_number': 'XXXX-XXXX-1234',
            'file': fake_file(),
        }, format='multipart')


class TestDocumentUpload(VerificationTestBase):
    def test_upload_document_success(self):
        res = self._upload_document()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['doc_type'], 'AADHAAR')
        self.assertEqual(res.data['data']['status'], 'PENDING')

    def test_upload_requires_auth(self):
        self.client.credentials()
        res = self.client.post('/api/v1/verification/documents/', {
            'doc_type': 'AADHAAR', 'file': fake_file(),
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_documents(self):
        self._upload_document()
        self._auth()
        res = self.client.get('/api/v1/verification/documents/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get('data', [])), 1)

    def test_get_document_detail(self):
        create_res = self._upload_document()
        doc_id = create_res.data['data']['id']
        self._auth()
        res = self.client.get(f'/api/v1/verification/documents/{doc_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_pending_document(self):
        create_res = self._upload_document()
        doc_id = create_res.data['data']['id']
        self._auth()
        res = self.client.delete(f'/api/v1/verification/documents/{doc_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_only_own_documents(self):
        self._upload_document()
        other = make_user('ver_other@test.com', phone='+919970000003')
        token = get_token(self.client, 'ver_other@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get('/api/v1/verification/documents/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for d in res.data.get('data', []):
            self.assertNotEqual(d.get('user'), str(self.companion.id))


class TestDocumentReview(VerificationTestBase):
    def setUp(self):
        super().setUp()
        self._upload_document()
        self._auth()
        list_res = self.client.get('/api/v1/verification/documents/')
        self.doc_id = list_res.data['data'][0]['id']

    def test_admin_can_approve_document(self):
        self._auth_admin()
        res = self.client.post(f'/api/v1/verification/documents/{self.doc_id}/review/', {
            'action': 'APPROVE',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        doc = Document.objects.get(id=self.doc_id)
        self.assertEqual(doc.status, 'APPROVED')

    def test_admin_can_reject_document(self):
        self._auth_admin()
        res = self.client.post(f'/api/v1/verification/documents/{self.doc_id}/review/', {
            'action': 'REJECT',
            'rejection_reason': 'Document is blurry.',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        doc = Document.objects.get(id=self.doc_id)
        self.assertEqual(doc.status, 'REJECTED')

    def test_non_admin_cannot_review(self):
        self._auth()
        res = self.client.post(f'/api/v1/verification/documents/{self.doc_id}/review/', {
            'action': 'APPROVE',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestKYC(VerificationTestBase):
    def test_get_kyc_status(self):
        self._auth()
        res = self.client.get('/api/v1/verification/kyc/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('status', data)

    def test_kyc_auto_created(self):
        self._auth()
        self.client.get('/api/v1/verification/kyc/')
        self.assertTrue(KYCRecord.objects.filter(user=self.companion).exists())

    def test_kyc_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/verification/kyc/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
