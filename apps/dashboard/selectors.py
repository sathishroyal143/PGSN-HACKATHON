"""Dashboard selectors — aggregate stats from existing models."""
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import timedelta


class DashboardSelectors:

    @staticmethod
    def family_stats(user_id):
        from apps.bookings.models import Booking
        from apps.patients.models import Patient
        from apps.notifications.models import Notification

        bookings = Booking.objects.filter(family_user_id=user_id)
        return {
            'total_patients': Patient.objects.filter(family_profile__user_id=user_id, is_deleted=False).count(),
            'total_bookings': bookings.count(),
            'active_bookings': bookings.filter(status__in=['CONFIRMED', 'IN_PROGRESS', 'COMPANION_ASSIGNED']).count(),
            'completed_bookings': bookings.filter(status='COMPLETED').count(),
            'unread_notifications': Notification.objects.filter(user_id=user_id, is_read=False).count(),
        }

    @staticmethod
    def companion_stats(user_id):
        from apps.bookings.models import Booking
        from apps.companions.models import CompanionProfile
        from apps.notifications.models import Notification

        bookings = Booking.objects.filter(companion_id=user_id)
        profile = CompanionProfile.objects.filter(user_id=user_id).first()
        
        return {
            'total_bookings': bookings.count(),
            'active_bookings': bookings.filter(status__in=['CONFIRMED', 'IN_PROGRESS', 'COMPANION_ASSIGNED']).count(),
            'completed_bookings': bookings.filter(status='COMPLETED').count(),
            'average_rating': round(profile.average_rating, 2) if profile else 0.00,
            'total_reviews': profile.total_reviews if profile else 0,
            'unread_notifications': Notification.objects.filter(user_id=user_id, is_read=False).count(),
        }

    @staticmethod
    def admin_stats():
        from apps.users.models import User
        from apps.bookings.models import Booking
        from apps.payments.models import Payment
        from apps.companions.models import CompanionProfile

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        revenue = Payment.objects.filter(status='CAPTURED').aggregate(total=Sum('amount'))['total'] or 0
        return {
            'total_users': User.objects.count(),
            'total_companions': CompanionProfile.objects.count(),
            'total_bookings': Booking.objects.count(),
            'bookings_this_week': Booking.objects.filter(created_at__date__gte=week_ago).count(),
            'total_revenue': float(revenue),
            'pending_bookings': Booking.objects.filter(status='PENDING').count(),
        }

    @staticmethod
    def recent_bookings(user_id, role='family', limit=5):
        from apps.bookings.models import Booking
        from apps.bookings.serializers import BookingListSerializer

        if role == 'companion':
            qs = Booking.objects.filter(companion_id=user_id).order_by('-created_at')[:limit]
        else:
            qs = Booking.objects.filter(family_user_id=user_id).order_by('-created_at')[:limit]
        return BookingListSerializer(qs, many=True).data
