"""
Django admin configuration for Users module.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, UserActivity, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = [
        'email',
        'full_name_display',
        'role',
        'phone_number',
        'is_active',
        'is_verified_display',
        'is_profile_complete',
        'created_at',
    ]
    
    list_filter = [
        'role',
        'is_active',
        'is_email_verified',
        'is_phone_verified',
        'is_profile_complete',
        'is_blocked',
        'gender',
        'created_at',
    ]
    
    search_fields = [
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'city',
        'state',
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password', 'phone_number', 'role')
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'gender',
                'date_of_birth',
                'profile_picture',
                'bio',
            )
        }),
        ('Address Information', {
            'fields': (
                'address_line_1',
                'address_line_2',
                'city',
                'state',
                'postal_code',
                'country',
                'latitude',
                'longitude',
            )
        }),
        ('Verification Status', {
            'fields': (
                'is_email_verified',
                'is_phone_verified',
                'is_profile_complete',
                'email_verified_at',
                'phone_verified_at',
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_blocked',
            )
        }),
        ('Notification Preferences', {
            'fields': (
                'notification_enabled',
                'email_notification_enabled',
                'sms_notification_enabled',
                'push_notification_enabled',
                'fcm_token',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'last_login_at',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'phone_number',
                'role',
            ),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': (
                'first_name',
                'last_name',
                'gender',
                'date_of_birth',
            ),
        }),
    )
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login_at',
        'email_verified_at',
        'phone_verified_at',
    ]
    
    def full_name_display(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name_display.short_description = 'Full Name'
    
    def is_verified_display(self, obj):
        """Display verification status with color"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Not Verified</span>'
        )
    is_verified_display.short_description = 'Verified'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset
    
    actions = ['verify_users', 'block_users', 'unblock_users', 'make_companions', 'make_family']
    
    def verify_users(self, request, queryset):
        """Bulk verify users"""
        count = 0
        for user in queryset:
            user.mark_email_verified()
            user.mark_phone_verified()
            count += 1
        self.message_user(request, f'{count} users verified successfully.')
    verify_users.short_description = 'Verify selected users'
    
    def block_users(self, request, queryset):
        """Bulk block users"""
        count = queryset.update(is_blocked=True, is_active=False)
        self.message_user(request, f'{count} users blocked successfully.')
    block_users.short_description = 'Block selected users'
    
    def unblock_users(self, request, queryset):
        """Bulk unblock users"""
        count = queryset.update(is_blocked=False, is_active=True)
        self.message_user(request, f'{count} users unblocked successfully.')
    unblock_users.short_description = 'Unblock selected users'
    
    def make_companions(self, request, queryset):
        """Change role to companion"""
        count = queryset.update(role=UserRole.COMPANION)
        self.message_user(request, f'{count} users changed to companions.')
    make_companions.short_description = 'Change to Companion role'
    
    def make_family(self, request, queryset):
        """Change role to family"""
        count = queryset.update(role=UserRole.FAMILY)
        self.message_user(request, f'{count} users changed to family members.')
    make_family.short_description = 'Change to Family role'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for UserActivity model"""
    
    list_display = [
        'user',
        'activity_type',
        'description',
        'ip_address',
        'created_at',
    ]
    
    list_filter = [
        'activity_type',
        'created_at',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'activity_type',
        'description',
        'ip_address',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'user',
        'activity_type',
        'description',
        'ip_address',
        'user_agent',
        'metadata',
        'created_at',
    ]
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return request.user.is_superuser
