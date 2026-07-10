"""
Custom permissions for authentication module.
"""
from rest_framework import permissions


class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Permission to check if user is authenticated and active.
    """
    message = 'User account is not active.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            not request.user.is_blocked
        )


class IsEmailVerified(permissions.BasePermission):
    """
    Permission to check if user's email is verified.
    """
    message = 'Email verification required.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified
        )


class IsPhoneVerified(permissions.BasePermission):
    """
    Permission to check if user's phone is verified.
    """
    message = 'Phone verification required.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_phone_verified
        )


class IsFullyVerified(permissions.BasePermission):
    """
    Permission to check if user's email and phone are both verified.
    """
    message = 'Complete verification required (email and phone).'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified and
            request.user.is_phone_verified
        )


class AllowAny(permissions.BasePermission):
    """
    Allow any user (authenticated or not).
    """
    def has_permission(self, request, view):
        return True
