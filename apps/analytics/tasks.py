"""Scheduled Analytics tasks."""
from celery import shared_task

from .services import InsightService


@shared_task(name='apps.analytics.tasks.generate_daily_report')
def generate_daily_report():
    """Refresh platform insights for the default rolling 30-day period."""
    insights = InsightService.generate()
    return {'generated_insights': len(insights)}
