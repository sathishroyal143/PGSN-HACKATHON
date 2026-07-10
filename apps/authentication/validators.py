"""
Validators for authentication module.
"""
from django.core.exceptions import ValidationError
from apps.authentication.utils import (
    validate_password_strength,
    is_valid_email_format,
    is_valid_phone_format
)


def validate_registration_email(email):
    """
    Validate email for registration.
    """
    if not email:
        raise ValidationError('Email is required.')
    
    if not is_valid_email_format(email):
        raise ValidationError('Invalid email format.')
    
    from apps.users.models import User
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError('User with this email already exists.')
    
    return email.lower()


def validate_registration_phone(phone_number):
    """
    Validate phone number for registration.
    """
    if not phone_number:
        raise ValidationError('Phone number is required.')
    
    if not is_valid_phone_format(phone_number):
        raise ValidationError('Invalid phone number format.')
    
    from apps.users.models import User
    if User.objects.filter(phone_number=phone_number).exists():
        raise ValidationError('User with this phone number already exists.')
    
    return phone_number


def validate_registration_password(password, password_confirmation):
    """
    Validate password for registration.
    """
    if not password:
        raise ValidationError('Password is required.')
    
    if not password_confirmation:
        raise ValidationError('Password confirmation is required.')
    
    if password != password_confirmation:
        raise ValidationError('Passwords do not match.')
    
    is_valid, error_message = validate_password_strength(password)
    if not is_valid:
        raise ValidationError(error_message)
    
    return password


def validate_otp_code(otp_code):
    """
    Validate OTP code format.
    """
    if not otp_code:
        raise ValidationError('OTP code is required.')
    
    if not otp_code.isdigit():
        raise ValidationError('OTP code must contain only digits.')
    
    if len(otp_code) != 6:
        raise ValidationError('OTP code must be 6 digits.')
    
    return otp_code


def validate_otp_type(otp_type):
    """
    Validate OTP type.
    """
    from apps.authentication import constants
    
    if not otp_type:
        raise ValidationError('OTP type is required.')
    
    if otp_type not in constants.OTP_TYPES:
        raise ValidationError(f'Invalid OTP type. Must be one of: {", ".join(constants.OTP_TYPES)}')
    
    return otp_type


def validate_reset_token(token):
    """
    Validate password reset token.
    """
    if not token:
        raise ValidationError('Reset token is required.')
    
    if len(token) < 32:
        raise ValidationError('Invalid reset token.')
    
    return token


def validate_device_info(device_id, device_name):
    """
    Validate device information.
    """
    if device_id and len(device_id) > 255:
        raise ValidationError('Device ID too long.')
    
    if device_name and len(device_name) > 255:
        raise ValidationError('Device name too long.')
    
    return device_id, device_name
