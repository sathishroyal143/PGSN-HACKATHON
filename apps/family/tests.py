"""
Gate 3 — Family API Tests
Tests all family endpoints end-to-end via Django test client.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.family.models import FamilyProfile, FamilyMember, EmergencyContact


class FamilyTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/v1/family/profile/'
        self.profile_update_url = '/api/v1/family/profile/update/'
        self.profile_summary_url = '/api/v1/family/profile/summary/'
        self.members_url = '/api/v1/family/members/'
        self.contacts_url = '/api/v1/family/emergency-contacts/'

        self.user = User.objects.create_user(
            email='family@carebridge.com',
            password='TestPass@123',
            phone_number='+919876543210',
            first_name='Family',
            last_name='User',
            role='FAMILY',
        )
        self.companion = User.objects.create_user(
            email='companion@carebridge.com',
            password='TestPass@123',
            phone_number='+919876543213',
            first_name='Care',
            last_name='Companion',
            role='COMPANION',
        )

    def _auth(self, email='family@carebridge.com', password='TestPass@123'):
        res = self.client.post('/api/v1/auth/login/', {
            'email': email, 'password': password
        }, format='json')
        token = res.data.get('data', {}).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _member_data(self, suffix=''):
        return {
            'first_name': f'John{suffix}',
            'last_name': 'Doe',
            'relationship': 'PARENT',
            'date_of_birth': '1960-01-15',
            'gender': 'MALE',
            'phone_number': '+919876543220',
            'is_primary_patient': True,
        }

    def _contact_data(self, suffix=''):
        return {
            'name': f'Emergency Contact{suffix}',
            'relationship': 'SIBLING',
            'phone_number': '+919876543230',
            'email': f'emergency{suffix}@test.com',
            'is_primary': True,
        }


class TestFamilyProfile(FamilyTestBase):
    def test_get_profile_success(self):
        self._auth()
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('preferred_language', data)

    def test_get_profile_requires_auth(self):
        self.client.credentials()
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_companion_forbidden(self):
        self._auth('companion@carebridge.com')
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_patch(self):
        self._auth()
        res = self.client.patch(self.profile_update_url, {
            'preferred_language': 'Hindi',
            'preferred_contact_method': 'SMS',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        profile = FamilyProfile.objects.get(user=self.user)
        self.assertEqual(profile.preferred_language, 'Hindi')

    def test_update_profile_put(self):
        self._auth()
        res = self.client.put(self.profile_update_url, {
            'preferred_language': 'Tamil',
            'preferred_contact_method': 'EMAIL',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_profile_summary(self):
        self._auth()
        res = self.client.get(self.profile_summary_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestFamilyMembers(FamilyTestBase):
    def test_list_members_empty(self):
        self._auth()
        res = self.client.get(self.members_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data', []), [])

    def test_add_member_success(self):
        self._auth()
        res = self.client.post(self.members_url, self._member_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.data.get('data', {})
        self.assertEqual(data.get('first_name'), 'John')

    def test_add_member_requires_auth(self):
        self.client.credentials()
        res = self.client.post(self.members_url, self._member_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_member_companion_forbidden(self):
        self._auth('companion@carebridge.com')
        res = self.client.post(self.members_url, self._member_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_member_success(self):
        self._auth()
        create_res = self.client.post(self.members_url, self._member_data(), format='json')
        member_id = create_res.data.get('data', {}).get('id')
        res = self.client.get(f'{self.members_url}{member_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_member_patch(self):
        self._auth()
        create_res = self.client.post(self.members_url, self._member_data(), format='json')
        member_id = create_res.data.get('data', {}).get('id')
        res = self.client.patch(f'{self.members_url}{member_id}/', {
            'first_name': 'UpdatedJohn',
            'blood_group': 'O+',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data', {}).get('first_name'), 'UpdatedJohn')

    def test_update_member_put(self):
        self._auth()
        create_res = self.client.post(self.members_url, self._member_data(), format='json')
        member_id = create_res.data.get('data', {}).get('id')
        res = self.client.put(f'{self.members_url}{member_id}/', {
            'first_name': 'PutJohn',
            'last_name': 'Doe',
            'relationship': 'PARENT',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_member_success(self):
        self._auth()
        create_res = self.client.post(self.members_url, self._member_data(), format='json')
        member_id = create_res.data.get('data', {}).get('id')
        res = self.client.delete(f'{self.members_url}{member_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_members_after_add(self):
        self._auth()
        self.client.post(self.members_url, self._member_data(), format='json')
        res = self.client.get(self.members_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('data', [])), 1)

    def test_add_member_missing_required_fields(self):
        self._auth()
        res = self.client.post(self.members_url, {'first_name': 'Only'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestEmergencyContacts(FamilyTestBase):
    def test_list_contacts_empty(self):
        self._auth()
        res = self.client.get(self.contacts_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data', []), [])

    def test_add_contact_success(self):
        self._auth()
        res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.data.get('data', {})
        self.assertEqual(data.get('name'), 'Emergency Contact')

    def test_add_contact_requires_auth(self):
        self.client.credentials()
        res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_contact_companion_forbidden(self):
        self._auth('companion@carebridge.com')
        res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_contact_success(self):
        self._auth()
        create_res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        contact_id = create_res.data.get('data', {}).get('id')
        res = self.client.get(f'{self.contacts_url}{contact_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_contact_patch(self):
        self._auth()
        create_res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        contact_id = create_res.data.get('data', {}).get('id')
        res = self.client.patch(f'{self.contacts_url}{contact_id}/', {
            'name': 'Updated Contact',
            'is_primary': False,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data', {}).get('name'), 'Updated Contact')

    def test_update_contact_put(self):
        self._auth()
        create_res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        contact_id = create_res.data.get('data', {}).get('id')
        res = self.client.put(f'{self.contacts_url}{contact_id}/', {
            'name': 'Put Contact',
            'relationship': 'FRIEND',
            'phone_number': '+919876543230',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_contact_success(self):
        self._auth()
        create_res = self.client.post(self.contacts_url, self._contact_data(), format='json')
        contact_id = create_res.data.get('data', {}).get('id')
        res = self.client.delete(f'{self.contacts_url}{contact_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_contacts_after_add(self):
        self._auth()
        self.client.post(self.contacts_url, self._contact_data(), format='json')
        res = self.client.get(self.contacts_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('data', [])), 1)

    def test_add_contact_missing_phone(self):
        self._auth()
        res = self.client.post(self.contacts_url, {'name': 'No Phone', 'relationship': 'FRIEND'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_primary_contact_enforcement(self):
        """Only one contact can be primary at a time."""
        self._auth()
        self.client.post(self.contacts_url, self._contact_data(), format='json')
        second = {**self._contact_data(), 'phone_number': '+919876543231', 'email': 'second@test.com', 'is_primary': True}
        res = self.client.post(self.contacts_url, second, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Only one should be primary
        primary_count = EmergencyContact.objects.filter(
            family_profile__user=self.user, is_primary=True
        ).count()
        self.assertEqual(primary_count, 1)
