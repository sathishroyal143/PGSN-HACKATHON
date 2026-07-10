"""
Serializers for Family module.
Handles validation and representation for FamilyProfile, FamilyMember, EmergencyContact.
"""
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import FamilyProfile, FamilyMember, EmergencyContact, RelationshipType


# ─── Emergency Contact ────────────────────────────────────────────────────────

class EmergencyContactSerializer(serializers.ModelSerializer):
    phone_number    = PhoneNumberField()
    alternate_phone = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model  = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone_number',
            'alternate_phone', 'email', 'is_primary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip()


class EmergencyContactCreateSerializer(serializers.ModelSerializer):
    phone_number    = PhoneNumberField()
    alternate_phone = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model  = EmergencyContact
        fields = [
            'name', 'relationship', 'phone_number',
            'alternate_phone', 'email', 'is_primary',
        ]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip()


# ─── Family Member ────────────────────────────────────────────────────────────

class FamilyMemberSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    full_name    = serializers.SerializerMethodField()

    class Meta:
        model  = FamilyMember
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'relationship',
            'phone_number', 'profile_picture',
            'blood_group', 'known_allergies', 'chronic_conditions',
            'is_primary_patient', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class FamilyMemberCreateSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model  = FamilyMember
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'relationship', 'phone_number', 'profile_picture',
            'blood_group', 'known_allergies', 'chronic_conditions',
            'is_primary_patient',
        ]

    def validate_first_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('First name must be at least 2 characters.')
        return value.strip()

    def validate_last_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Last name must be at least 2 characters.')
        return value.strip()

    def validate_date_of_birth(self, value):
        from django.utils import timezone
        if value and value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value


class FamilyMemberUpdateSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model  = FamilyMember
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'relationship', 'phone_number', 'profile_picture',
            'blood_group', 'known_allergies', 'chronic_conditions',
            'is_primary_patient', 'is_active',
        ]

    def validate_date_of_birth(self, value):
        from django.utils import timezone
        if value and value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value


# ─── Family Profile ───────────────────────────────────────────────────────────

class FamilyProfileSerializer(serializers.ModelSerializer):
    members           = FamilyMemberSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    user_full_name    = serializers.SerializerMethodField()
    user_email        = serializers.SerializerMethodField()

    class Meta:
        model  = FamilyProfile
        fields = [
            'id', 'user', 'user_full_name', 'user_email',
            'preferred_language', 'preferred_contact_method',
            'is_premium', 'premium_expires_at',
            'members', 'emergency_contacts',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'user_full_name', 'user_email',
            'is_premium', 'premium_expires_at',
            'created_at', 'updated_at',
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name()

    def get_user_email(self, obj):
        return obj.user.email


class FamilyProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FamilyProfile
        fields = ['preferred_language', 'preferred_contact_method']

    def validate_preferred_language(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Language must be at least 2 characters.')
        return value.strip()
