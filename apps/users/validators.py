"""
Validators for Users module.
"""

import re
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from phonenumber_field.validators import validate_international_phonenumber

from .constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    INVALID_EMAIL,
    INVALID_PHONE,
    INVALID_POSTAL_CODE,
    MAX_PROFILE_PICTURE_SIZE,
)


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Raises:
        ValidationError: If email is invalid
    """
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError(INVALID_EMAIL)
    
    # Additional custom validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValidationError(INVALID_EMAIL)


def validate_phone_number(phone_number):
    """
    Validate phone number format.
    
    Args:
        phone_number: Phone number to validate
        
    Raises:
        ValidationError: If phone number is invalid
    """
    try:
        validate_international_phonenumber(phone_number)
    except ValidationError:
        raise ValidationError(INVALID_PHONE)


def validate_postal_code(postal_code):
    """
    Validate Indian postal code format (6 digits).
    
    Args:
        postal_code: Postal code to validate
        
    Raises:
        ValidationError: If postal code is invalid
    """
    if not re.match(r'^\d{6}$', postal_code):
        raise ValidationError(INVALID_POSTAL_CODE)


def validate_date_of_birth(date_of_birth):
    """
    Validate date of birth.
    User must be at least 18 years old and not more than 120 years old.
    
    Args:
        date_of_birth: Date of birth to validate
        
    Raises:
        ValidationError: If date of birth is invalid
    """
    if not date_of_birth:
        return
    
    today = date.today()
    age = today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )
    
    if age < 18:
        raise ValidationError('User must be at least 18 years old')
    
    if age > 120:
        raise ValidationError('Invalid date of birth')
    
    if date_of_birth > today:
        raise ValidationError('Date of birth cannot be in the future')


def validate_profile_picture(image):
    """
    Validate profile picture.
    
    Args:
        image: Image file to validate
        
    Raises:
        ValidationError: If image is invalid
    """
    if not image:
        return
    
    # Check file size
    if image.size > MAX_PROFILE_PICTURE_SIZE:
        raise ValidationError(
            f'Profile picture size must not exceed {MAX_PROFILE_PICTURE_SIZE / (1024 * 1024)}MB'
        )
    
    # Check file extension
    extension = image.name.split('.')[-1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Invalid file format. Allowed formats: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )


def validate_password_strength(password):
    """
    Validate password strength.
    Password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character
    
    Args:
        password: Password to validate
        
    Raises:
        ValidationError: If password is weak
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')


def validate_coordinates(latitude, longitude):
    """
    Validate geographic coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Raises:
        ValidationError: If coordinates are invalid
    """
    if latitude is not None:
        if not -90 <= float(latitude) <= 90:
            raise ValidationError('Latitude must be between -90 and 90')
    
    if longitude is not None:
        if not -180 <= float(longitude) <= 180:
            raise ValidationError('Longitude must be between -180 and 180')


def validate_name(name, field_name='Name'):
    """
    Validate name fields (first name, last name).
    
    Args:
        name: Name to validate
        field_name: Field name for error message
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name or not name.strip():
        raise ValidationError(f'{field_name} is required')
    
    if len(name) < 2:
        raise ValidationError(f'{field_name} must be at least 2 characters long')
    
    if len(name) > 100:
        raise ValidationError(f'{field_name} must not exceed 100 characters')
    
    if not re.match(r'^[a-zA-Z\s\'-]+$', name):
        raise ValidationError(f'{field_name} can only contain letters, spaces, hyphens, and apostrophes')
