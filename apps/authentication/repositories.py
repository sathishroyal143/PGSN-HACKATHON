"""
Repository layer for authentication module.
Handles all database operations.
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from apps.authentication.models import OTP, PasswordResetToken, RefreshToken, LoginAttempt
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class OTPRepository:
    """Repository for OTP operations."""
    
    @staticmethod
    def create(user, otp_code, otp_type, expires_at, **kwargs):
        """Create new OTP record."""
        return OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=expires_at,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(otp_id):
        """Get OTP by ID."""
        try:
            return OTP.objects.get(id=otp_id)
        except OTP.DoesNotExist:
            return None
    
    @staticmethod
    def get_valid_otp(user, otp_code, otp_type):
        """Get valid OTP for user."""
        try:
            return OTP.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=otp_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except OTP.DoesNotExist:
            return None
    
    @staticmethod
    def get_latest_otp(user, otp_type):
        """Get latest OTP for user and type."""
        return OTP.objects.filter(
            user=user,
            otp_type=otp_type
        ).order_by('-created_at').first()
    
    @staticmethod
    def get_by_email_or_phone(email=None, phone_number=None, otp_type=None):
        """Get OTP by email or phone number."""
        query = Q()
        if email:
            query |= Q(email=email)
        if phone_number:
            query |= Q(phone_number=phone_number)
        if otp_type:
            query &= Q(otp_type=otp_type)
        
        return OTP.objects.filter(query).order_by('-created_at').first()
    
    @staticmethod
    def mark_as_verified(otp):
        """Mark OTP as verified."""
        otp.mark_as_verified()
    
    @staticmethod
    def increment_attempts(otp):
        """Increment OTP verification attempts."""
        otp.increment_attempts()
    
    @staticmethod
    def invalidate_previous_otps(user, otp_type):
        """Invalidate all previous OTPs of same type for user."""
        OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).update(is_used=True)
    
    @staticmethod
    def delete_expired_otps():
        """Delete expired OTPs (cleanup task)."""
        expired_count = OTP.objects.filter(
            expires_at__lt=timezone.now() - timedelta(days=1)
        ).delete()[0]
        logger.info(f"Deleted {expired_count} expired OTPs")
        return expired_count
    
    @staticmethod
    def get_recent_otp_count(user, otp_type, hours=1):
        """Get count of OTPs sent in recent hours."""
        time_threshold = timezone.now() - timedelta(hours=hours)
        return OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            created_at__gte=time_threshold
        ).count()


class PasswordResetTokenRepository:
    """Repository for password reset token operations."""
    
    @staticmethod
    def create(user, token, expires_at, **kwargs):
        """Create new password reset token."""
        return PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at,
            **kwargs
        )
    
    @staticmethod
    def get_by_token(token):
        """Get password reset token by token string."""
        try:
            return PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return None
    
    @staticmethod
    def get_valid_token(token):
        """Get valid (not expired, not used) password reset token."""
        try:
            return PasswordResetToken.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            return None
    
    @staticmethod
    def mark_as_used(token_obj):
        """Mark token as used."""
        token_obj.mark_as_used()
    
    @staticmethod
    def invalidate_user_tokens(user):
        """Invalidate all password reset tokens for user."""
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
    
    @staticmethod
    def delete_expired_tokens():
        """Delete expired tokens (cleanup task)."""
        expired_count = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now() - timedelta(days=1)
        ).delete()[0]
        logger.info(f"Deleted {expired_count} expired password reset tokens")
        return expired_count
    
    @staticmethod
    def get_recent_token_count(user, hours=24):
        """Get count of tokens created in recent hours."""
        time_threshold = timezone.now() - timedelta(hours=hours)
        return PasswordResetToken.objects.filter(
            user=user,
            created_at__gte=time_threshold
        ).count()


class RefreshTokenRepository:
    """Repository for refresh token operations."""
    
    @staticmethod
    def create(user, token, jti, expires_at, **kwargs):
        """Create new refresh token."""
        return RefreshToken.objects.create(
            user=user,
            token=token,
            jti=jti,
            expires_at=expires_at,
            **kwargs
        )
    
    @staticmethod
    def get_by_token(token):
        """Get refresh token by token string."""
        try:
            return RefreshToken.objects.get(token=token)
        except RefreshToken.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(token_id):
        """Get refresh token by ID."""
        try:
            return RefreshToken.objects.get(id=token_id)
        except RefreshToken.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_jti(jti):
        """Get refresh token by JTI."""
        try:
            return RefreshToken.objects.get(jti=jti)
        except RefreshToken.DoesNotExist:
            return None
    
    @staticmethod
    def get_valid_token(token):
        """Get valid refresh token."""
        try:
            return RefreshToken.objects.get(
                token=token,
                is_revoked=False,
                is_blacklisted=False,
                expires_at__gt=timezone.now()
            )
        except RefreshToken.DoesNotExist:
            return None
    
    @staticmethod
    def revoke_token(token_obj):
        """Revoke refresh token."""
        token_obj.revoke()
    
    @staticmethod
    def blacklist_token(token_obj):
        """Blacklist refresh token."""
        token_obj.blacklist()
    
    @staticmethod
    def revoke_all_user_tokens(user):
        """Revoke all refresh tokens for user."""
        RefreshToken.objects.filter(
            user=user,
            is_revoked=False
        ).update(is_revoked=True, revoked_at=timezone.now())
    
    @staticmethod
    def get_user_active_tokens(user):
        """Get all active refresh tokens for user."""
        return RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            is_blacklisted=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')
    
    @staticmethod
    def get_user_token_count(user):
        """Get count of active tokens for user."""
        return RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            is_blacklisted=False,
            expires_at__gt=timezone.now()
        ).count()
    
    @staticmethod
    def delete_expired_tokens():
        """Delete expired refresh tokens (cleanup task)."""
        expired_count = RefreshToken.objects.filter(
            expires_at__lt=timezone.now() - timedelta(days=7)
        ).delete()[0]
        logger.info(f"Deleted {expired_count} expired refresh tokens")
        return expired_count
    
    @staticmethod
    def revoke_device_tokens(user, device_id):
        """Revoke all tokens for a specific device."""
        RefreshToken.objects.filter(
            user=user,
            device_id=device_id,
            is_revoked=False
        ).update(is_revoked=True, revoked_at=timezone.now())


class LoginAttemptRepository:
    """Repository for login attempt operations."""
    
    @staticmethod
    def create(status, **kwargs):
        """Create new login attempt record."""
        return LoginAttempt.objects.create(
            status=status,
            **kwargs
        )
    
    @staticmethod
    def get_recent_attempts(identifier, identifier_type='email', hours=1):
        """Get recent login attempts for email/phone."""
        time_threshold = timezone.now() - timedelta(hours=hours)
        filter_kwargs = {
            identifier_type: identifier,
            'created_at__gte': time_threshold
        }
        return LoginAttempt.objects.filter(**filter_kwargs).order_by('-created_at')
    
    @staticmethod
    def get_failed_attempts_count(identifier, identifier_type='email', hours=1):
        """Get count of recent failed login attempts."""
        return LoginAttempt.get_recent_failed_attempts(identifier, identifier_type, hours)
    
    @staticmethod
    def is_blocked(identifier, identifier_type='email', max_attempts=5, hours=1):
        """Check if identifier is blocked due to too many failed attempts."""
        return LoginAttempt.is_blocked(identifier, identifier_type, max_attempts, hours)
    
    @staticmethod
    def get_user_login_history(user, limit=10):
        """Get user's login history."""
        return LoginAttempt.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_successful_logins(user, days=30):
        """Get successful logins for user in last N days."""
        time_threshold = timezone.now() - timedelta(days=days)
        return LoginAttempt.objects.filter(
            user=user,
            status='SUCCESS',
            created_at__gte=time_threshold
        ).order_by('-created_at')
    
    @staticmethod
    def delete_old_attempts(days=90):
        """Delete old login attempts (cleanup task)."""
        time_threshold = timezone.now() - timedelta(days=days)
        deleted_count = LoginAttempt.objects.filter(
            created_at__lt=time_threshold
        ).delete()[0]
        logger.info(f"Deleted {deleted_count} old login attempts")
        return deleted_count
    
    @staticmethod
    def get_login_statistics(user):
        """Get login statistics for user."""
        total_attempts = LoginAttempt.objects.filter(user=user).count()
        successful_logins = LoginAttempt.objects.filter(
            user=user,
            status='SUCCESS'
        ).count()
        failed_logins = LoginAttempt.objects.filter(
            user=user,
            status='FAILED'
        ).count()
        
        return {
            'total_attempts': total_attempts,
            'successful_logins': successful_logins,
            'failed_logins': failed_logins,
            'success_rate': (successful_logins / total_attempts * 100) if total_attempts > 0 else 0
        }
