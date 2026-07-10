"""
Custom permissions for Users module.
"""

from rest_framework import permissions

from .models import UserRole


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow users to edit their own profile or admins.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any profile
        if request.user.role == UserRole.ADMIN:
            return True
        
        # User can only access their own profile
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN and
            request.user.is_active
        )


class IsFamilyUser(permissions.BasePermission):
    """
    Permission to only allow family users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.FAMILY and
            request.user.is_active
        )


class IsCompanionUser(permissions.BasePermission):
    """
    Permission to only allow companion users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.COMPANION and
            request.user.is_active
        )


class IsSupportUser(permissions.BasePermission):
    """
    Permission to only allow support users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.SUPPORT and
            request.user.is_active
        )


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to only allow verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified and
            request.user.is_phone_verified and
            request.user.is_active and
            not request.user.is_blocked
        )


class HasCompleteProfile(permissions.BasePermission):
    """
    Permission to only allow users with complete profiles.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_profile_complete and
            request.user.is_active
        )


class IsActiveUser(permissions.BasePermission):
    """
    Permission to only allow active non-blocked users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            not request.user.is_blocked
        )


class CanModifyUser(permissions.BasePermission):
    """
    Permission to check if user can modify another user's data.
    Admin can modify anyone.
    User can only modify themselves.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Admin can modify anyone
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Users can only modify themselves
        return obj == request.user


class CanBlockUser(permissions.BasePermission):
    """
    Permission to check if user can block/unblock accounts.
    Only admins can block users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN and
            request.user.is_active
        )


class CanViewAllUsers(permissions.BasePermission):
    """
    Permission to view all users.
    Admin and support staff can view all users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.ADMIN, UserRole.SUPPORT] and
            request.user.is_active
        )


class CanChangeRole(permissions.BasePermission):
    """
    Permission to change user roles.
    Only admins can change roles.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN and
            request.user.is_staff and
            request.user.is_active
        )
