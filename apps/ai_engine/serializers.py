"""AI Engine serializers."""
from rest_framework import serializers
from .models import AIRequest, AIResponse, MatchScore
from . import constants


class AIResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIResponse
        fields = ['output_data', 'model_used', 'tokens_used', 'created_at']


class AIRequestSerializer(serializers.ModelSerializer):
    response = AIResponseSerializer(read_only=True)

    class Meta:
        model = AIRequest
        fields = [
            'id', 'request_type', 'input_data', 'status',
            'error_message', 'processing_time_ms', 'response',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class MatchScoreSerializer(serializers.ModelSerializer):
    companion_id = serializers.UUIDField(source='companion.id', read_only=True)
    companion_name = serializers.CharField(source='companion.user.get_full_name', read_only=True)
    availability_status = serializers.CharField(source='companion.availability_status', read_only=True)
    experience_years = serializers.FloatField(source='companion.computed_experience_years', read_only=True)

    class Meta:
        model = MatchScore
        fields = [
            'rank', 'companion_id', 'companion_name', 'availability_status',
            'total_score', 'rating_score', 'skills_score',
            'experience_score', 'trust_score', 'availability_score', 'experience_years',
        ]


# --- Input serializers ---

class CompanionMatchInputSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    required_skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    top_n = serializers.IntegerField(min_value=1, max_value=20, default=10)


class TrustScoreInputSerializer(serializers.Serializer):
    companion_id = serializers.UUIDField()


class PriorityInputSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    is_emergency = serializers.BooleanField(default=False)


class MedicalSummaryInputSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
