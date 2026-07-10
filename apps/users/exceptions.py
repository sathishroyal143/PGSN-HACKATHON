"""
Custom exceptions for Users module.
"""
from rest_framework import status
from common.exceptions import (
    ResourceNotFoundException,
    BusinessLogicException,
    ConflictException,
    AuthenticationException,
)


class UserNotFoundException(ResourceNotFoundException):
    default_detail = 'User not found.'
    default_code = 'user_not_found'


class UserAlreadyExistsException(ConflictException):
    default_detail = 'A user with this email already exists.'
    default_code = 'user_already_exists'


class PhoneAlreadyExistsException(ConflictException):
    default_detail = 'A user with this phone number already exists.'
    default_code = 'phone_already_exists'


class UserBlockedException(AuthenticationException):
    default_detail = 'This account has been blocked. Please contact support.'
    default_code = 'user_blocked'


class UserInactiveException(AuthenticationException):
    default_detail = 'This account is inactive.'
    default_code = 'user_inactive'


class ProfileIncompleteException(BusinessLogicException):
    default_detail = 'Please complete your profile before proceeding.'
    default_code = 'profile_incomplete'
