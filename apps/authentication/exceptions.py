"""
Custom exceptions for authentication module.
All exceptions map to specific HTTP status codes and error codes.
"""
from rest_framework import status
from common.exceptions import (
    CareBridgeBaseException,
    AuthenticationException,
    ValidationException,
    BusinessLogicException,
    RateLimitException,
    ConflictException,
)


class InvalidCredentialsException(AuthenticationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid email or password.'
    default_code = 'invalid_credentials'


class UserNotFoundException(AuthenticationException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'User with this email does not exist.'
    default_code = 'user_not_found'


class UserBlockedException(AuthenticationException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Your account has been blocked. Please contact support.'
    default_code = 'user_blocked'


class UserInactiveException(AuthenticationException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Your account is inactive. Please contact support.'
    default_code = 'user_inactive'


class EmailNotVerifiedException(AuthenticationException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Please verify your email before logging in.'
    default_code = 'email_not_verified'


class PhoneNotVerifiedException(AuthenticationException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Please verify your phone number before logging in.'
    default_code = 'phone_not_verified'


class TooManyAttemptsException(RateLimitException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Too many failed attempts. Please try again later.'
    default_code = 'too_many_attempts'


class OTPInvalidException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid OTP code.'
    default_code = 'otp_invalid'


class OTPExpiredException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'OTP has expired. Please request a new one.'
    default_code = 'otp_expired'


class OTPAlreadyUsedException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'OTP has already been used.'
    default_code = 'otp_already_used'


class OTPMaxAttemptsException(RateLimitException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Maximum OTP verification attempts reached.'
    default_code = 'otp_max_attempts'


class OTPResendCooldownException(RateLimitException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Please wait before requesting a new OTP.'
    default_code = 'otp_resend_cooldown'


class TokenInvalidException(AuthenticationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired token.'
    default_code = 'token_invalid'


class TokenRevokedException(AuthenticationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token has been revoked.'
    default_code = 'token_revoked'


class PasswordResetTokenInvalidException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid or expired password reset token.'
    default_code = 'password_reset_token_invalid'


class PasswordResetMaxAttemptsException(RateLimitException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Maximum password reset requests exceeded. Please try again later.'
    default_code = 'password_reset_max_attempts'


class EmailAlreadyExistsException(ConflictException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'User with this email already exists.'
    default_code = 'email_already_exists'


class PhoneAlreadyExistsException(ConflictException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'User with this phone number already exists.'
    default_code = 'phone_already_exists'


class WeakPasswordException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Password is too weak. Please choose a stronger password.'
    default_code = 'weak_password'


class PasswordMismatchException(ValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Passwords do not match.'
    default_code = 'password_mismatch'


__all__ = [
    'InvalidCredentialsException',
    'UserNotFoundException',
    'UserBlockedException',
    'UserInactiveException',
    'EmailNotVerifiedException',
    'PhoneNotVerifiedException',
    'TooManyAttemptsException',
    'OTPInvalidException',
    'OTPExpiredException',
    'OTPAlreadyUsedException',
    'OTPMaxAttemptsException',
    'OTPResendCooldownException',
    'TokenInvalidException',
    'TokenRevokedException',
    'PasswordResetTokenInvalidException',
    'PasswordResetMaxAttemptsException',
    'EmailAlreadyExistsException',
    'PhoneAlreadyExistsException',
    'WeakPasswordException',
    'PasswordMismatchException',
]
