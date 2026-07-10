"""
Celery configuration for CareBridge-AI.
Handles asynchronous task processing for notifications, AI operations, and background jobs.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('carebridge')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working"""
    print(f'Request: {self.request!r}')


# Periodic Tasks Configuration
app.conf.beat_schedule = {
    # Check expired bookings every 5 minutes
    'check-expired-bookings': {
        'task': 'apps.bookings.tasks.check_expired_bookings',
        'schedule': crontab(minute='*/5'),
    },
    
    # Send appointment reminders every hour
    'send-appointment-reminders': {
        'task': 'apps.notifications.tasks.send_appointment_reminders',
        'schedule': crontab(minute=0),
    },
    
    # Update companion trust scores daily at 2 AM
    'update-trust-scores': {
        'task': 'apps.ai_engine.tasks.update_companion_trust_scores',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Generate analytics reports daily at 3 AM
    'generate-daily-analytics': {
        'task': 'apps.analytics.tasks.generate_daily_report',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Clean up old notifications weekly on Sunday at 4 AM
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },
    
    # Check inactive care journeys every 10 minutes
    'check-inactive-journeys': {
        'task': 'apps.care_journey.tasks.check_inactive_journeys',
        'schedule': crontab(minute='*/10'),
    },
    
    # Process pending payments every 30 minutes
    'process-pending-payments': {
        'task': 'apps.payments.tasks.process_pending_payments',
        'schedule': crontab(minute='*/30'),
    },
}

# Task Configuration
app.conf.task_routes = {
    'apps.notifications.*': {'queue': 'notifications'},
    'apps.ai_engine.*': {'queue': 'ai_tasks'},
    'apps.payments.*': {'queue': 'payments'},
}

app.conf.task_annotations = {
    'apps.notifications.tasks.send_push_notification': {'rate_limit': '100/m'},
    'apps.notifications.tasks.send_sms': {'rate_limit': '50/m'},
    'apps.notifications.tasks.send_email': {'rate_limit': '200/m'},
}
