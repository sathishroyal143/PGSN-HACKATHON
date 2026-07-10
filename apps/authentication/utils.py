"""
Utility functions for authentication module.
"""
import random
import string
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
import logging

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """
    Generate a random OTP code.
    
    Args:
        length: Length of OTP (default 6)
    
    Returns:
        str: Random OTP code
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_token(length=64):
    """
    Generate a secure random token.
    
    Args:
        length: Length of token (default 64)
    
    Returns:
        str: Secure random token
    """
    return secrets.token_urlsafe(length)


def hash_token(token):
    """
    Hash a token using SHA256.
    
    Args:
        token: Token to hash
    
    Returns:
        str: Hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def get_otp_expiry_time(minutes=10):
    """
    Get OTP expiry time.
    
    Args:
        minutes: Minutes until expiry (default 10)
    
    Returns:
        datetime: Expiry datetime
    """
    return timezone.now() + timedelta(minutes=minutes)


def get_token_expiry_time(hours=24):
    """
    Get token expiry time.
    
    Args:
        hours: Hours until expiry (default 24)
    
    Returns:
        datetime: Expiry datetime
    """
    return timezone.now() + timedelta(hours=hours)


def get_refresh_token_expiry_time(days=7):
    """
    Get refresh token expiry time.
    
    Args:
        days: Days until expiry (default 7)
    
    Returns:
        datetime: Expiry datetime
    """
    return timezone.now() + timedelta(days=days)


def generate_jwt_tokens(user):
    """
    Generate JWT access and refresh tokens for a user.
    
    Args:
        user: User instance
    
    Returns:
        dict: Dictionary containing access and refresh tokens
    """
    refresh = JWTRefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'access_expires_at': timezone.now() + timedelta(
            seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        ),
        'refresh_expires_at': timezone.now() + timedelta(
            seconds=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        ),
    }


def send_email(subject, template, context, recipient_email):
    """
    Send email using template.
    
    Args:
        subject: Email subject
        template: Template path
        context: Template context
        recipient_email: Recipient email address
    
    Returns:
        bool: True if sent successfully
    """
    try:
        html_message = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_sms(phone_number, message):
    """
    Send SMS using Twilio.
    
    Args:
        phone_number: Recipient phone number
        message: SMS message
    
    Returns:
        bool: True if sent successfully
    """
    try:
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully to {phone_number}, SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent from request.
    
    Args:
        request: Django request object
    
    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def get_device_info(request):
    """
    Extract device information from request.
    
    Args:
        request: Django request object
    
    Returns:
        dict: Device information
    """
    device_id = request.data.get('device_id', '')
    device_name = request.data.get('device_name', '')
    
    return {
        'device_id': device_id,
        'device_name': device_name,
        'ip_address': get_client_ip(request),
        'user_agent': get_user_agent(request),
    }


def mask_email(email):
    """
    Mask email address for privacy.
    Example: john.doe@example.com -> j***e@example.com
    
    Args:
        email: Email address to mask
    
    Returns:
        str: Masked email address
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone_number):
    """
    Mask phone number for privacy.
    Example: +1234567890 -> +1******890
    
    Args:
        phone_number: Phone number to mask
    
    Returns:
        str: Masked phone number
    """
    if not phone_number or len(phone_number) < 4:
        return phone_number
    
    return phone_number[:2] + '*' * (len(phone_number) - 5) + phone_number[-3:]


def validate_password_strength(password):
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    
    if not any(char.isupper() for char in password):
        return False, 'Password must contain at least one uppercase letter.'
    
    if not any(char.islower() for char in password):
        return False, 'Password must contain at least one lowercase letter.'
    
    if not any(char.isdigit() for char in password):
        return False, 'Password must contain at least one digit.'
    
    special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_characters for char in password):
        return False, 'Password must contain at least one special character.'
    
    return True, ''


def is_valid_email_format(email):
    """
    Validate email format.
    
    Args:
        email: Email to validate
    
    Returns:
        bool: True if valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone_format(phone_number):
    """
    Validate phone number format.
    Accepts formats: +1234567890, 1234567890
    
    Args:
        phone_number: Phone number to validate
    
    Returns:
        bool: True if valid
    """
    import re
    pattern = r'^\+?[1-9]\d{9,14}$'
    return bool(re.match(pattern, phone_number))


def normalize_phone_number(phone_number):
    """
    Normalize phone number by removing spaces and special characters.
    
    Args:
        phone_number: Phone number to normalize
    
    Returns:
        str: Normalized phone number
    """
    import re
    return re.sub(r'[^\d+]', '', phone_number)
