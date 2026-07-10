"""
Authentication module constants.
"""

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60

# Password Reset Configuration
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = 24
PASSWORD_RESET_MAX_ATTEMPTS = 3

# JWT Token Configuration
ACCESS_TOKEN_LIFETIME_MINUTES = 60
REFRESH_TOKEN_LIFETIME_DAYS = 7
TOKEN_ROTATION_ENABLED = True

# Login Attempt Configuration
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW_HOURS = 1
ACCOUNT_LOCKOUT_DURATION_HOURS = 2

# OTP Types
OTP_TYPE_EMAIL_VERIFICATION = 'EMAIL_VERIFICATION'
OTP_TYPE_PHONE_VERIFICATION = 'PHONE_VERIFICATION'
OTP_TYPE_LOGIN = 'LOGIN'
OTP_TYPE_PASSWORD_RESET = 'PASSWORD_RESET'

OTP_TYPES = [
    OTP_TYPE_EMAIL_VERIFICATION,
    OTP_TYPE_PHONE_VERIFICATION,
    OTP_TYPE_LOGIN,
    OTP_TYPE_PASSWORD_RESET,
]

# Login Attempt Statuses
LOGIN_STATUS_SUCCESS = 'SUCCESS'
LOGIN_STATUS_FAILED = 'FAILED'
LOGIN_STATUS_BLOCKED = 'BLOCKED'

# Login Failure Reasons
FAILURE_INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
FAILURE_USER_NOT_FOUND = 'USER_NOT_FOUND'
FAILURE_USER_BLOCKED = 'USER_BLOCKED'
FAILURE_USER_INACTIVE = 'USER_INACTIVE'
FAILURE_EMAIL_NOT_VERIFIED = 'EMAIL_NOT_VERIFIED'
FAILURE_PHONE_NOT_VERIFIED = 'PHONE_NOT_VERIFIED'
FAILURE_TOO_MANY_ATTEMPTS = 'TOO_MANY_ATTEMPTS'
FAILURE_OTP_REQUIRED = 'OTP_REQUIRED'

# Email Templates
EMAIL_TEMPLATE_WELCOME = 'emails/welcome.html'
EMAIL_TEMPLATE_EMAIL_VERIFICATION = 'emails/email_verification.html'
EMAIL_TEMPLATE_PASSWORD_RESET = 'emails/password_reset.html'
EMAIL_TEMPLATE_LOGIN_ALERT = 'emails/login_alert.html'
EMAIL_TEMPLATE_PASSWORD_CHANGED = 'emails/password_changed.html'

# SMS Templates
SMS_TEMPLATE_PHONE_VERIFICATION = 'Your CareBridge verification code is: {otp_code}. Valid for {minutes} minutes.'
SMS_TEMPLATE_PASSWORD_RESET = 'Your CareBridge password reset code is: {otp_code}. Valid for {minutes} minutes.'
SMS_TEMPLATE_LOGIN_OTP = 'Your CareBridge login code is: {otp_code}. Valid for {minutes} minutes.'

# Email Subjects
EMAIL_SUBJECT_WELCOME = 'Welcome to CareBridge AI'
EMAIL_SUBJECT_EMAIL_VERIFICATION = 'Verify Your Email - CareBridge AI'
EMAIL_SUBJECT_PASSWORD_RESET = 'Reset Your Password - CareBridge AI'
EMAIL_SUBJECT_LOGIN_ALERT = 'New Login Detected - CareBridge AI'
EMAIL_SUBJECT_PASSWORD_CHANGED = 'Password Changed - CareBridge AI'

# User Roles (from users module)
ROLE_ADMIN = 'ADMIN'
ROLE_FAMILY = 'FAMILY'
ROLE_COMPANION = 'COMPANION'
ROLE_SUPPORT = 'SUPPORT'

# Validation Messages
ERROR_INVALID_CREDENTIALS = 'Invalid email or password.'
ERROR_USER_NOT_FOUND = 'User with this email does not exist.'
ERROR_USER_BLOCKED = 'Your account has been blocked. Please contact support.'
ERROR_USER_INACTIVE = 'Your account is inactive. Please contact support.'
ERROR_EMAIL_NOT_VERIFIED = 'Please verify your email before logging in.'
ERROR_PHONE_NOT_VERIFIED = 'Please verify your phone number before logging in.'
ERROR_TOO_MANY_ATTEMPTS = 'Too many failed attempts. Please try again later.'
ERROR_OTP_INVALID = 'Invalid OTP code.'
ERROR_OTP_EXPIRED = 'OTP has expired. Please request a new one.'
ERROR_OTP_ALREADY_USED = 'OTP has already been used.'
ERROR_OTP_MAX_ATTEMPTS = 'Maximum OTP verification attempts reached.'
ERROR_TOKEN_INVALID = 'Invalid or expired token.'
ERROR_TOKEN_ALREADY_USED = 'This token has already been used.'
ERROR_PASSWORD_RESET_FAILED = 'Password reset failed. Please try again.'
ERROR_EMAIL_ALREADY_EXISTS = 'User with this email already exists.'
ERROR_PHONE_ALREADY_EXISTS = 'User with this phone number already exists.'
ERROR_WEAK_PASSWORD = 'Password is too weak. Please choose a stronger password.'
ERROR_PASSWORD_MISMATCH = 'Passwords do not match.'

# Success Messages
SUCCESS_REGISTRATION = 'Registration successful. Please verify your email.'
SUCCESS_LOGIN = 'Login successful.'
SUCCESS_LOGOUT = 'Logout successful.'
SUCCESS_OTP_SENT = 'OTP sent successfully.'
SUCCESS_OTP_VERIFIED = 'OTP verified successfully.'
SUCCESS_EMAIL_VERIFIED = 'Email verified successfully.'
SUCCESS_PHONE_VERIFIED = 'Phone number verified successfully.'
SUCCESS_PASSWORD_RESET_EMAIL_SENT = 'Password reset email sent successfully.'
SUCCESS_PASSWORD_RESET = 'Password reset successful.'
SUCCESS_PASSWORD_CHANGED = 'Password changed successfully.'
SUCCESS_TOKEN_REFRESHED = 'Token refreshed successfully.'

# Rate Limiting
RATE_LIMIT_OTP_PER_HOUR = 10
RATE_LIMIT_PASSWORD_RESET_PER_DAY = 5
RATE_LIMIT_LOGIN_PER_MINUTE = 5

# Device Management
MAX_ACTIVE_SESSIONS_PER_USER = 5
