"""
Tests for the Patients module.
Covers all endpoints: patients CRUD, vitals, insurance, summary, set-primary.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, UserRole
from apps.family.models import FamilyProfile, FamilyMember
from apps.patients.models import Patient, PatientVital, PatientInsurance
from apps.patients import constants


def make_user(email, role=UserRole.FAMILY, phone='+919000000001'):
    return User.objects.create_user(
        email=email,
        password='TestPass@123',
        first_name='Test',
        last_name='User',
        phone_number=phone,
        role=role,
    )


def get_tokens(client, email, password='TestPass@123'):
    resp = client.post('/api/v1/auth/login/', {'email': email, 'password': password})
    return resp.data['data']['tokens']['access']


def auth(client, token):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class PatientCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('family@test.com', phone='+919000000001')
        # FamilyProfile is auto-created by signal on FAMILY user creation
        self.profile = FamilyProfile.objects.get(user=self.user)
        token = get_tokens(self.client, 'family@test.com')
        auth(self.client, token)

    def _create_patient(self, first_name='John', last_name='Doe'):
        return self.client.post('/api/v1/patients/', {
            'first_name': first_name,
            'last_name': last_name,
            'blood_group': 'O+',
            'gender': 'MALE',
        })

    def test_create_patient(self):
        resp = self._create_patient()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['data']['first_name'], 'John')

    def test_list_patients(self):
        self._create_patient()
        resp = self.client.get('/api/v1/patients/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['data']), 1)

    def test_retrieve_patient(self):
        create_resp = self._create_patient()
        pid = create_resp.data['data']['id']
        resp = self.client.get(f'/api/v1/patients/{pid}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['id'], pid)

    def test_update_patient(self):
        create_resp = self._create_patient()
        pid = create_resp.data['data']['id']
        resp = self.client.patch(f'/api/v1/patients/{pid}/', {'blood_group': 'A+'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['blood_group'], 'A+')

    def test_delete_patient(self):
        create_resp = self._create_patient()
        pid = create_resp.data['data']['id']
        resp = self.client.delete(f'/api/v1/patients/{pid}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Confirm soft-deleted (not accessible)
        resp2 = self.client.get(f'/api/v1/patients/{pid}/')
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_limit(self):
        for i in range(constants.MAX_PATIENTS_PER_FAMILY):
            self._create_patient(first_name=f'Patient{i}', last_name='X')
        resp = self._create_patient(first_name='Extra', last_name='Patient')
        self.assertEqual(resp.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_summary(self):
        self._create_patient()
        resp = self.client.get('/api/v1/patients/summary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data['data'], list)

    def test_set_primary(self):
        self._create_patient('Alice', 'A')
        resp2 = self._create_patient('Bob', 'B')
        pid = resp2.data['data']['id']
        resp = self.client.post(f'/api/v1/patients/{pid}/set-primary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        patient = Patient.objects.get(id=pid)
        self.assertTrue(patient.is_primary)

    def test_unauthenticated_access(self):
        self.client.credentials()
        resp = self.client.get('/api/v1/patients/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_family_cannot_access(self):
        create_resp = self._create_patient()
        pid = create_resp.data['data']['id']
        other_user = make_user('other@test.com', phone='+919000000002')
        FamilyProfile.objects.get_or_create(user=other_user)
        token2 = get_tokens(self.client, 'other@test.com')
        auth(self.client, token2)
        resp = self.client.get(f'/api/v1/patients/{pid}/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class PatientVitalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('vital@test.com', phone='+919000000003')
        self.profile = FamilyProfile.objects.get(user=self.user)
        token = get_tokens(self.client, 'vital@test.com')
        auth(self.client, token)
        resp = self.client.post('/api/v1/patients/', {
            'first_name': 'Jane', 'last_name': 'Doe', 'blood_group': 'B+',
        })
        self.patient_id = resp.data['data']['id']

    def test_record_vital(self):
        resp = self.client.post(f'/api/v1/patients/{self.patient_id}/vitals/', {
            'heart_rate': 72,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'oxygen_saturation': 98,
            'temperature': '36.6',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['data']['heart_rate'], 72)

    def test_list_vitals(self):
        self.client.post(f'/api/v1/patients/{self.patient_id}/vitals/', {'heart_rate': 70})
        resp = self.client.get(f'/api/v1/patients/{self.patient_id}/vitals/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['data']), 1)

    def test_delete_vital(self):
        create_resp = self.client.post(
            f'/api/v1/patients/{self.patient_id}/vitals/', {'heart_rate': 75}
        )
        vid = create_resp.data['data']['id']
        resp = self.client.delete(f'/api/v1/patients/{self.patient_id}/vitals/{vid}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_invalid_bp_validation(self):
        resp = self.client.post(f'/api/v1/patients/{self.patient_id}/vitals/', {
            'blood_pressure_systolic': 80,
            'blood_pressure_diastolic': 120,  # diastolic > systolic — invalid
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bp_requires_both_fields(self):
        resp = self.client.post(f'/api/v1/patients/{self.patient_id}/vitals/', {
            'blood_pressure_systolic': 120,
            # missing diastolic
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class PatientInsuranceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('insure@test.com', phone='+919000000004')
        self.profile = FamilyProfile.objects.get(user=self.user)
        token = get_tokens(self.client, 'insure@test.com')
        auth(self.client, token)
        resp = self.client.post('/api/v1/patients/', {
            'first_name': 'Sam', 'last_name': 'Smith', 'blood_group': 'AB+',
        })
        self.patient_id = resp.data['data']['id']

    def _add_insurance(self):
        return self.client.post(f'/api/v1/patients/{self.patient_id}/insurance/', {
            'insurance_type': 'PRIVATE',
            'provider_name': 'Star Health',
            'policy_number': 'POL123456',
            'policy_holder_name': 'Sam Smith',
            'valid_from': '2025-01-01',
            'valid_until': '2026-01-01',
        })

    def test_add_insurance(self):
        resp = self._add_insurance()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['data']['provider_name'], 'Star Health')

    def test_list_insurance(self):
        self._add_insurance()
        resp = self.client.get(f'/api/v1/patients/{self.patient_id}/insurance/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['data']), 1)

    def test_duplicate_active_insurance_rejected(self):
        self._add_insurance()
        resp = self._add_insurance()
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_insurance(self):
        create_resp = self._add_insurance()
        iid = create_resp.data['data']['id']
        resp = self.client.patch(
            f'/api/v1/patients/{self.patient_id}/insurance/{iid}/',
            {'provider_name': 'HDFC Ergo'},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['provider_name'], 'HDFC Ergo')

    def test_deactivate_insurance(self):
        create_resp = self._add_insurance()
        iid = create_resp.data['data']['id']
        resp = self.client.delete(f'/api/v1/patients/{self.patient_id}/insurance/{iid}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        insurance = PatientInsurance.objects.get(id=iid)
        self.assertFalse(insurance.is_active)

    def test_invalid_date_range(self):
        resp = self.client.post(f'/api/v1/patients/{self.patient_id}/insurance/', {
            'insurance_type': 'PRIVATE',
            'provider_name': 'Test',
            'valid_from': '2026-01-01',
            'valid_until': '2025-01-01',  # before valid_from
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class PatientSignalTests(TestCase):
    """Verify that creating a FamilyMember auto-creates a Patient."""

    def setUp(self):
        self.user = make_user('signal@test.com', phone='+919000000005')
        self.profile = FamilyProfile.objects.get(user=self.user)

    def test_auto_patient_created_on_family_member(self):
        member = FamilyMember.objects.create(
            family_profile=self.profile,
            first_name='Auto',
            last_name='Patient',
            relationship='CHILD',
        )
        self.assertTrue(Patient.objects.filter(family_member=member).exists())

    def test_auto_patient_not_duplicated_on_update(self):
        member = FamilyMember.objects.create(
            family_profile=self.profile,
            first_name='Auto',
            last_name='Patient',
            relationship='CHILD',
        )
        member.first_name = 'Updated'
        member.save()
        self.assertEqual(Patient.objects.filter(family_member=member).count(), 1)
