"""
Constants for Users module.
"""

# Activity types
ACTIVITY_TYPE_LOGIN = 'LOGIN'
ACTIVITY_TYPE_LOGOUT = 'LOGOUT'
ACTIVITY_TYPE_PROFILE_UPDATE = 'PROFILE_UPDATE'
ACTIVITY_TYPE_ACCOUNT_BLOCKED = 'ACCOUNT_BLOCKED'
ACTIVITY_TYPE_ACCOUNT_UNBLOCKED = 'ACCOUNT_UNBLOCKED'
ACTIVITY_TYPE_PASSWORD_CHANGED = 'PASSWORD_CHANGED'
ACTIVITY_TYPE_EMAIL_VERIFIED = 'EMAIL_VERIFIED'
ACTIVITY_TYPE_PHONE_VERIFIED = 'PHONE_VERIFIED'

# Success messages
USER_CREATED_SUCCESS = 'User created successfully.'
USER_UPDATED_SUCCESS = 'User updated successfully.'
USER_BLOCKED_SUCCESS = 'User blocked successfully.'
USER_UNBLOCKED_SUCCESS = 'User unblocked successfully.'
USER_DELETED_SUCCESS = 'User deleted successfully.'

# Validation error messages
INVALID_EMAIL = 'Enter a valid email address.'
INVALID_PHONE = 'Enter a valid phone number with country code (e.g. +91XXXXXXXXXX).'
INVALID_POSTAL_CODE = 'Enter a valid 6-digit postal code.'

# Profile picture constraints
MAX_PROFILE_PICTURE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
