"""
Serializers for authentication module.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.authentication.utils import validate_password_strength, is_valid_email_format, is_valid_phone_format
from apps.authentication import constants

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, required=True, min_length=8)
    phone_number = serializers.CharField(required=True, max_length=15)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    role = serializers.ChoiceField(choices=['FAMILY', 'COMPANION'], required=True)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=['MALE', 'FEMALE', 'OTHER'], required=False)
    
    def validate_email(self, value):
        """Validate email format."""
        if not is_valid_email_format(value):
            raise serializers.ValidationError('Invalid email format.')
        return value.lower()
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not is_valid_phone_format(value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value
    
    def validate(self, attrs):
        """Validate passwords match and strength."""
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        
        is_valid, error_message = validate_password_strength(attrs['password'])
        if not is_valid:
            raise serializers.ValidationError({'password': error_message})
        
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    device_id = serializers.CharField(required=False, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_blank=True)


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    access_expires_at = serializers.DateTimeField()
    refresh_expires_at = serializers.DateTimeField()
    session_id = serializers.UUIDField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Get user data."""
        from apps.users.serializers import UserDetailSerializer
        return UserDetailSerializer(obj['user']).data


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh."""
    refresh = serializers.CharField(required=True)


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    access_expires_at = serializers.DateTimeField()
    refresh_expires_at = serializers.DateTimeField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout."""
    refresh = serializers.CharField(required=True)


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP."""
    otp_type = serializers.ChoiceField(
        choices=[
            constants.OTP_TYPE_EMAIL_VERIFICATION,
            constants.OTP_TYPE_PHONE_VERIFICATION,
        ],
        required=True
    )


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    otp_code = serializers.CharField(required=True, max_length=6, min_length=6)
    otp_type = serializers.ChoiceField(
        choices=constants.OTP_TYPES,
        required=True
    )


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    otp_type = serializers.ChoiceField(
        choices=[
            constants.OTP_TYPE_EMAIL_VERIFICATION,
            constants.OTP_TYPE_PHONE_VERIFICATION,
        ],
        required=True
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email format."""
        if not is_valid_email_format(value):
            raise serializers.ValidationError('Invalid email format.')
        return value.lower()


class PasswordResetVerifySerializer(serializers.Serializer):
    """Serializer for verifying password reset token."""
    token = serializers.CharField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate(self, attrs):
        """Validate passwords match and strength."""
        if attrs['new_password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        
        is_valid, error_message = validate_password_strength(attrs['new_password'])
        if not is_valid:
            raise serializers.ValidationError({'new_password': error_message})
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate(self, attrs):
        """Validate passwords match and strength."""
        if attrs['new_password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'New password must be different from old password.'})
        
        is_valid, error_message = validate_password_strength(attrs['new_password'])
        if not is_valid:
            raise serializers.ValidationError({'new_password': error_message})
        
        return attrs


class SessionSerializer(serializers.Serializer):
    """Serializer for session details."""
    id = serializers.UUIDField()
    device_name = serializers.CharField()
    device_id = serializers.CharField()
    ip_address = serializers.IPAddressField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    is_current = serializers.BooleanField()


class RevokeSessionSerializer(serializers.Serializer):
    """Serializer for revoking session."""
    session_id = serializers.UUIDField(required=True)


class RevokeDeviceSessionsSerializer(serializers.Serializer):
    """Serializer for revoking device sessions."""
    device_id = serializers.CharField(required=True)


class SecurityOverviewSerializer(serializers.Serializer):
    """Serializer for security overview."""
    active_sessions = serializers.IntegerField()
    recent_logins_count = serializers.IntegerField()
    failed_attempts_count = serializers.IntegerField()
    last_login = serializers.DictField()
    last_password_reset = serializers.DateTimeField(allow_null=True)
    pending_verifications = serializers.ListField()
    account_status = serializers.DictField()


class LoginHistorySerializer(serializers.Serializer):
    """Serializer for login history entry."""
    timestamp = serializers.DateTimeField()
    status = serializers.CharField()
    failure_reason = serializers.CharField(allow_null=True)
    ip_address = serializers.IPAddressField()
    device = serializers.CharField(allow_null=True)
    location = serializers.DictField(allow_null=True)


class VerificationStatusSerializer(serializers.Serializer):
    """Serializer for verification status."""
    email = serializers.DictField()
    phone = serializers.DictField()


class SecurityScoreSerializer(serializers.Serializer):
    """Serializer for security score."""
    score = serializers.IntegerField()
    level = serializers.CharField()
    recommendations = serializers.ListField()


class OTPResponseSerializer(serializers.Serializer):
    """Serializer for OTP response."""
    otp_sent = serializers.BooleanField()
    expires_at = serializers.DateTimeField()
    otp_type = serializers.CharField()
    message = serializers.CharField(default='OTP sent successfully')
    dev_otp = serializers.CharField(required=False, allow_null=True, default=None)


class OTPVerificationResponseSerializer(serializers.Serializer):
    """Serializer for OTP verification response."""
    verified = serializers.BooleanField()
    otp_type = serializers.CharField()
    message = serializers.CharField(default='OTP verified successfully')


class PasswordResetResponseSerializer(serializers.Serializer):
    """Serializer for password reset response."""
    reset_requested = serializers.BooleanField()
    expires_at = serializers.DateTimeField()
    message = serializers.CharField(default='Password reset email sent successfully')


class PasswordResetVerifyResponseSerializer(serializers.Serializer):
    """Serializer for password reset verification response."""
    valid = serializers.BooleanField()
    user_email = serializers.EmailField()
    expires_at = serializers.DateTimeField()


class PasswordResetConfirmResponseSerializer(serializers.Serializer):
    """Serializer for password reset confirmation response."""
    password_reset = serializers.BooleanField()
    message = serializers.CharField()


class ChangePasswordResponseSerializer(serializers.Serializer):
    """Serializer for change password response."""
    password_changed = serializers.BooleanField()
    message = serializers.CharField()
