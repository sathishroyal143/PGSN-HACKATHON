"""Analytics models - events, generated reports, and operational insights."""
import uuid

from django.conf import settings
from django.db import models

from . import constants


class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_events',
    )
    event_type = models.CharField(
        max_length=50, choices=constants.EVENT_TYPE_CHOICES, db_index=True,
    )
    entity_type = models.CharField(max_length=50, blank=True, db_index=True)
    entity_id = models.CharField(max_length=64, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'analytics_events'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['event_type', 'occurred_at']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f'{self.event_type} at {self.occurred_at}'


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(
        max_length=30, choices=constants.REPORT_TYPE_CHOICES, db_index=True,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='analytics_reports',
    )
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=constants.REPORT_STATUS_CHOICES,
        default=constants.REPORT_PENDING,
        db_index=True,
    )
    filters = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['requested_by', 'created_at']),
        ]

    def __str__(self):
        return f'{self.title} [{self.status}]'


class Insight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20, choices=constants.INSIGHT_CATEGORY_CHOICES, db_index=True,
    )
    severity = models.CharField(
        max_length=10,
        choices=constants.INSIGHT_SEVERITY_CHOICES,
        default=constants.SEVERITY_INFO,
        db_index=True,
    )
    metric_name = models.CharField(max_length=100, blank=True)
    metric_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
    )
    data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'analytics_insights'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['is_active', 'severity']),
            models.Index(fields=['category', 'generated_at']),
        ]

    def __str__(self):
        return self.title
