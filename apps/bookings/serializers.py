"""Bookings serializers."""
from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookingStatusLog
from . import constants


class BookingStatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = BookingStatusLog
        fields = ['id', 'from_status', 'to_status', 'changed_by_name', 'notes', 'created_at']


class BookingListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    companion_name = serializers.CharField(source='companion.get_full_name', read_only=True, default=None)
    companion_id = serializers.IntegerField(read_only=True)
    # service_name is a snapshot field saved at booking time; works for both care_service and package-based bookings
    service_name = serializers.CharField(read_only=True)
    pickup_address = serializers.CharField(read_only=True)
    hospital_name = serializers.CharField(read_only=True, default='')
    patient_id = serializers.UUIDField(read_only=True)
    family_user_id = serializers.IntegerField(source='family_user.id', read_only=True)

    def get_patient_name(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None

    class Meta:
        model = Booking
        fields = [
            'id', 'patient_id', 'patient_name', 'family_user_id', 'companion_name', 'companion_id', 'service_name',
            'booking_type', 'status', 'scheduled_start', 'scheduled_end',
            'quoted_price', 'final_price', 'pickup_address', 'hospital_name', 'created_at',
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    companion_name = serializers.CharField(source='companion.get_full_name', read_only=True, default=None)
    companion_profile_id = serializers.UUIDField(source='companion.companion_profile.id', read_only=True, default=None)
    # service_name snapshot — works regardless of care_service vs service_package
    service_name = serializers.CharField(read_only=True)
    care_service_id = serializers.UUIDField(read_only=True)
    patient_id = serializers.UUIDField(read_only=True)
    companion_id = serializers.IntegerField(read_only=True)
    status_logs = BookingStatusLogSerializer(many=True, read_only=True)

    def get_patient_name(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None

    class Meta:
        model = Booking
        fields = [
            'id', 'family_user', 'patient', 'patient_id', 'patient_name',
            'companion', 'companion_id', 'companion_name', 'companion_profile_id',
            'care_service_id', 'service_package', 'service_name',
            'booking_type', 'status',
            'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end',
            'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'hospital_name', 'hospital_address', 'hospital_latitude', 'hospital_longitude',
            'quoted_price', 'final_price', 'price_breakdown',
            'special_instructions', 'requires_wheelchair', 'requires_oxygen',
            'cancelled_at', 'cancelled_by', 'cancellation_reason',
            'ai_match_score', 'duration_hours', 'status_logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'family_user', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    # Primary: use a CareService UUID (what the UI shows)
    care_service_id = serializers.UUIDField(required=False, allow_null=True)
    # Legacy: direct ServicePackage UUID (backward compat)
    service_package_id = serializers.UUIDField(required=False, allow_null=True)
    booking_type = serializers.ChoiceField(choices=constants.BOOKING_TYPE_CHOICES, default=constants.BOOKING_TYPE_SCHEDULED)
    scheduled_start = serializers.DateTimeField()
    scheduled_end = serializers.DateTimeField()
    pickup_address = serializers.CharField(max_length=500)
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    hospital_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    hospital_address = serializers.CharField(required=False, allow_blank=True)
    hospital_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    hospital_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    requires_wheelchair = serializers.BooleanField(default=False)
    requires_oxygen = serializers.BooleanField(default=False)

    def validate(self, data):
        booking_type = data.get('booking_type', constants.BOOKING_TYPE_SCHEDULED)
        # Emergency bookings are immediate — skip future-time check
        # Instant bookings are same-day — only require end > start
        if booking_type == constants.BOOKING_TYPE_SCHEDULED:
            if data['scheduled_start'] <= timezone.now():
                raise serializers.ValidationError(
                    "Scheduled start must be in the future for scheduled bookings."
                )
        if data['scheduled_end'] <= data['scheduled_start']:
            raise serializers.ValidationError("Scheduled end must be after scheduled start.")
        if not data.get('care_service_id') and not data.get('service_package_id'):
            raise serializers.ValidationError(
                "Either care_service_id or service_package_id must be provided."
            )
        return data


class BookingStatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=constants.BOOKING_STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class BookingCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=5, max_length=500)


class AssignCompanionSerializer(serializers.Serializer):
    companion_id = serializers.IntegerField()


class BookingRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, max_length=500, allow_blank=True, default='')

