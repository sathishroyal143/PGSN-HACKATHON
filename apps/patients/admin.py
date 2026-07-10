"""Admin configuration for the Patients module."""
from django.contrib import admin
from .models import Patient, PatientVital, PatientInsurance


class PatientVitalInline(admin.TabularInline):
    model = PatientVital
    extra = 0
    readonly_fields = ['recorded_at']
    fields = [
        'blood_pressure_systolic', 'blood_pressure_diastolic',
        'heart_rate', 'temperature', 'oxygen_saturation',
        'blood_glucose', 'weight', 'height', 'recorded_by', 'recorded_at',
    ]


class PatientInsuranceInline(admin.TabularInline):
    model = PatientInsurance
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 'blood_group', 'gender', 'status',
        'is_primary', 'mobility_level', 'family_profile', 'created_at',
    ]
    list_filter = ['status', 'blood_group', 'gender', 'mobility_level', 'is_primary', 'is_deleted']
    search_fields = ['first_name', 'last_name', 'family_profile__user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [PatientVitalInline, PatientInsuranceInline]
    ordering = ['-created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(PatientVital)
class PatientVitalAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'heart_rate', 'blood_pressure_systolic',
        'blood_pressure_diastolic', 'oxygen_saturation', 'recorded_at',
    ]
    list_filter = ['recorded_at']
    search_fields = ['patient__first_name', 'patient__last_name']
    readonly_fields = ['id', 'recorded_at']
    ordering = ['-recorded_at']


@admin.register(PatientInsurance)
class PatientInsuranceAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'insurance_type', 'provider_name',
        'policy_number', 'is_active', 'valid_until',
    ]
    list_filter = ['insurance_type', 'is_active']
    search_fields = ['patient__first_name', 'patient__last_name', 'policy_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
