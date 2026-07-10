"""
Admin configuration for Family module.
"""
from django.contrib import admin
from .models import FamilyProfile, FamilyMember, EmergencyContact


@admin.register(FamilyProfile)
class FamilyProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'preferred_language', 'preferred_contact_method', 'is_premium', 'is_deleted', 'created_at']
    list_filter = ['is_premium', 'is_deleted', 'preferred_contact_method', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('User', {'fields': ('id', 'user')}),
        ('Preferences', {'fields': ('preferred_language', 'preferred_contact_method')}),
        ('Subscription', {'fields': ('is_premium', 'premium_expires_at')}),
        ('Status', {'fields': ('is_deleted', 'deleted_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'relationship', 'family_profile', 'is_primary_patient', 'is_active', 'is_deleted']
    list_filter = ['relationship', 'gender', 'is_primary_patient', 'is_active', 'is_deleted']
    search_fields = ['first_name', 'last_name', 'family_profile__user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identity', {'fields': ('id', 'family_profile', 'first_name', 'last_name', 'date_of_birth', 'gender', 'relationship')}),
        ('Contact', {'fields': ('phone_number', 'profile_picture')}),
        ('Medical', {'fields': ('blood_group', 'known_allergies', 'chronic_conditions')}),
        ('Status', {'fields': ('is_primary_patient', 'is_active', 'is_deleted', 'deleted_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'relationship', 'phone_number', 'family_profile', 'is_primary', 'created_at']
    list_filter = ['relationship', 'is_primary', 'created_at']
    search_fields = ['name', 'phone_number', 'family_profile__user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-is_primary', 'name']

    fieldsets = (
        ('Identity', {'fields': ('id', 'family_profile', 'name', 'relationship')}),
        ('Contact', {'fields': ('phone_number', 'alternate_phone', 'email')}),
        ('Status', {'fields': ('is_primary',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
