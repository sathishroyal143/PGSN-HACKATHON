"""
Django admin configuration for authentication module.
"""
from django.contrib import admin
from apps.authentication.models import OTP, PasswordResetToken, RefreshToken, LoginAttempt


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin configuration for OTP model."""
    list_display = [
        'id', 'user', 'otp_type', 'email', 'phone_number',
        'is_verified', 'is_used', 'attempts', 'expires_at', 'created_at'
    ]
    list_filter = ['otp_type', 'is_verified', 'is_used', 'created_at']
    search_fields = ['user__email', 'email', 'phone_number', 'otp_code']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'verified_at',
        'ip_address', 'user_agent'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('id', 'user', 'otp_code', 'otp_type')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_used', 'attempts', 'max_attempts')
        }),
        ('Timestamps', {
            'fields': ('expires_at', 'verified_at', 'created_at', 'updated_at')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable add permission in admin."""
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordResetToken model."""
    list_display = [
        'id', 'user', 'is_used', 'expires_at', 'used_at', 'created_at'
    ]
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = [
        'id', 'token', 'created_at', 'used_at',
        'ip_address', 'user_agent'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Token Information', {
            'fields': ('id', 'user', 'token')
        }),
        ('Status', {
            'fields': ('is_used', 'expires_at', 'used_at')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable add permission in admin."""
        return False


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    """Admin configuration for RefreshToken model."""
    list_display = [
        'id', 'user', 'device_name', 'is_revoked', 'is_blacklisted',
        'expires_at', 'created_at'
    ]
    list_filter = ['is_revoked', 'is_blacklisted', 'created_at']
    search_fields = ['user__email', 'jti', 'device_id', 'device_name']
    readonly_fields = [
        'id', 'token', 'jti', 'created_at', 'revoked_at',
        'ip_address', 'user_agent'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Token Information', {
            'fields': ('id', 'user', 'jti', 'token')
        }),
        ('Device Information', {
            'fields': ('device_id', 'device_name')
        }),
        ('Status', {
            'fields': ('is_revoked', 'is_blacklisted', 'expires_at', 'revoked_at')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['revoke_tokens', 'blacklist_tokens']
    
    def revoke_tokens(self, request, queryset):
        """Bulk action to revoke tokens."""
        count = 0
        for token in queryset:
            if not token.is_revoked:
                token.revoke()
                count += 1
        self.message_user(request, f'{count} token(s) revoked successfully.')
    revoke_tokens.short_description = 'Revoke selected tokens'
    
    def blacklist_tokens(self, request, queryset):
        """Bulk action to blacklist tokens."""
        count = 0
        for token in queryset:
            if not token.is_blacklisted:
                token.blacklist()
                count += 1
        self.message_user(request, f'{count} token(s) blacklisted successfully.')
    blacklist_tokens.short_description = 'Blacklist selected tokens'
    
    def has_add_permission(self, request):
        """Disable add permission in admin."""
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for LoginAttempt model."""
    list_display = [
        'id', 'user', 'email', 'status', 'failure_reason',
        'ip_address', 'device_name', 'created_at'
    ]
    list_filter = ['status', 'failure_reason', 'created_at']
    search_fields = ['user__email', 'email', 'phone_number', 'ip_address']
    readonly_fields = [
        'id', 'user', 'email', 'phone_number', 'status',
        'failure_reason', 'ip_address', 'user_agent',
        'device_id', 'device_name', 'location_data', 'created_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'user', 'email', 'phone_number')
        }),
        ('Attempt Status', {
            'fields': ('status', 'failure_reason')
        }),
        ('Device Information', {
            'fields': ('device_id', 'device_name', 'ip_address', 'user_agent')
        }),
        ('Location Data', {
            'fields': ('location_data',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable add permission in admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable change permission in admin."""
        return False
