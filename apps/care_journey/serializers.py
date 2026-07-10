"""Care Journey serializers."""
from rest_framework import serializers
from .models import CareJourney, JourneyStep
from . import constants


class JourneyStepSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True, default=None)

    class Meta:
        model = JourneyStep
        fields = [
            'id', 'step_code', 'step_order', 'status',
            'started_at', 'completed_at', 'notes', 'updated_by_name',
        ]


class CareJourneyListSerializer(serializers.ModelSerializer):
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    patient_name = serializers.CharField(source='booking.patient.get_full_name', read_only=True)

    class Meta:
        model = CareJourney
        fields = [
            'id', 'booking_id', 'patient_name',
            'status', 'current_step', 'started_at', 'completed_at', 'created_at',
        ]


class CareJourneyDetailSerializer(serializers.ModelSerializer):
    booking_id = serializers.UUIDField(source='booking.id', read_only=True)
    patient_name = serializers.CharField(source='booking.patient.get_full_name', read_only=True)
    companion_name = serializers.CharField(source='booking.companion.get_full_name', read_only=True, default=None)
    steps = JourneyStepSerializer(many=True, read_only=True)

    class Meta:
        model = CareJourney
        fields = [
            'id', 'booking_id', 'patient_name', 'companion_name',
            'status', 'current_step', 'companion_notes',
            'started_at', 'completed_at', 'steps',
            'created_at', 'updated_at',
        ]


class StartJourneySerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()


class AdvanceStepSerializer(serializers.Serializer):
    step_code = serializers.ChoiceField(choices=constants.JOURNEY_STEPS)
    status = serializers.ChoiceField(choices=constants.STEP_STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateNotesSerializer(serializers.Serializer):
    companion_notes = serializers.CharField(allow_blank=True)
