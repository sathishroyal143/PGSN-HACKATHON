"""Companions serializers."""
from rest_framework import serializers
from .models import CompanionProfile, CompanionSkill, CompanionAvailabilitySlot
from . import constants


class CompanionSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionSkill
        fields = ['id', 'skill', 'proficiency_level', 'verified']
        read_only_fields = ['id', 'verified']


class CompanionAvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionAvailabilitySlot
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'is_active']
        read_only_fields = ['id']


class CompanionProfileListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    experience_years = serializers.FloatField(source='computed_experience_years', read_only=True)

    class Meta:
        model = CompanionProfile
        fields = [
            'id', 'full_name', 'phone', 'profile_picture',
            'experience_years', 'average_rating', 'total_reviews',
            'availability_status', 'status', 'vehicle_type', 'ai_trust_score',
        ]


class CompanionProfileDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    experience_years = serializers.FloatField(source='computed_experience_years', read_only=True)
    skills = CompanionSkillSerializer(many=True, read_only=True)
    availability_slots = CompanionAvailabilitySlotSerializer(many=True, read_only=True)

    class Meta:
        model = CompanionProfile
        fields = [
            'id', 'full_name', 'email', 'phone', 'profile_picture',
            'bio', 'experience_years', 'languages_spoken', 'certifications',
            'vehicle_type', 'vehicle_number',
            'status', 'availability_status',
            'current_latitude', 'current_longitude', 'location_updated_at',
            'average_rating', 'total_reviews', 'total_bookings_completed', 'ai_trust_score',
            'skills', 'availability_slots',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'average_rating', 'total_reviews',
                            'total_bookings_completed', 'ai_trust_score', 'created_at', 'updated_at']


class CompanionProfileWriteSerializer(serializers.ModelSerializer):
    skills = CompanionSkillSerializer(many=True, required=False)
    availability_slots = CompanionAvailabilitySlotSerializer(many=True, required=False)

    class Meta:
        model = CompanionProfile
        fields = [
            'bio', 'experience_years', 'languages_spoken', 'certifications',
            'vehicle_type', 'vehicle_number', 'skills', 'availability_slots',
        ]


class AvailabilityUpdateSerializer(serializers.Serializer):
    availability_status = serializers.ChoiceField(choices=constants.AVAILABILITY_CHOICES)


class LocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
