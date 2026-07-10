"""
Selector layer for authentication module.
Handles complex read-only queries and data aggregation.
"""
from django.db.models import Q, Count, Avg, Max
from django.utils import timezone
from datetime import timedelta
from apps.authentication.models import OTP, PasswordResetToken, RefreshToken, LoginAttempt
from apps.users.models import User


class AuthenticationSelector:
    """Selector for authentication-related complex queries."""
    
    @staticmethod
    def get_user_security_overview(user):
        """
        Get comprehensive security overview for user.
        """
        active_sessions = RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            is_blacklisted=False,
            expires_at__gt=timezone.now()
        ).count()
        
        recent_logins = LoginAttempt.objects.filter(
            user=user,
            status='SUCCESS',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        failed_attempts = LoginAttempt.objects.filter(
            user=user,
            status='FAILED',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        last_login = LoginAttempt.objects.filter(
            user=user,
            status='SUCCESS'
        ).order_by('-created_at').first()
        
        last_password_reset = PasswordResetToken.objects.filter(
            user=user,
            is_used=True
        ).order_by('-used_at').first()
        
        pending_verifications = []
        if not user.is_email_verified:
            pending_verifications.append('email')
        if not user.is_phone_verified:
            pending_verifications.append('phone')
        
        return {
            'active_sessions': active_sessions,
            'recent_logins_count': recent_logins,
            'failed_attempts_count': failed_attempts,
            'last_login': {
                'timestamp': last_login.created_at if last_login else None,
                'ip_address': last_login.ip_address if last_login else None,
                'device': last_login.device_name if last_login else None,
            } if last_login else None,
            'last_password_reset': last_password_reset.used_at if last_password_reset else None,
            'pending_verifications': pending_verifications,
            'account_status': {
                'is_active': user.is_active,
                'is_blocked': user.is_blocked,
                'is_email_verified': user.is_email_verified,
                'is_phone_verified': user.is_phone_verified,
            }
        }
    
    @staticmethod
    def get_active_sessions(user):
        """Get all active sessions with details."""
        sessions = RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            is_blacklisted=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')
        
        return [
            {
                'id': str(session.id),
                'device_name': session.device_name,
                'device_id': session.device_id,
                'ip_address': session.ip_address,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
                'is_current': False,
            }
            for session in sessions
        ]
    
    @staticmethod
    def get_login_history(user, days=30, limit=20):
        """Get user's login history with details."""
        time_threshold = timezone.now() - timedelta(days=days)
        attempts = LoginAttempt.objects.filter(
            user=user,
            created_at__gte=time_threshold
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'timestamp': attempt.created_at,
                'status': attempt.status,
                'failure_reason': attempt.failure_reason,
                'ip_address': attempt.ip_address,
                'device': attempt.device_name,
                'location': attempt.location_data,
            }
            for attempt in attempts
        ]
    
    @staticmethod
    def get_verification_status(user):
        """Get user's verification status details."""
        email_otp = OTP.objects.filter(
            user=user,
            otp_type='EMAIL_VERIFICATION',
            is_verified=True
        ).order_by('-verified_at').first()
        
        phone_otp = OTP.objects.filter(
            user=user,
            otp_type='PHONE_VERIFICATION',
            is_verified=True
        ).order_by('-verified_at').first()
        
        return {
            'email': {
                'is_verified': user.is_email_verified,
                'verified_at': email_otp.verified_at if email_otp else None,
                'email': user.email,
            },
            'phone': {
                'is_verified': user.is_phone_verified,
                'verified_at': phone_otp.verified_at if phone_otp else None,
                'phone_number': str(user.phone_number),
            }
        }
    
    @staticmethod
    def check_otp_rate_limit(user, otp_type, hours=1, max_count=10):
        """Check if user has exceeded OTP rate limit."""
        time_threshold = timezone.now() - timedelta(hours=hours)
        count = OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            created_at__gte=time_threshold
        ).count()
        
        return {
            'is_limited': count >= max_count,
            'current_count': count,
            'max_count': max_count,
            'reset_time': time_threshold + timedelta(hours=hours)
        }
    
    @staticmethod
    def check_password_reset_rate_limit(user, hours=24, max_count=5):
        """Check if user has exceeded password reset rate limit."""
        time_threshold = timezone.now() - timedelta(hours=hours)
        count = PasswordResetToken.objects.filter(
            user=user,
            created_at__gte=time_threshold
        ).count()
        
        return {
            'is_limited': count >= max_count,
            'current_count': count,
            'max_count': max_count,
            'reset_time': time_threshold + timedelta(hours=hours)
        }
    
    @staticmethod
    def get_suspicious_activities(user, days=7):
        """Get suspicious login activities for user."""
        time_threshold = timezone.now() - timedelta(days=days)
        
        failed_attempts = LoginAttempt.objects.filter(
            user=user,
            status='FAILED',
            created_at__gte=time_threshold
        ).values('ip_address').annotate(
            count=Count('id')
        ).filter(count__gte=3).order_by('-count')
        
        blocked_attempts = LoginAttempt.objects.filter(
            user=user,
            status='BLOCKED',
            created_at__gte=time_threshold
        ).order_by('-created_at')
        
        return {
            'failed_attempts_by_ip': list(failed_attempts),
            'blocked_attempts': [
                {
                    'timestamp': attempt.created_at,
                    'ip_address': attempt.ip_address,
                    'reason': attempt.failure_reason,
                }
                for attempt in blocked_attempts
            ],
            'total_suspicious_ips': len(failed_attempts),
            'total_blocked_attempts': blocked_attempts.count(),
        }
    
    @staticmethod
    def get_account_security_score(user):
        """
        Calculate security score for user account (0-100).
        """
        score = 0
        
        if user.is_email_verified:
            score += 20
        
        if user.is_phone_verified:
            score += 20
        
        if user.profile_picture:
            score += 10
        
        recent_password_change = PasswordResetToken.objects.filter(
            user=user,
            is_used=True,
            used_at__gte=timezone.now() - timedelta(days=90)
        ).exists()
        if recent_password_change or user.created_at >= timezone.now() - timedelta(days=90):
            score += 15
        
        recent_failed_attempts = LoginAttempt.objects.filter(
            user=user,
            status='FAILED',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        if recent_failed_attempts == 0:
            score += 15
        elif recent_failed_attempts <= 3:
            score += 10
        elif recent_failed_attempts <= 5:
            score += 5
        
        active_sessions = RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            expires_at__gt=timezone.now()
        ).count()
        if active_sessions <= 3:
            score += 10
        elif active_sessions <= 5:
            score += 5
        
        if user.is_active and not user.is_blocked:
            score += 10
        
        return {
            'score': min(score, 100),
            'level': 'High' if score >= 80 else 'Medium' if score >= 50 else 'Low',
            'recommendations': AuthenticationSelector._get_security_recommendations(user, score)
        }
    
    @staticmethod
    def _get_security_recommendations(user, score):
        """Get security recommendations based on account state."""
        recommendations = []
        
        if not user.is_email_verified:
            recommendations.append('Verify your email address')
        
        if not user.is_phone_verified:
            recommendations.append('Verify your phone number')
        
        if not user.profile_picture:
            recommendations.append('Add a profile picture')
        
        last_password_change = PasswordResetToken.objects.filter(
            user=user,
            is_used=True
        ).order_by('-used_at').first()
        
        if last_password_change and last_password_change.used_at < timezone.now() - timedelta(days=90):
            recommendations.append('Change your password (last changed over 90 days ago)')
        
        active_sessions = RefreshToken.objects.filter(
            user=user,
            is_revoked=False,
            expires_at__gt=timezone.now()
        ).count()
        
        if active_sessions > 5:
            recommendations.append('You have many active sessions, consider logging out from unused devices')
        
        return recommendations


class OTPSelector:
    """Selector for OTP-related queries."""
    
    @staticmethod
    def get_pending_verifications(user):
        """Get pending OTP verifications for user."""
        pending = []
        
        if not user.is_email_verified:
            latest_email_otp = OTP.objects.filter(
                user=user,
                otp_type='EMAIL_VERIFICATION',
                is_used=False
            ).order_by('-created_at').first()
            
            if latest_email_otp and not latest_email_otp.is_expired():
                pending.append({
                    'type': 'email',
                    'sent_at': latest_email_otp.created_at,
                    'expires_at': latest_email_otp.expires_at,
                })
        
        if not user.is_phone_verified:
            latest_phone_otp = OTP.objects.filter(
                user=user,
                otp_type='PHONE_VERIFICATION',
                is_used=False
            ).order_by('-created_at').first()
            
            if latest_phone_otp and not latest_phone_otp.is_expired():
                pending.append({
                    'type': 'phone',
                    'sent_at': latest_phone_otp.created_at,
                    'expires_at': latest_phone_otp.expires_at,
                })
        
        return pending
