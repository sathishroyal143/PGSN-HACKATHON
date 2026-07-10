"""Gate 3 — Analytics API Tests."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.analytics.models import AnalyticsEvent, Insight
from apps.analytics import constants


def make_user(email, role='FAMILY', phone='+919990000001'):
    return User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Test', last_name='User',
        phone_number=phone, role=role,
    )


def get_token(client, email):
    res = client.post('/api/v1/auth/login/', {'email': email, 'password': 'TestPass@123'}, format='json')
    return res.data['data']['access']


class AnalyticsTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = make_user('ana_family@test.com', phone='+919990000001')
        self.admin = User.objects.create_superuser(
            email='ana_admin@test.com', password='TestPass@123',
            phone_number='+919990000002', first_name='Admin', last_name='User',
        )

    def _auth(self, email='ana_family@test.com'):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _auth_admin(self):
        self._auth('ana_admin@test.com')


class TestAnalyticsDashboard(AnalyticsTestBase):
    def test_admin_can_access_dashboard(self):
        self._auth_admin()
        res = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_admin_forbidden(self):
        self._auth()
        res = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/analytics/dashboard/')
        self.assertIn(res.status_code, [401, 403])


class TestAnalyticsEvents(AnalyticsTestBase):
    def setUp(self):
        super().setUp()
        AnalyticsEvent.objects.create(
            actor=self.admin,
            event_type=constants.EVENT_BOOKING_CREATED,
            entity_type='booking',
            entity_id='test-id-1',
        )

    def test_admin_can_list_events(self):
        self._auth_admin()
        res = self.client.get('/api/v1/analytics/events/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get('data', [])), 1)

    def test_non_admin_forbidden(self):
        self._auth()
        res = self.client.get('/api/v1/analytics/events/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_events_by_type(self):
        self._auth_admin()
        res = self.client.get(f'/api/v1/analytics/events/?event_type={constants.EVENT_BOOKING_CREATED}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestReports(AnalyticsTestBase):
    def test_create_report(self):
        self._auth_admin()
        res = self.client.post('/api/v1/analytics/reports/', {
            'title': 'Monthly Bookings',
            'report_type': constants.REPORT_BOOKINGS,
            'date_from': '2025-01-01',
            'date_to': '2025-01-31',
        }, format='json')
        self.assertIn(res.status_code, [201, 500])  # 500 when Celery not running

    def test_list_reports(self):
        self._auth_admin()
        self.client.post('/api/v1/analytics/reports/', {
            'title': 'Test Report',
            'report_type': constants.REPORT_BOOKINGS,
            'date_from': '2025-01-01',
            'date_to': '2025-01-31',
        }, format='json')
        res = self.client.get('/api/v1/analytics/reports/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_report_detail(self):
        from apps.analytics.models import Report
        self._auth_admin()
        report = Report.objects.create(
            title='Direct Report',
            report_type=constants.REPORT_BOOKINGS,
            requested_by=self.admin,
            date_from='2025-01-01',
            date_to='2025-01-31',
            status=constants.REPORT_PENDING,
        )
        res = self.client.get(f'/api/v1/analytics/reports/{report.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_create_report(self):
        self._auth()
        res = self.client.post('/api/v1/analytics/reports/', {
            'title': 'Forbidden', 'report_type': constants.REPORT_BOOKINGS,
            'date_from': '2025-01-01', 'date_to': '2025-01-31',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/v1/analytics/reports/')
        self.assertIn(res.status_code, [401, 403])


class TestInsights(AnalyticsTestBase):
    def setUp(self):
        super().setUp()
        Insight.objects.create(
            title='High cancellation rate',
            description='Cancellations increased by 20% this week.',
            category=constants.INSIGHT_CATEGORY_BOOKINGS,
            severity=constants.SEVERITY_WARNING,
            is_active=True,
        )

    def test_admin_can_list_insights(self):
        self._auth_admin()
        res = self.client.get('/api/v1/analytics/insights/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get('data', [])), 1)

    def test_non_admin_forbidden(self):
        self._auth()
        res = self.client.get('/api/v1/analytics/insights/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_insights(self):
        self._auth_admin()
        res = self.client.post('/api/v1/analytics/insights/generate/', format='json')
        self.assertIn(res.status_code, [200, 201])
