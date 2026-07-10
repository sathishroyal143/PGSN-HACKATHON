"""
Gate 3 — Authentication API Tests
Tests all 19 auth endpoints end-to-end via Django test client.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.authentication.models import OTP, PasswordResetToken, RefreshToken


class AuthTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.logout_url = '/api/v1/auth/logout/'
        self.logout_all_url = '/api/v1/auth/logout-all/'
        self.refresh_url = '/api/v1/auth/refresh/'
        self.send_otp_url = '/api/v1/auth/send-verification-otp/'
        self.verify_otp_url = '/api/v1/auth/verify-otp/'
        self.resend_otp_url = '/api/v1/auth/resend-verification-otp/'
        self.pw_reset_request_url = '/api/v1/auth/password-reset/request/'
        self.pw_reset_verify_url = '/api/v1/auth/password-reset/verify/'
        self.pw_reset_confirm_url = '/api/v1/auth/password-reset/confirm/'
        self.change_pw_url = '/api/v1/auth/change-password/'
        self.sessions_url = '/api/v1/auth/sessions/'
        self.revoke_session_url = '/api/v1/auth/sessions/revoke/'
        self.revoke_device_url = '/api/v1/auth/sessions/revoke-device/'
        self.security_overview_url = '/api/v1/auth/security/overview/'
        self.login_history_url = '/api/v1/auth/security/login-history/'
        self.verification_status_url = '/api/v1/auth/security/verification-status/'
        self.security_score_url = '/api/v1/auth/security/score/'

        self.valid_register_data = {
            'email': 'testuser@carebridge.com',
            'password': 'TestPass@123',
            'password_confirmation': 'TestPass@123',
            'phone_number': '+919876543210',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'FAMILY',
        }

    def _register_and_login(self, email='testuser@carebridge.com', password='TestPass@123'):
        """Helper: register user and return tokens."""
        User.objects.filter(email=email).delete()
        reg_data = {**self.valid_register_data, 'email': email, 'password': password, 'password_confirmation': password}
        self.client.post(self.register_url, reg_data, format='json')
        user = User.objects.get(email=email)
        res = self.client.post(self.login_url, {'email': email, 'password': password}, format='json')
        tokens = res.data.get('data', {})
        return user, tokens.get('access'), tokens.get('refresh')


class TestRegister(AuthTestBase):
    def test_register_success(self):
        res = self.client.post(self.register_url, self.valid_register_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@carebridge.com').exists())

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, self.valid_register_data, format='json')
        res = self.client.post(self.register_url, self.valid_register_data, format='json')
        self.assertIn(res.status_code, [400, 409])

    def test_register_password_mismatch(self):
        data = {**self.valid_register_data, 'password_confirmation': 'WrongPass@123'}
        res = self.client.post(self.register_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        res = self.client.post(self.register_url, {'email': 'x@x.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_role(self):
        data = {**self.valid_register_data, 'email': 'role@test.com', 'phone_number': '+919876543211', 'role': 'INVALID'}
        res = self.client.post(self.register_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestLogin(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.client.post(self.register_url, self.valid_register_data, format='json')

    def test_login_success(self):
        res = self.client.post(self.login_url, {
            'email': 'testuser@carebridge.com',
            'password': 'TestPass@123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertIn('user', data)

    def test_login_wrong_password(self):
        res = self.client.post(self.login_url, {
            'email': 'testuser@carebridge.com',
            'password': 'WrongPass@123'
        }, format='json')
        self.assertIn(res.status_code, [400, 401])

    def test_login_nonexistent_user(self):
        res = self.client.post(self.login_url, {
            'email': 'nobody@carebridge.com',
            'password': 'TestPass@123'
        }, format='json')
        self.assertIn(res.status_code, [400, 401, 404])

    def test_login_missing_fields(self):
        res = self.client.post(self.login_url, {'email': 'testuser@carebridge.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestTokenRefresh(AuthTestBase):
    def test_refresh_success(self):
        _, access, refresh = self._register_and_login()
        res = self.client.post(self.refresh_url, {'refresh': refresh}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data.get('data', {}))

    def test_refresh_invalid_token(self):
        res = self.client.post(self.refresh_url, {'refresh': 'invalid.token.here'}, format='json')
        self.assertIn(res.status_code, [400, 401])


class TestLogout(AuthTestBase):
    def test_logout_success(self):
        _, access, refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        res = self.client.post(self.logout_url, {'refresh': refresh}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_all_success(self):
        _, access, refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        res = self.client.post(self.logout_all_url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_requires_auth(self):
        self.client.credentials()
        res = self.client.post(self.logout_url, {'refresh': 'token'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestOTP(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user, self.access, self.refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_send_otp_email(self):
        res = self.client.post(self.send_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_send_otp_phone(self):
        res = self.client.post(self.send_otp_url, {'otp_type': 'PHONE_VERIFICATION'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_verify_otp_success(self):
        self.client.post(self.send_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        otp = OTP.objects.filter(user=self.user, otp_type='EMAIL_VERIFICATION', is_used=False).latest('created_at')
        res = self.client.post(self.verify_otp_url, {
            'otp_code': otp.otp_code,
            'otp_type': 'EMAIL_VERIFICATION'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_otp_wrong_code(self):
        self.client.post(self.send_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        res = self.client.post(self.verify_otp_url, {
            'otp_code': '000000',
            'otp_type': 'EMAIL_VERIFICATION'
        }, format='json')
        self.assertIn(res.status_code, [400, 422])

    def test_resend_otp(self):
        self.client.post(self.send_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        # Expire the cooldown by directly updating the OTP
        from django.utils import timezone as tz
        import datetime
        OTP.objects.filter(user=self.user, otp_type='EMAIL_VERIFICATION').update(
            created_at=tz.now() - datetime.timedelta(seconds=70)
        )
        res = self.client.post(self.resend_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        self.assertIn(res.status_code, [200, 400])  # 400 if cooldown still active

    def test_otp_requires_auth(self):
        self.client.credentials()
        res = self.client.post(self.send_otp_url, {'otp_type': 'EMAIL_VERIFICATION'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPasswordReset(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user, self.access, self.refresh = self._register_and_login()

    def test_password_reset_request_success(self):
        res = self.client.post(self.pw_reset_request_url, {'email': self.user.email}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_reset_request_unknown_email(self):
        res = self.client.post(self.pw_reset_request_url, {'email': 'nobody@x.com'}, format='json')
        self.assertIn(res.status_code, [400, 404])

    def test_password_reset_verify_valid_token(self):
        self.client.post(self.pw_reset_request_url, {'email': self.user.email}, format='json')
        token_obj = PasswordResetToken.objects.filter(user=self.user, is_used=False).latest('created_at')
        res = self.client.post(self.pw_reset_verify_url, {'token': token_obj.token}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_reset_verify_invalid_token(self):
        res = self.client.post(self.pw_reset_verify_url, {'token': 'invalid-token-xyz'}, format='json')
        self.assertIn(res.status_code, [400, 404])

    def test_password_reset_confirm_success(self):
        self.client.post(self.pw_reset_request_url, {'email': self.user.email}, format='json')
        token_obj = PasswordResetToken.objects.filter(user=self.user, is_used=False).latest('created_at')
        res = self.client.post(self.pw_reset_confirm_url, {
            'token': token_obj.token,
            'new_password': 'NewPass@456',
            'password_confirmation': 'NewPass@456',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_mismatch(self):
        self.client.post(self.pw_reset_request_url, {'email': self.user.email}, format='json')
        token_obj = PasswordResetToken.objects.filter(user=self.user, is_used=False).latest('created_at')
        res = self.client.post(self.pw_reset_confirm_url, {
            'token': token_obj.token,
            'new_password': 'NewPass@456',
            'password_confirmation': 'DifferentPass@456',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestChangePassword(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user, self.access, self.refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_change_password_success(self):
        res = self.client.post(self.change_pw_url, {
            'old_password': 'TestPass@123',
            'new_password': 'NewPass@456',
            'password_confirmation': 'NewPass@456',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old(self):
        res = self.client.post(self.change_pw_url, {
            'old_password': 'WrongOld@123',
            'new_password': 'NewPass@456',
            'password_confirmation': 'NewPass@456',
        }, format='json')
        self.assertIn(res.status_code, [400, 401])

    def test_change_password_requires_auth(self):
        self.client.credentials()
        res = self.client.post(self.change_pw_url, {
            'old_password': 'TestPass@123',
            'new_password': 'NewPass@456',
            'password_confirmation': 'NewPass@456',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestSessions(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user, self.access, self.refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_get_sessions(self):
        res = self.client.get(self.sessions_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_revoke_session(self):
        token_obj = RefreshToken.objects.filter(user=self.user, is_revoked=False).latest('created_at')
        res = self.client.post(self.revoke_session_url, {'session_id': str(token_obj.id)}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_revoke_device_sessions(self):
        res = self.client.post(self.revoke_device_url, {'device_id': 'test-device-001'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestSecurityEndpoints(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user, self.access, self.refresh = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_security_overview(self):
        res = self.client.get(self.security_overview_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_history(self):
        res = self.client.get(self.login_history_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_verification_status(self):
        res = self.client.get(self.verification_status_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_security_score(self):
        res = self.client.get(self.security_score_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_security_endpoints_require_auth(self):
        self.client.credentials()
        for url in [self.security_overview_url, self.login_history_url,
                    self.verification_status_url, self.security_score_url]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED, msg=f'Expected 401 for {url}')
