"""
Selector layer for Users module.
Handles complex read-only queries and data retrieval operations.
"""

from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields
from django.utils import timezone

from .models import User, UserActivity, UserRole
from .repositories import UserRepository, UserActivityRepository


class UserSelector:
    """Selector for User queries"""
    
    @staticmethod
    def get_user_profile(user_id):
        """
        Get complete user profile with related data.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance with prefetched relations or None
        """
        try:
            return User.objects.prefetch_related('activities').get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_credentials(email, password):
        """
        Get user by email and verify password.
        
        Args:
            email: Email address
            password: Password
            
        Returns:
            User instance if credentials are valid, None otherwise
        """
        user = UserRepository.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_user_statistics(user):
        """
        Get statistics for a user.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with user statistics
        """
        activity_count = UserActivity.objects.filter(user=user).count()
        recent_login = UserActivity.objects.filter(
            user=user,
            activity_type='LOGIN'
        ).order_by('-created_at').first()
        
        return {
            'total_activities': activity_count,
            'last_login': recent_login.created_at if recent_login else None,
            'account_age_days': (timezone.now().date() - user.created_at.date()).days,
            'is_verified': user.is_verified,
            'profile_completion': user.is_profile_complete,
        }
    
    @staticmethod
    def get_users_for_listing(filters=None, page=1, page_size=20):
        """
        Get paginated users list with filters.
        
        Args:
            filters: Dictionary of filter parameters
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Dictionary with users and pagination info
        """
        queryset = UserRepository.get_all_users(filters)
        
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        users = queryset[start:end]
        
        return {
            'users': users,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
        }
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get dashboard statistics for all users.
        
        Returns:
            Dictionary with dashboard statistics
        """
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(
            is_email_verified=True,
            is_phone_verified=True
        ).count()
        
        # Users by role
        role_counts = User.objects.values('role').annotate(count=Count('id'))
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_registrations = User.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'inactive_users': total_users - active_users,
            'role_distribution': list(role_counts),
            'recent_registrations': recent_registrations,
        }
    
    @staticmethod
    def get_family_users():
        """
        Get all family users.
        
        Returns:
            QuerySet of family users
        """
        return UserRepository.get_users_by_role(UserRole.FAMILY)
    
    @staticmethod
    def get_companion_users():
        """
        Get all companion users.
        
        Returns:
            QuerySet of companion users
        """
        return UserRepository.get_users_by_role(UserRole.COMPANION)
    
    @staticmethod
    def get_available_companions(city=None, state=None):
        """
        Get available companions by location.
        
        Args:
            city: City name (optional)
            state: State name (optional)
            
        Returns:
            QuerySet of available companions
        """
        queryset = User.objects.filter(
            role=UserRole.COMPANION,
            is_active=True,
            is_email_verified=True,
            is_phone_verified=True,
            is_profile_complete=True
        )
        
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        if state:
            queryset = queryset.filter(state__iexact=state)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def search_users_advanced(search_params):
        """
        Advanced user search with multiple parameters.
        
        Args:
            search_params: Dictionary with search parameters
            
        Returns:
            QuerySet of users
        """
        queryset = User.objects.filter(is_active=True)
        
        if 'query' in search_params and search_params['query']:
            query = search_params['query']
            queryset = queryset.filter(
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(phone_number__icontains=query)
            )
        
        if 'role' in search_params:
            queryset = queryset.filter(role=search_params['role'])
        
        if 'city' in search_params:
            queryset = queryset.filter(city__iexact=search_params['city'])
        
        if 'state' in search_params:
            queryset = queryset.filter(state__iexact=search_params['state'])
        
        if 'is_verified' in search_params:
            queryset = queryset.filter(
                is_email_verified=search_params['is_verified'],
                is_phone_verified=search_params['is_verified']
            )
        
        if 'age_min' in search_params or 'age_max' in search_params:
            today = timezone.now().date()
            
            if 'age_min' in search_params:
                age_min = search_params['age_min']
                max_birth_date = today.replace(year=today.year - age_min)
                queryset = queryset.filter(date_of_birth__lte=max_birth_date)
            
            if 'age_max' in search_params:
                age_max = search_params['age_max']
                min_birth_date = today.replace(year=today.year - age_max)
                queryset = queryset.filter(date_of_birth__gte=min_birth_date)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_user_activity_summary(user, days=30):
        """
        Get user activity summary for specified days.
        
        Args:
            user: User instance
            days: Number of days to analyze
            
        Returns:
            Dictionary with activity summary
        """
        date_threshold = timezone.now() - timezone.timedelta(days=days)
        
        activities = UserActivity.objects.filter(
            user=user,
            created_at__gte=date_threshold
        )
        
        activity_by_type = activities.values('activity_type').annotate(
            count=Count('id')
        )
        
        return {
            'total_activities': activities.count(),
            'activity_breakdown': list(activity_by_type),
            'period_days': days,
        }
    
    @staticmethod
    def check_user_eligibility(user):
        """
        Check if user is eligible for various actions.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with eligibility checks
        """
        return {
            'can_book_service': (
                user.is_active and
                user.is_verified and
                user.role == UserRole.FAMILY and
                not user.is_blocked
            ),
            'can_accept_bookings': (
                user.is_active and
                user.is_verified and
                user.role == UserRole.COMPANION and
                user.is_profile_complete and
                not user.is_blocked
            ),
            'can_access_admin': (
                user.is_active and
                user.is_staff and
                user.role == UserRole.ADMIN
            ),
            'requires_verification': not user.is_verified,
            'requires_profile_completion': not user.is_profile_complete,
        }
    
    @staticmethod
    def get_nearby_users(latitude, longitude, radius_km=10, role=None):
        """
        Get users near a location (basic distance calculation).
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            role: User role filter (optional)
            
        Returns:
            QuerySet of nearby users
        """
        # Simple bounding box calculation (not precise but fast)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        
        import math
        
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(float(latitude))))
        
        queryset = User.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=float(latitude) - lat_delta,
            latitude__lte=float(latitude) + lat_delta,
            longitude__gte=float(longitude) - lon_delta,
            longitude__lte=float(longitude) + lon_delta,
        )
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset


class UserActivitySelector:
    """Selector for UserActivity queries"""
    
    @staticmethod
    def get_activity_timeline(user, limit=50):
        """
        Get user activity timeline.
        
        Args:
            user: User instance
            limit: Number of activities
            
        Returns:
            QuerySet of activities
        """
        return UserActivityRepository.get_user_activities(user, limit)
    
    @staticmethod
    def get_login_history(user, limit=20):
        """
        Get user login history.
        
        Args:
            user: User instance
            limit: Number of login records
            
        Returns:
            QuerySet of login activities
        """
        return UserActivity.objects.filter(
            user=user,
            activity_type='LOGIN'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_system_activity_stats(days=7):
        """
        Get system-wide activity statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with activity statistics
        """
        date_threshold = timezone.now() - timezone.timedelta(days=days)
        
        activities = UserActivity.objects.filter(created_at__gte=date_threshold)
        
        activity_counts = activities.values('activity_type').annotate(
            count=Count('id')
        )
        
        daily_activity = activities.extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(count=Count('id'))
        
        return {
            'total_activities': activities.count(),
            'activity_by_type': list(activity_counts),
            'daily_activity': list(daily_activity),
            'period_days': days,
        }
