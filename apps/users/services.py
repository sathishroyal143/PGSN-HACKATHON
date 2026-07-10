"""
Service layer for Users module.
Contains business logic for user operations.
"""

import logging
from django.db import transaction
from django.utils import timezone

from .constants import (
    ACTIVITY_TYPE_LOGIN,
    ACTIVITY_TYPE_LOGOUT,
    ACTIVITY_TYPE_PROFILE_UPDATE,
    ACTIVITY_TYPE_ACCOUNT_BLOCKED,
    ACTIVITY_TYPE_ACCOUNT_UNBLOCKED,
    USER_CREATED_SUCCESS,
    USER_UPDATED_SUCCESS,
    USER_BLOCKED_SUCCESS,
    USER_UNBLOCKED_SUCCESS,
)
from .exceptions import (
    UserAlreadyExistsException,
    PhoneAlreadyExistsException,
    UserNotFoundException,
    UserBlockedException,
    UserInactiveException,
    ProfileIncompleteException,
)
from .repositories import UserRepository, UserActivityRepository
from .validators import (
    validate_email,
    validate_phone_number,
    validate_date_of_birth,
    validate_profile_picture,
    validate_coordinates,
    validate_name,
)

logger = logging.getLogger('carebridge.users')


class UserService:
    """Service for user business logic"""
    
    @staticmethod
    @transaction.atomic
    def create_user(user_data, created_by=None):
        """
        Create a new user with validation.
        
        Args:
            user_data: Dictionary containing user data
            created_by: User who created this user (optional)
            
        Returns:
            User instance
            
        Raises:
            UserAlreadyExistsException: If email already exists
            PhoneAlreadyExistsException: If phone already exists
            ValidationError: If data is invalid
        """
        # Validate email
        validate_email(user_data.get('email'))
        
        # Validate phone number
        validate_phone_number(user_data.get('phone_number'))
        
        # Validate names
        validate_name(user_data.get('first_name'), 'First name')
        validate_name(user_data.get('last_name'), 'Last name')
        
        # Check if email already exists
        if UserRepository.check_email_exists(user_data.get('email')):
            raise UserAlreadyExistsException()
        
        # Check if phone already exists
        if UserRepository.check_phone_exists(user_data.get('phone_number')):
            raise PhoneAlreadyExistsException()
        
        # Validate date of birth if provided
        if user_data.get('date_of_birth'):
            validate_date_of_birth(user_data['date_of_birth'])
        
        # Validate coordinates if provided
        if user_data.get('latitude') or user_data.get('longitude'):
            validate_coordinates(
                user_data.get('latitude'),
                user_data.get('longitude')
            )
        
        # Create user
        user = UserRepository.create_user(user_data)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            activity_type='USER_CREATED',
            description=f'User account created: {user.email}',
            metadata={'created_by': created_by.id if created_by else None}
        )
        
        logger.info(f'User created successfully: {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def update_user_profile(user, update_data, updated_by=None):
        """
        Update user profile with validation.
        
        Args:
            user: User instance
            update_data: Dictionary containing fields to update
            updated_by: User who performed the update
            
        Returns:
            Updated User instance
            
        Raises:
            UserNotFoundException: If user not found
            UserAlreadyExistsException: If email already exists
            PhoneAlreadyExistsException: If phone already exists
        """
        if not user:
            raise UserNotFoundException()
        
        # Validate email if being updated
        if 'email' in update_data and update_data['email'] != user.email:
            validate_email(update_data['email'])
            if UserRepository.check_email_exists(update_data['email'], user.id):
                raise UserAlreadyExistsException()
            # Reset email verification if email changed
            update_data['is_email_verified'] = False
            update_data['email_verified_at'] = None
        
        # Validate phone if being updated
        if 'phone_number' in update_data and update_data['phone_number'] != user.phone_number:
            validate_phone_number(update_data['phone_number'])
            if UserRepository.check_phone_exists(update_data['phone_number'], user.id):
                raise PhoneAlreadyExistsException()
            # Reset phone verification if phone changed
            update_data['is_phone_verified'] = False
            update_data['phone_verified_at'] = None
        
        # Validate names if being updated
        if 'first_name' in update_data:
            validate_name(update_data['first_name'], 'First name')
        
        if 'last_name' in update_data:
            validate_name(update_data['last_name'], 'Last name')
        
        # Validate date of birth if being updated
        if 'date_of_birth' in update_data:
            validate_date_of_birth(update_data['date_of_birth'])
        
        # Validate coordinates if being updated
        if 'latitude' in update_data or 'longitude' in update_data:
            validate_coordinates(
                update_data.get('latitude', user.latitude),
                update_data.get('longitude', user.longitude)
            )
        
        # Validate profile picture if being updated
        if 'profile_picture' in update_data:
            validate_profile_picture(update_data['profile_picture'])
        
        # Update user
        user = UserRepository.update_user(user, update_data)
        
        # Check profile completion
        user.check_profile_completion()
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            activity_type=ACTIVITY_TYPE_PROFILE_UPDATE,
            description="User profile updated",
            ip_address="",
            user_agent="",
            metadata={
                "updated_by": updated_by.id if updated_by else user.id,
                "updated_fields": list(update_data.keys()),
            },
        )
        
        logger.info(f'User profile updated: {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def block_user(user, reason=None, blocked_by=None):
        """
        Block user account.
        
        Args:
            user: User instance
            reason: Reason for blocking
            blocked_by: User who blocked this account
            
        Returns:
            Blocked User instance
        """
        if not user:
            raise UserNotFoundException()
        
        user.block_user(reason)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            activity_type=ACTIVITY_TYPE_ACCOUNT_BLOCKED,
            description=f'User account blocked. Reason: {reason or "Not specified"}',
            metadata={
                'blocked_by': blocked_by.id if blocked_by else None,
                'reason': reason
            }
        )
        
        logger.warning(f'User blocked: {user.email}. Reason: {reason}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def unblock_user(user, unblocked_by=None):
        """
        Unblock user account.
        
        Args:
            user: User instance
            unblocked_by: User who unblocked this account
            
        Returns:
            Unblocked User instance
        """
        if not user:
            raise UserNotFoundException()
        
        user.unblock_user()
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            activity_type=ACTIVITY_TYPE_ACCOUNT_UNBLOCKED,
            description='User account unblocked',
            metadata={'unblocked_by': unblocked_by.id if unblocked_by else None}
        )
        
        logger.info(f'User unblocked: {user.email}')
        
        return user
    
    @staticmethod
    def verify_user_status(user):
        """
        Verify user account status before allowing actions.
        
        Args:
            user: User instance
            
        Raises:
            UserBlockedException: If user is blocked
            UserInactiveException: If user is inactive
        """
        if user.is_blocked:
            raise UserBlockedException()
        
        if not user.is_active:
            raise UserInactiveException()
    
    @staticmethod
    def check_profile_completion_required(user, required=True):
        """
        Check if profile completion is required.
        
        Args:
            user: User instance
            required: If True, raise exception when incomplete
            
        Returns:
            Boolean indicating profile completion status
            
        Raises:
            ProfileIncompleteException: If profile is incomplete and required=True
        """
        is_complete = user.check_profile_completion()
        
        if required and not is_complete:
            raise ProfileIncompleteException()
        
        return is_complete
    
    @staticmethod
    @transaction.atomic
    def log_user_login(user, ip_address=None, user_agent=None):
        """
        Log user login activity.
        
        Args:
            user: User instance
            ip_address: IP address
            user_agent: User agent string
        """
        user.update_last_login()
        
        UserActivityRepository.log_activity(
            user=user,
            activity_type=ACTIVITY_TYPE_LOGIN,
            description='User logged in',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f'User logged in: {user.email}')
    
    @staticmethod
    @transaction.atomic
    def log_user_logout(user, ip_address=None, user_agent=None):
        """
        Log user logout activity.
        
        Args:
            user: User instance
            ip_address: IP address
            user_agent: User agent string
        """
        UserActivityRepository.log_activity(
            user=user,
            activity_type=ACTIVITY_TYPE_LOGOUT,
            description='User logged out',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f'User logged out: {user.email}')
    
    @staticmethod
    @transaction.atomic
    def update_fcm_token(user, fcm_token):
        """
        Update Firebase Cloud Messaging token for push notifications.
        
        Args:
            user: User instance
            fcm_token: FCM token
            
        Returns:
            Updated User instance
        """
        user.fcm_token = fcm_token
        user.save(update_fields=['fcm_token'])
        
        logger.info(f'FCM token updated for user: {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def update_notification_preferences(user, preferences):
        """
        Update user notification preferences.
        
        Args:
            user: User instance
            preferences: Dictionary with preference updates
            
        Returns:
            Updated User instance
        """
        allowed_fields = [
            'notification_enabled',
            'email_notification_enabled',
            'sms_notification_enabled',
            'push_notification_enabled',
        ]
        
        for field in allowed_fields:
            if field in preferences:
                setattr(user, field, preferences[field])
        
        user.save(update_fields=allowed_fields)
        
        logger.info(f'Notification preferences updated for user: {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def delete_user_account(user, deleted_by=None):
        """
        Soft delete user account.
        
        Args:
            user: User instance
            deleted_by: User who deleted this account
            
        Returns:
            Boolean
        """
        if not user:
            raise UserNotFoundException()
        
        UserRepository.delete_user(user)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            activity_type='ACCOUNT_DELETED',
            description='User account deleted',
            metadata={'deleted_by': deleted_by.id if deleted_by else user.id}
        )
        
        logger.warning(f'User account deleted: {user.email}')
        
        return True
    
    @staticmethod
    def get_user_full_profile(user):
        """
        Get complete user profile with computed fields.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with complete profile data
        """
        from .selectors import UserSelector
        
        return {
            'user': user,
            'statistics': UserSelector.get_user_statistics(user),
            'eligibility': UserSelector.check_user_eligibility(user),
        }
