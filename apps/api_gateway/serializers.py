"""Serializers for API Gateway."""
from rest_framework import serializers

from . import constants
from .models import APIKey, AuditLog, RateLimit


class APIKeySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = APIKey
        fields = [
            'id', 'owner', 'owner_email', 'name', 'prefix', 'status',
            'scopes', 'rate_limit_per_minute', 'last_used_at',
            'expires_at', 'created_at', 'revoked_at',
        ]
        read_only_fields = fields


class CreateAPIKeySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    owner_id = serializers.IntegerField(required=False, min_value=1)
    scopes = serializers.ListField(
        child=serializers.ChoiceField(choices=constants.SCOPE_CHOICES),
        required=False,
    )
    rate_limit_per_minute = serializers.IntegerField(
        min_value=1, max_value=10000, default=60,
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class CreatedAPIKeySerializer(APIKeySerializer):
    key = serializers.CharField(read_only=True)

    class Meta(APIKeySerializer.Meta):
        fields = APIKeySerializer.Meta.fields + ['key']


class RateLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateLimit
        fields = [
            'id', 'name', 'path_pattern', 'methods', 'requests_per_minute',
            'is_active', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_methods(self, value):
        allowed = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}
        methods = [method.upper() for method in value]
        if any(method not in allowed for method in methods):
            raise serializers.ValidationError('Unsupported HTTP method.')
        return methods


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'request_id', 'user', 'user_email', 'api_key',
            'api_key_name', 'method', 'path', 'status_code',
            'ip_address', 'user_agent', 'duration_ms', 'created_at',
        ]
        read_only_fields = fields
