"""
Repository layer for Users module.
Handles all database operations with reusable query methods.
"""

from django.db import transaction
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import User, UserActivity, UserRole


class UserRepository:
    """Repository for User model database operations"""
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_email(email):
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User instance or None
        """
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_phone(phone_number):
        """
        Get user by phone number.
        
        Args:
            phone_number: Phone number
            
        Returns:
            User instance or None
        """
        try:
            return User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def check_email_exists(email, exclude_user_id=None):
        """
        Check if email already exists.
        
        Args:
            email: Email address
            exclude_user_id: User ID to exclude from check
            
        Returns:
            Boolean
        """
        queryset = User.objects.filter(email__iexact=email)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        return queryset.exists()
    
    @staticmethod
    def check_phone_exists(phone_number, exclude_user_id=None):
        """
        Check if phone number already exists.
        
        Args:
            phone_number: Phone number
            exclude_user_id: User ID to exclude from check
            
        Returns:
            Boolean
        """
        queryset = User.objects.filter(phone_number=phone_number)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        return queryset.exists()
    
    @staticmethod
    @transaction.atomic
    def create_user(user_data=None, **kwargs):
        """
        Create a new user.
        Accepts either a dict: create_user({'email': ...}) or keyword args: create_user(email=...).
        """
        data = dict(user_data) if user_data else {}
        data.update(kwargs)
        password = data.pop('password', None)
        user = User.objects.create(**data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    @staticmethod
    @transaction.atomic
    def update_user(user, user_data):
        """
        Update user information.
        
        Args:
            user: User instance
            user_data: Dictionary containing fields to update
            
        Returns:
            Updated User instance
        """
        for field, value in user_data.items():
            if field != 'password':
                setattr(user, field, value)
        
        if 'password' in user_data:
            user.set_password(user_data['password'])
        
        user.save()
        return user
    
    @staticmethod
    @transaction.atomic
    def delete_user(user):
        """
        Soft delete user by marking as inactive.
        
        Args:
            user: User instance
            
        Returns:
            Boolean
        """
        user.is_active = False
        user.save(update_fields=['is_active'])
        return True
    
    @staticmethod
    def get_all_users(filters=None):
        """
        Get all users with optional filters.
        
        Args:
            filters: Dictionary of filter parameters
            
        Returns:
            QuerySet of users
        """
        queryset = User.objects.all()
        
        if filters:
            if 'role' in filters:
                queryset = queryset.filter(role=filters['role'])
            
            if 'is_active' in filters:
                queryset = queryset.filter(is_active=filters['is_active'])
            
            if 'is_verified' in filters:
                queryset = queryset.filter(
                    is_email_verified=filters['is_verified'],
                    is_phone_verified=filters['is_verified']
                )
            
            if 'search' in filters:
                search = filters['search']
                queryset = queryset.filter(
                    Q(email__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(phone_number__icontains=search)
                )
            
            if 'city' in filters:
                queryset = queryset.filter(city__iexact=filters['city'])
            
            if 'state' in filters:
                queryset = queryset.filter(state__iexact=filters['state'])
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_users_by_role(role):
        """
        Get users by role.
        
        Args:
            role: User role
            
        Returns:
            QuerySet of users
        """
        return User.objects.filter(role=role, is_active=True).order_by('-created_at')
    
    @staticmethod
    def get_active_users():
        """
        Get all active users.
        
        Returns:
            QuerySet of active users
        """
        return User.objects.filter(is_active=True).order_by('-created_at')
    
    @staticmethod
    def get_verified_users():
        """
        Get all verified users.
        
        Returns:
            QuerySet of verified users
        """
        return User.objects.filter(
            is_email_verified=True,
            is_phone_verified=True,
            is_active=True
        ).order_by('-created_at')
    
    @staticmethod
    def get_users_by_location(city=None, state=None):
        """
        Get users by location.
        
        Args:
            city: City name
            state: State name
            
        Returns:
            QuerySet of users
        """
        queryset = User.objects.filter(is_active=True)
        
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        if state:
            queryset = queryset.filter(state__iexact=state)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def search_users(query):
        """
        Search users by name, email, or phone.
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of users
        """
        return User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query),
            is_active=True
        ).order_by('-created_at')
    
    @staticmethod
    def get_user_count_by_role():
        """
        Get user count grouped by role.
        
        Returns:
            Dictionary with role counts
        """
        return User.objects.values('role').annotate(count=Count('id'))
    
    @staticmethod
    def get_recent_users(days=7, limit=10):
        """
        Get recently registered users.
        
        Args:
            days: Number of days to look back
            limit: Number of users to return
            
        Returns:
            QuerySet of recent users
        """
        date_threshold = timezone.now() - timezone.timedelta(days=days)
        return User.objects.filter(
            created_at__gte=date_threshold
        ).order_by('-created_at')[:limit]


class UserActivityRepository:
    """Repository for UserActivity model database operations"""
    
    @staticmethod
    @transaction.atomic
    def log_activity(user, activity_type, description, ip_address=None, user_agent=None, metadata=None):
        """
        Log user activity.
        
        Args:
            user: User instance
            activity_type: Type of activity
            description: Activity description
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            UserActivity instance
        """
        return UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent or "",
            metadata=metadata or {}
        )
    
    @staticmethod
    def get_user_activities(user, limit=50):
        """
        Get user activities.
        
        Args:
            user: User instance
            limit: Number of activities to return
            
        Returns:
            QuerySet of activities
        """
        return UserActivity.objects.filter(user=user).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_activities_by_type(user, activity_type):
        """
        Get user activities by type.
        
        Args:
            user: User instance
            activity_type: Activity type
            
        Returns:
            QuerySet of activities
        """
        return UserActivity.objects.filter(
            user=user,
            activity_type=activity_type
        ).order_by('-created_at')
    
    @staticmethod
    def get_recent_activities(days=7, limit=100):
        """
        Get recent activities across all users.
        
        Args:
            days: Number of days to look back
            limit: Number of activities to return
            
        Returns:
            QuerySet of activities
        """
        date_threshold = timezone.now() - timezone.timedelta(days=days)
        return UserActivity.objects.filter(
            created_at__gte=date_threshold
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def delete_old_activities(days=90):
        """
        Delete activities older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted activities
        """
        date_threshold = timezone.now() - timezone.timedelta(days=days)
        deleted_count, _ = UserActivity.objects.filter(
            created_at__lt=date_threshold
        ).delete()
        return deleted_count
