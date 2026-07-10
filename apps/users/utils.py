"""
Utility functions for Users module.
"""

import hashlib
import secrets
from typing import Optional

from django.core.files.base import ContentFile
from django.utils import timezone


def generate_verification_token(user_id: int, email: str) -> str:
    """
    Generate a verification token for email/phone verification.
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        Verification token string
    """
    random_string = secrets.token_urlsafe(32)
    data = f"{user_id}:{email}:{random_string}:{timezone.now().isoformat()}"
    token = hashlib.sha256(data.encode()).hexdigest()
    return token


def get_client_ip(request) -> Optional[str]:
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        IP address string or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """
    Get user agent from request.
    
    Args:
        request: Django request object
        
    Returns:
        User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def compress_profile_picture(image, max_size_mb=2):
    """
    Compress profile picture if it exceeds max size.
    
    Args:
        image: Image file
        max_size_mb: Maximum size in megabytes
        
    Returns:
        Compressed image or original if already small enough
    """
    from PIL import Image
    from io import BytesIO
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if image.size <= max_size_bytes:
        return image
    
    # Open image
    img = Image.open(image)
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Calculate new size to reduce file size
    output = BytesIO()
    quality = 85
    
    while True:
        output.seek(0)
        output.truncate()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        size = output.tell()
        
        if size <= max_size_bytes or quality <= 20:
            break
        
        quality -= 5
    
    output.seek(0)
    return ContentFile(output.read(), name=image.name)


def calculate_profile_completion_percentage(user) -> int:
    """
    Calculate profile completion percentage.
    
    Args:
        user: User instance
        
    Returns:
        Completion percentage (0-100)
    """
    fields_to_check = [
        ('first_name', 10),
        ('last_name', 10),
        ('email', 10),
        ('phone_number', 10),
        ('date_of_birth', 10),
        ('gender', 5),
        ('address_line_1', 10),
        ('city', 10),
        ('state', 10),
        ('postal_code', 5),
        ('profile_picture', 10),
        ('bio', 5),
        ('is_email_verified', 5),
        ('is_phone_verified', 5),
    ]
    
    total_weight = sum(weight for _, weight in fields_to_check)
    completed_weight = 0
    
    for field, weight in fields_to_check:
        value = getattr(user, field, None)
        if value:
            completed_weight += weight
    
    return int((completed_weight / total_weight) * 100)


def format_phone_number(phone_number: str) -> str:
    """
    Format phone number for display.
    
    Args:
        phone_number: Raw phone number
        
    Returns:
        Formatted phone number
    """
    # Remove non-numeric characters
    digits = ''.join(filter(str.isdigit, str(phone_number)))
    
    if len(digits) == 10:
        # Indian format: (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return str(phone_number)


def anonymize_user_data(user):
    """
    Anonymize user data for GDPR compliance.
    
    Args:
        user: User instance
        
    Returns:
        Updated user instance
    """
    user.email = f"deleted_{user.id}@carebridge.local"
    user.phone_number = None
    user.first_name = "Deleted"
    user.last_name = "User"
    user.profile_picture = None
    user.bio = ""
    user.address_line_1 = ""
    user.address_line_2 = ""
    user.city = ""
    user.state = ""
    user.postal_code = ""
    user.latitude = None
    user.longitude = None
    user.metadata = {}
    user.is_active = False
    user.save()
    
    return user
