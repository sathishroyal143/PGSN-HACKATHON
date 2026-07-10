"""Gate 3 — Payments API Tests."""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.family.models import FamilyProfile
from apps.patients.models import Patient
from apps.services.models import ServiceType, ServicePackage, ServicePricing
from apps.companions.models import CompanionProfile
from apps.bookings.models import Booking
from apps.payments.models import Wallet, Payment


def make_user(email, role='FAMILY', phone='+919800000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


def make_booking(family, companion, patient):
    st = ServiceType.objects.create(name='Pay Visit', code='PAY_VISIT', status='ACTIVE')
    pkg = ServicePackage.objects.create(
        service_type=st, name='Pay Basic', slug='pay-basic', status='ACTIVE',
    )
    ServicePricing.objects.create(
        package=pkg, pricing_type='FIXED', base_price=1000, effective_from='2025-01-01',
    )
    start = timezone.now() + timedelta(hours=2)
    return Booking.objects.create(
        family_user=family, patient=patient, companion=companion,
        service_package=pkg, status='COMPLETED',
        scheduled_start=start, scheduled_end=start + timedelta(hours=4),
        pickup_address='Test Address',
    ), pkg


class PaymentTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('pay_family@test.com', role='FAMILY', phone='+919800000001')
        self.companion_user = make_user('pay_companion@test.com', role='COMPANION', phone='+919800000002')
        self.admin = User.objects.create_superuser(
            email='pay_admin@test.com', password='TestPass@123',
            phone_number='+919800000003', first_name='Admin', last_name='User',
        )
        FamilyProfile.objects.get_or_create(user=self.family)
        CompanionProfile.objects.create(user=self.companion_user, status='ACTIVE')
        self.patient = Patient.objects.create(
            family_user=self.family, first_name='Pay', last_name='Patient',
        )
        self.booking, self.package = make_booking(self.family, self.companion_user, self.patient)

    def _auth(self, email='pay_family@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('pay_admin@test.com')


class TestWallet(PaymentTestBase):
    def test_get_wallet(self):
        self._auth()
        res = self.client.get('/api/v1/payments/wallet/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('data', {})
        self.assertIn('balance', data)

    def test_wallet_auto_created(self):
        self._auth()
        self.client.get('/api/v1/payments/wallet/')
        self.assertTrue(Wallet.objects.filter(user=self.family).exists())

    def test_wallet_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/payments/wallet/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wallet_transactions_list(self):
        self._auth()
        res = self.client.get('/api/v1/payments/wallet/transactions/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestPaymentList(PaymentTestBase):
    def test_list_payments(self):
        self._auth()
        res = self.client.get('/api/v1/payments/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_payments_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/payments/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_payments(self):
        Payment.objects.create(
            booking=self.booking, user=self.family,
            amount=Decimal('1000.00'), status='PENDING',
        )
        self._auth()
        res = self.client.get('/api/v1/payments/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for p in res.data.get('data', []):
            self.assertNotEqual(p.get('user'), str(self.companion_user.id))


class TestInvoice(PaymentTestBase):
    def test_list_invoices(self):
        self._auth()
        res = self.client.get('/api/v1/payments/invoices/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_invoice_by_booking(self):
        self._auth()
        res = self.client.get(f'/api/v1/payments/invoices/booking/{self.booking.id}/')
        self.assertIn(res.status_code, [200, 404])

    def test_invoice_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/payments/invoices/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPaymentVerify(PaymentTestBase):
    def test_verify_payment_invalid_signature(self):
        payment = Payment.objects.create(
            booking=self.booking, user=self.family,
            amount=Decimal('1000.00'), status='PENDING',
            gateway_order_id='order_test123',
        )
        self._auth()
        res = self.client.post(f'/api/v1/payments/{payment.id}/verify/', {
            'razorpay_order_id': 'order_test123',
            'razorpay_payment_id': 'pay_test123',
            'razorpay_signature': 'invalid_signature',
        }, format='json')
        self.assertIn(res.status_code, [400, 422])
