from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class OTP(models.Model):
    """
    Model to store OTP for email and phone verification.
    """
    OTP_TYPE_CHOICES = [
        ('EMAIL_VERIFICATION', 'Email Verification'),
        ('PHONE_VERIFICATION', 'Phone Verification'),
        ('LOGIN', 'Login'),
        ('PASSWORD_RESET', 'Password Reset'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=30, choices=OTP_TYPE_CHOICES)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'authentication_otps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', 'is_verified']),
            models.Index(fields=['otp_code', 'expires_at']),
            models.Index(fields=['email', 'otp_type']),
            models.Index(fields=['phone_number', 'otp_type']),
        ]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_type}"

    def is_expired(self):
        """Check if OTP has expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if OTP is valid (not expired, not used, attempts remaining)."""
        return (
            not self.is_expired() and
            not self.is_used and
            self.attempts < self.max_attempts
        )

    def mark_as_verified(self):
        """Mark OTP as verified."""
        self.is_verified = True
        self.is_used = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'is_used', 'verified_at', 'updated_at'])

    def increment_attempts(self):
        """Increment failed verification attempts."""
        self.attempts += 1
        self.save(update_fields=['attempts', 'updated_at'])


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'authentication_password_reset_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['user', 'expires_at']),
        ]

    def __str__(self):
        return f"Password Reset Token for {self.user.email}"

    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not expired, not used)."""
        return not self.is_expired() and not self.is_used

    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])


class RefreshToken(models.Model):
    """
    Model to store JWT refresh tokens for token rotation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.TextField(unique=True)
    jti = models.CharField(max_length=255, unique=True, help_text="JWT ID")
    is_revoked = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'authentication_refresh_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_revoked']),
            models.Index(fields=['jti', 'is_revoked']),
            models.Index(fields=['token']),
            models.Index(fields=['device_id', 'user']),
        ]

    def __str__(self):
        return f"Refresh Token for {self.user.email}"

    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not expired, not revoked, not blacklisted)."""
        return (
            not self.is_expired() and
            not self.is_revoked and
            not self.is_blacklisted
        )

    def revoke(self):
        """Revoke the refresh token."""
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.save(update_fields=['is_revoked', 'revoked_at'])

    def blacklist(self):
        """Blacklist the refresh token."""
        self.is_blacklisted = True
        self.save(update_fields=['is_blacklisted'])


class LoginAttempt(models.Model):
    """
    Model to track login attempts for security monitoring and rate limiting.
    """
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('BLOCKED', 'Blocked'),
    ]

    FAILURE_REASON_CHOICES = [
        ('INVALID_CREDENTIALS', 'Invalid Credentials'),
        ('USER_NOT_FOUND', 'User Not Found'),
        ('USER_BLOCKED', 'User Blocked'),
        ('USER_INACTIVE', 'User Inactive'),
        ('EMAIL_NOT_VERIFIED', 'Email Not Verified'),
        ('PHONE_NOT_VERIFIED', 'Phone Not Verified'),
        ('TOO_MANY_ATTEMPTS', 'Too Many Attempts'),
        ('OTP_REQUIRED', 'OTP Required'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_attempts')
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    failure_reason = models.CharField(max_length=30, choices=FAILURE_REASON_CHOICES, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    location_data = models.JSONField(null=True, blank=True, help_text="Geolocation data")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authentication_login_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Login Attempt - {self.status} - {self.email or self.phone_number}"

    @classmethod
    def get_recent_failed_attempts(cls, identifier, identifier_type='email', hours=1):
        """
        Get recent failed login attempts for an email/phone within specified hours.
        """
        time_threshold = timezone.now() - timedelta(hours=hours)
        filter_kwargs = {
            identifier_type: identifier,
            'status': 'FAILED',
            'created_at__gte': time_threshold
        }
        return cls.objects.filter(**filter_kwargs).count()

    @classmethod
    def is_blocked(cls, identifier, identifier_type='email', max_attempts=5, hours=1):
        """
        Check if login attempts should be blocked based on recent failed attempts.
        """
        failed_attempts = cls.get_recent_failed_attempts(identifier, identifier_type, hours)
        return failed_attempts >= max_attempts
