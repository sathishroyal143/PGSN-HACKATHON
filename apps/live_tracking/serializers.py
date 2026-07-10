"""Live Tracking serializers — validation and representation."""
from django.utils import timezone
from rest_framework import serializers

from .models import Geofence, GeofenceEvent, LocationUpdate, Route
from . import constants


class LocationUpdateCreateSerializer(serializers.Serializer):
    """Used to validate incoming GPS pings from the companion app."""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    accuracy = serializers.FloatField(required=False, allow_null=True, min_value=0)
    speed = serializers.FloatField(required=False, allow_null=True, min_value=0)
    heading = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=360)
    altitude = serializers.FloatField(required=False, allow_null=True)
    source = serializers.ChoiceField(
        choices=constants.SOURCE_CHOICES,
        default=constants.SOURCE_COMPANION_APP,
    )
    recorded_at = serializers.DateTimeField(default=timezone.now)

    def validate_latitude(self, value):
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError('Latitude must be between -90 and 90.')
        return value

    def validate_longitude(self, value):
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError('Longitude must be between -180 and 180.')
        return value

    def validate_recorded_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError('recorded_at cannot be in the future.')
        return value


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'booking', 'companion', 'latitude', 'longitude',
            'accuracy', 'speed', 'heading', 'altitude', 'source',
            'recorded_at', 'created_at',
        ]
        read_only_fields = fields


class RouteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            'leg', 'origin_latitude', 'origin_longitude', 'origin_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'polyline', 'distance_meters', 'duration_seconds', 'estimated_arrival',
        ]

    def validate(self, attrs):
        for field in ('origin_latitude', 'origin_longitude', 'destination_latitude', 'destination_longitude'):
            if field not in attrs:
                raise serializers.ValidationError({field: 'This field is required.'})
        return attrs


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            'id', 'booking', 'leg', 'status',
            'origin_latitude', 'origin_longitude', 'origin_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'polyline', 'distance_meters', 'duration_seconds',
            'estimated_arrival', 'actual_arrival',
            'started_at', 'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class RouteETAUpdateSerializer(serializers.Serializer):
    estimated_arrival = serializers.DateTimeField()

    def validate_estimated_arrival(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('ETA cannot be in the past.')
        return value


class GeofenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = [
            'fence_type', 'name', 'latitude', 'longitude', 'radius_meters',
        ]

    def validate_radius_meters(self, value):
        if value < 50 or value > 5000:
            raise serializers.ValidationError('Radius must be between 50 and 5000 meters.')
        return value


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = [
            'id', 'booking', 'fence_type', 'name',
            'latitude', 'longitude', 'radius_meters',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class GeofenceEventSerializer(serializers.ModelSerializer):
    fence_type = serializers.CharField(source='geofence.fence_type', read_only=True)
    fence_name = serializers.CharField(source='geofence.name', read_only=True)

    class Meta:
        model = GeofenceEvent
        fields = [
            'id', 'geofence', 'fence_type', 'fence_name',
            'booking', 'companion', 'event_type',
            'latitude', 'longitude', 'occurred_at', 'created_at',
        ]
        read_only_fields = fields


class TrackingSummarySerializer(serializers.Serializer):
    """Read-only summary returned by the tracking summary endpoint."""
    live_location = serializers.DictField(allow_null=True)
    active_route = serializers.DictField(allow_null=True)
    geofences = serializers.ListField(child=serializers.DictField())
