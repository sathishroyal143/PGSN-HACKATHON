"""Gate 3 — Medical Records API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.family.models import FamilyProfile
from apps.patients.models import Patient


def make_user(email, role='FAMILY', phone='+919000000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['tokens']['access']


class MedicalRecordTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('meduser@test.com', phone='+919100000001')
        FamilyProfile.objects.get_or_create(user=self.user)
        token = get_token(self.client, 'meduser@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post('/api/v1/patients/', {
            'first_name': 'Med', 'last_name': 'Patient', 'blood_group': 'O+',
        }, format='json')
        self.patient_id = res.data['data']['id']
        self.records_url = f'/api/v1/medical-records/patients/{self.patient_id}/records/'

    def _create_record(self):
        return self.client.post(self.records_url, {
            'title': 'Consultation Visit',
            'record_type': 'CONSULTATION',
            'record_date': '2025-01-15',
            'hospital_name': 'City Hospital',
            'doctor_name': 'Dr. Smith',
        }, format='json')


class TestMedicalRecordCRUD(MedicalRecordTestBase):
    def test_create_record(self):
        res = self._create_record()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['title'], 'Consultation Visit')

    def test_list_records(self):
        self._create_record()
        res = self.client.get(self.records_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data['data']), 1)

    def test_retrieve_record(self):
        create_res = self._create_record()
        rid = create_res.data['data']['id']
        res = self.client.get(f'{self.records_url}{rid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_record(self):
        create_res = self._create_record()
        rid = create_res.data['data']['id']
        res = self.client.patch(f'{self.records_url}{rid}/', {'title': 'Updated Title'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['title'], 'Updated Title')

    def test_delete_record(self):
        create_res = self._create_record()
        rid = create_res.data['data']['id']
        res = self.client.delete(f'{self.records_url}{rid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_summary_endpoint(self):
        self._create_record()
        res = self.client.get(f'{self.records_url}summary/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_timeline_endpoint(self):
        self._create_record()
        res = self.client.get(f'{self.records_url}timeline/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_requires_auth(self):
        self.client.credentials()
        res = self.client.get(self.records_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrescriptions(MedicalRecordTestBase):
    def setUp(self):
        super().setUp()
        create_res = self._create_record()
        self.record_id = create_res.data['data']['id']
        self.rx_url = f'/api/v1/medical-records/records/{self.record_id}/prescriptions/'

    def test_create_prescription(self):
        res = self.client.post(self.rx_url, {
            'medicine_name': 'Paracetamol',
            'dosage': '500mg',
            'frequency': 'TWICE_DAILY',
            'prescribed_date': '2025-01-15',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_prescriptions(self):
        self.client.post(self.rx_url, {
            'medicine_name': 'Aspirin', 'dosage': '100mg',
            'frequency': 'ONCE_DAILY', 'prescribed_date': '2025-01-15',
        }, format='json')
        res = self.client.get(self.rx_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_prescription(self):
        create_res = self.client.post(self.rx_url, {
            'medicine_name': 'Ibuprofen', 'dosage': '400mg',
            'frequency': 'THRICE_DAILY', 'prescribed_date': '2025-01-15',
        }, format='json')
        pid = create_res.data['data']['id']
        res = self.client.patch(f'{self.rx_url}{pid}/', {'dosage': '200mg'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_prescription(self):
        create_res = self.client.post(self.rx_url, {
            'medicine_name': 'Metformin', 'dosage': '500mg',
            'frequency': 'TWICE_DAILY', 'prescribed_date': '2025-01-15',
        }, format='json')
        pid = create_res.data['data']['id']
        res = self.client.delete(f'{self.rx_url}{pid}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestLabReports(MedicalRecordTestBase):
    def setUp(self):
        super().setUp()
        create_res = self._create_record()
        self.record_id = create_res.data['data']['id']
        self.lab_url = f'/api/v1/medical-records/records/{self.record_id}/lab-reports/'

    def test_create_lab_report(self):
        res = self.client.post(self.lab_url, {
            'test_name': 'CBC', 'test_date': '2025-01-15',
            'lab_name': 'PathLab', 'status': 'COMPLETED',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_lab_reports(self):
        self.client.post(self.lab_url, {
            'test_name': 'LFT', 'test_date': '2025-01-15',
        }, format='json')
        res = self.client.get(self.lab_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_lab_report(self):
        create_res = self.client.post(self.lab_url, {
            'test_name': 'RFT', 'test_date': '2025-01-15',
        }, format='json')
        lid = create_res.data['data']['id']
        res = self.client.patch(f'{self.lab_url}{lid}/', {'result_value': 'Normal'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
