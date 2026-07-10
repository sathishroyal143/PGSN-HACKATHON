"""AI Engine models — AIRequest, AIResponse, MatchScore."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from . import constants

User = get_user_model()


class AIRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests', db_index=True)
    request_type = models.CharField(
        max_length=25, choices=constants.REQUEST_TYPE_CHOICES, db_index=True,
    )
    input_data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=15, choices=constants.STATUS_CHOICES,
        default=constants.STATUS_PENDING, db_index=True,
    )
    error_message = models.TextField(blank=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'request_type']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"AIRequest {self.request_type} [{self.status}] — {self.user_id}"


class AIResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(AIRequest, on_delete=models.CASCADE, related_name='response')
    output_data = models.JSONField(default=dict)
    model_used = models.CharField(max_length=100, blank=True, default='rule_based')
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_responses'

    def __str__(self):
        return f"AIResponse for {self.request_id}"


class MatchScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(AIRequest, on_delete=models.CASCADE, related_name='match_scores', db_index=True)
    companion = models.ForeignKey(
        'companions.CompanionProfile', on_delete=models.CASCADE,
        related_name='match_scores', db_index=True,
    )
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    rating_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    skills_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    experience_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    availability_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rank = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_match_scores'
        ordering = ['rank']
        indexes = [
            models.Index(fields=['request', 'rank']),
        ]

    def __str__(self):
        return f"MatchScore rank={self.rank} score={self.total_score} companion={self.companion_id}"
