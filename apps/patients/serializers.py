"""Serializers for the Patients module."""
from rest_framework import serializers
from .models import Patient, PatientVital, PatientInsurance
from . import constants


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_group',
            'known_allergies', 'chronic_conditions', 'current_medications',
            'special_needs', 'dietary_restrictions', 'mobility_level',
            'requires_wheelchair', 'requires_oxygen', 'requires_stretcher',
            'emergency_notes', 'family_member',
            'preferred_doctor_name', 'preferred_hospital_name', 'preferred_hospital_address',
        ]

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('First name cannot be blank.')
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Last name cannot be blank.')
        return value.strip()


class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_group',
            'known_allergies', 'chronic_conditions', 'current_medications',
            'special_needs', 'dietary_restrictions', 'mobility_level',
            'requires_wheelchair', 'requires_oxygen', 'requires_stretcher',
            'emergency_notes', 'status',
            'preferred_doctor_name', 'preferred_hospital_name', 'preferred_hospital_address',
        ]


class PatientDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_group', 'known_allergies', 'chronic_conditions', 'current_medications',
            'special_needs', 'dietary_restrictions', 'mobility_level',
            'requires_wheelchair', 'requires_oxygen', 'requires_stretcher',
            'emergency_notes', 'status', 'is_primary', 'family_member',
            'preferred_doctor_name', 'preferred_hospital_name', 'preferred_hospital_address',
            'created_at', 'updated_at', 'bmi',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_bmi(self, obj):
        latest = obj.vitals.order_by('-recorded_at').first()
        return latest.bmi if latest else None


class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'date_of_birth', 'blood_group', 'gender', 'status',
            'is_primary', 'mobility_level', 'created_at',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


# ── Vitals ──────────────────────────────────────────────────────────────────

class PatientVitalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientVital
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'oxygen_saturation',
            'blood_glucose', 'weight', 'height', 'notes',
        ]

    def validate(self, data):
        sys = data.get('blood_pressure_systolic')
        dia = data.get('blood_pressure_diastolic')
        if (sys is None) != (dia is None):
            raise serializers.ValidationError(
                'Both systolic and diastolic blood pressure must be provided together.'
            )
        if sys and dia and sys <= dia:
            raise serializers.ValidationError(
                'Systolic pressure must be greater than diastolic pressure.'
            )
        return data


class PatientVitalDetailSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()

    class Meta:
        model = PatientVital
        fields = [
            'id', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'oxygen_saturation',
            'blood_glucose', 'weight', 'height', 'bmi',
            'notes', 'recorded_by', 'recorded_at',
        ]

    def get_bmi(self, obj):
        return obj.bmi


# ── Insurance ────────────────────────────────────────────────────────────────

class PatientInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientInsurance
        fields = [
            'id', 'insurance_type', 'provider_name', 'policy_number',
            'policy_holder_name', 'coverage_amount', 'valid_from',
            'valid_until', 'is_active', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        valid_from = data.get('valid_from')
        valid_until = data.get('valid_until')
        if valid_from and valid_until and valid_from >= valid_until:
            raise serializers.ValidationError(
                'valid_until must be after valid_from.'
            )
        return data
