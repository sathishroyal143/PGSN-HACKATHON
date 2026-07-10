"""Persistence helpers for Analytics."""
from django.utils import timezone

from . import constants
from .models import AnalyticsEvent, Insight, Report


class AnalyticsEventRepository:
    @staticmethod
    def create(event_type, actor_id=None, entity_type='', entity_id='', metadata=None):
        return AnalyticsEvent.objects.create(
            event_type=event_type,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else '',
            metadata=metadata or {},
        )

    @staticmethod
    def list(date_from=None, date_to=None, event_type=None):
        queryset = AnalyticsEvent.objects.select_related('actor')
        if date_from:
            queryset = queryset.filter(occurred_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(occurred_at__date__lte=date_to)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        return queryset


class ReportRepository:
    @staticmethod
    def create(**data):
        return Report.objects.create(**data)

    @staticmethod
    def list():
        return Report.objects.select_related('requested_by').all()

    @staticmethod
    def get(report_id):
        return Report.objects.select_related('requested_by').filter(id=report_id).first()

    @staticmethod
    def mark_processing(report):
        report.status = constants.REPORT_PROCESSING
        report.error_message = ''
        report.save(update_fields=['status', 'error_message', 'updated_at'])

    @staticmethod
    def mark_completed(report, data):
        report.status = constants.REPORT_COMPLETED
        report.data = data
        report.generated_at = timezone.now()
        report.save(update_fields=['status', 'data', 'generated_at', 'updated_at'])

    @staticmethod
    def mark_failed(report, message):
        report.status = constants.REPORT_FAILED
        report.error_message = str(message)
        report.save(update_fields=['status', 'error_message', 'updated_at'])


class InsightRepository:
    @staticmethod
    def active():
        now = timezone.now()
        return Insight.objects.filter(is_active=True).exclude(expires_at__lt=now)

    @staticmethod
    def replace_generated(insights):
        Insight.objects.filter(is_active=True).update(is_active=False)
        return Insight.objects.bulk_create([Insight(**item) for item in insights])
