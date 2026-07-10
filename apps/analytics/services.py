"""Application services for Analytics."""
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, Sum

from apps.bookings.models import Booking
from apps.companions.models import CompanionProfile
from apps.payments import constants as payment_constants
from apps.payments.models import Payment

from . import constants
from .repositories import AnalyticsEventRepository, InsightRepository, ReportRepository
from .selectors import DashboardSelectors

User = get_user_model()


class AnalyticsEventService:
    @staticmethod
    def track(**data):
        return AnalyticsEventRepository.create(**data)


class ReportService:
    @classmethod
    def generate(cls, requested_by_id, **data):
        report = ReportRepository.create(requested_by_id=requested_by_id, **data)
        ReportRepository.mark_processing(report)
        try:
            output = cls._build(report)
            ReportRepository.mark_completed(report, output)
        except Exception as exc:
            ReportRepository.mark_failed(report, exc)
        report.refresh_from_db()
        return report

    @staticmethod
    def _build(report):
        date_filter = {
            'created_at__date__range': (report.date_from, report.date_to),
        }
        if report.report_type == constants.REPORT_BOOKINGS:
            queryset = Booking.objects.filter(is_deleted=False, **date_filter)
            return {
                'total': queryset.count(),
                'by_status': list(
                    queryset.values('status').annotate(count=Count('id')).order_by('status')
                ),
                'quoted_value': queryset.aggregate(total=Sum('quoted_price'))['total'] or 0,
                'average_match_score': queryset.aggregate(value=Avg('ai_match_score'))['value'],
            }
        if report.report_type == constants.REPORT_REVENUE:
            queryset = Payment.objects.filter(
                status=payment_constants.PAYMENT_STATUS_SUCCESS, **date_filter,
            )
            return {
                'transactions': queryset.count(),
                'total_revenue': queryset.aggregate(total=Sum('amount'))['total'] or 0,
                'by_method': list(
                    queryset.values('method').annotate(
                        count=Count('id'), amount=Sum('amount'),
                    ).order_by('method')
                ),
            }
        if report.report_type == constants.REPORT_USER_GROWTH:
            queryset = User.objects.filter(**date_filter)
            return {
                'new_users': queryset.count(),
                'by_role': list(
                    queryset.values('role').annotate(count=Count('id')).order_by('role')
                ),
            }
        if report.report_type == constants.REPORT_COMPANION_PERFORMANCE:
            queryset = CompanionProfile.objects.select_related('user').annotate(
                booking_count=Count(
                    'user__bookings_as_companion',
                    filter=Q(
                        user__bookings_as_companion__created_at__date__range=(
                            report.date_from, report.date_to,
                        ),
                    ),
                ),
            )
            return {
                'companions': list(queryset.values(
                    'id', 'user__email', 'average_rating', 'ai_trust_score',
                    'booking_count',
                ))
            }
        raise ValueError('Unsupported report type.')


class InsightService:
    @staticmethod
    def generate(date_from=None, date_to=None):
        dashboard = DashboardSelectors.summary(date_from, date_to)
        totals = dashboard['totals']
        insights = []

        cancellation_rate = (
            totals['cancelled_bookings'] * 100 / totals['bookings']
            if totals['bookings'] else 0
        )
        if cancellation_rate >= 20:
            insights.append({
                'title': 'High booking cancellation rate',
                'description': (
                    f'{cancellation_rate:.1f}% of bookings in this period were cancelled. '
                    'Review cancellation reasons and companion availability.'
                ),
                'category': constants.INSIGHT_OPERATIONS,
                'severity': constants.SEVERITY_WARNING,
                'metric_name': 'cancellation_rate',
                'metric_value': cancellation_rate,
            })

        if totals['bookings'] and totals['completion_rate'] < 60:
            insights.append({
                'title': 'Booking completion needs attention',
                'description': (
                    f"Only {totals['completion_rate']:.1f}% of bookings were completed "
                    'during the selected period.'
                ),
                'category': constants.INSIGHT_QUALITY,
                'severity': constants.SEVERITY_CRITICAL,
                'metric_name': 'completion_rate',
                'metric_value': totals['completion_rate'],
            })

        insights.append({
            'title': 'Revenue snapshot',
            'description': (
                f"Successful payments generated INR {totals['revenue']} in this period."
            ),
            'category': constants.INSIGHT_REVENUE,
            'severity': constants.SEVERITY_INFO,
            'metric_name': 'revenue',
            'metric_value': totals['revenue'],
        })
        insights.append({
            'title': 'User growth snapshot',
            'description': f"{totals['new_users']} new users joined in this period.",
            'category': constants.INSIGHT_USERS,
            'severity': constants.SEVERITY_INFO,
            'metric_name': 'new_users',
            'metric_value': totals['new_users'],
        })

        return InsightRepository.replace_generated(insights)
