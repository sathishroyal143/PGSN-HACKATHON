"""Read-side queries and dashboard aggregation for Analytics."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.bookings.models import Booking
from apps.payments import constants as payment_constants
from apps.payments.models import Payment

from .repositories import AnalyticsEventRepository, InsightRepository, ReportRepository

User = get_user_model()


def _date_range(date_from=None, date_to=None):
    end = date_to or timezone.localdate()
    start = date_from or (end - timedelta(days=29))
    return start, end


class DashboardSelectors:
    @staticmethod
    def summary(date_from=None, date_to=None):
        start, end = _date_range(date_from, date_to)
        bookings = Booking.objects.filter(
            is_deleted=False, created_at__date__range=(start, end),
        )
        payments = Payment.objects.filter(
            status=payment_constants.PAYMENT_STATUS_SUCCESS,
            created_at__date__range=(start, end),
        )
        users = User.objects.filter(created_at__date__range=(start, end))

        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='COMPLETED').count()
        cancelled_bookings = bookings.filter(status='CANCELLED').count()

        booking_series = {
            row['day']: row['count']
            for row in bookings.annotate(day=TruncDate('created_at'))
            .values('day').annotate(count=Count('id')).order_by('day')
        }
        revenue_series = {
            row['day']: row['amount'] or Decimal('0')
            for row in payments.annotate(day=TruncDate('created_at'))
            .values('day').annotate(amount=Sum('amount')).order_by('day')
        }
        trend = []
        current = start
        while current <= end:
            trend.append({
                'date': current.isoformat(),
                'bookings': booking_series.get(current, 0),
                'revenue': float(revenue_series.get(current, 0)),
            })
            current += timedelta(days=1)

        return {
            'range': {'date_from': start, 'date_to': end},
            'totals': {
                'users': User.objects.count(),
                'new_users': users.count(),
                'bookings': total_bookings,
                'completed_bookings': completed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'completion_rate': round(
                    completed_bookings * 100 / total_bookings, 2,
                ) if total_bookings else 0,
                'revenue': total_revenue,
                'average_booking_value': round(
                    total_revenue / total_bookings, 2,
                ) if total_bookings else Decimal('0'),
            },
            'booking_statuses': list(
                bookings.values('status').annotate(count=Count('id')).order_by('status')
            ),
            'user_roles': list(
                User.objects.values('role').annotate(count=Count('id')).order_by('role')
            ),
            'trend': trend,
        }


class AnalyticsEventSelectors:
    @staticmethod
    def list(**filters):
        return AnalyticsEventRepository.list(**filters)


class ReportSelectors:
    @staticmethod
    def list():
        return ReportRepository.list()

    @staticmethod
    def get(report_id):
        return ReportRepository.get(report_id)


class InsightSelectors:
    @staticmethod
    def active():
        return InsightRepository.active()
