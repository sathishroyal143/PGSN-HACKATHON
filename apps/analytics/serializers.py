"""Serializers for Analytics endpoints."""
from rest_framework import serializers

from . import constants
from .models import AnalyticsEvent, Insight, Report


class AnalyticsEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source='actor.email', read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'actor', 'actor_email', 'event_type', 'entity_type',
            'entity_id', 'metadata', 'occurred_at',
        ]
        read_only_fields = ['id', 'actor', 'actor_email', 'occurred_at']


class CreateAnalyticsEventSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=constants.EVENT_TYPE_CHOICES)
    entity_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    entity_id = serializers.CharField(max_length=64, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)


class ReportSerializer(serializers.ModelSerializer):
    requested_by_email = serializers.EmailField(
        source='requested_by.email', read_only=True,
    )

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'requested_by',
            'requested_by_email', 'date_from', 'date_to', 'status',
            'filters', 'data', 'error_message', 'generated_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class CreateReportSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    report_type = serializers.ChoiceField(choices=constants.REPORT_TYPE_CHOICES)
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    filters = serializers.JSONField(required=False)

    def validate(self, attrs):
        if attrs['date_from'] > attrs['date_to']:
            raise serializers.ValidationError('date_from must be on or before date_to.')
        return attrs


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = [
            'id', 'title', 'description', 'category', 'severity',
            'metric_name', 'metric_value', 'data', 'is_active',
            'generated_at', 'expires_at',
        ]
        read_only_fields = fields


class DateRangeSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs):
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError(
                    'date_from must be on or before date_to.',
                )
        return attrs
