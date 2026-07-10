"""Persistence helpers for API Gateway."""
from django.db.models import Avg, Count
from django.utils import timezone

from . import constants
from .models import APIKey, AuditLog, RateLimit


class APIKeyRepository:
    @staticmethod
    def create(**data):
        return APIKey.objects.create(**data)

    @staticmethod
    def list():
        return APIKey.objects.select_related('owner').all()

    @staticmethod
    def get(key_id):
        return APIKey.objects.select_related('owner').filter(id=key_id).first()

    @staticmethod
    def find_by_hash(hashed_key):
        return APIKey.objects.select_related('owner').filter(
            hashed_key=hashed_key,
        ).first()

    @staticmethod
    def touch(api_key):
        APIKey.objects.filter(id=api_key.id).update(last_used_at=timezone.now())

    @staticmethod
    def revoke(api_key):
        api_key.status = constants.KEY_REVOKED
        api_key.revoked_at = timezone.now()
        api_key.save(update_fields=['status', 'revoked_at'])
        return api_key


class RateLimitRepository:
    @staticmethod
    def list():
        return RateLimit.objects.select_related('created_by').all()

    @staticmethod
    def create(**data):
        return RateLimit.objects.create(**data)

    @staticmethod
    def get(policy_id):
        return RateLimit.objects.filter(id=policy_id).first()

    @staticmethod
    def update(policy, **data):
        for field, value in data.items():
            setattr(policy, field, value)
        policy.save()
        return policy

    @staticmethod
    def for_path(path, method):
        policies = RateLimit.objects.filter(is_active=True).order_by(
            '-path_pattern',
        )
        return next(
            (
                policy for policy in policies
                if path.startswith(policy.path_pattern)
                and (not policy.methods or method in policy.methods)
            ),
            None,
        )


class AuditLogRepository:
    @staticmethod
    def create(**data):
        return AuditLog.objects.create(**data)

    @staticmethod
    def list(path=None, status_code=None, method=None):
        queryset = AuditLog.objects.select_related('user', 'api_key')
        if path:
            queryset = queryset.filter(path__icontains=path)
        if status_code:
            queryset = queryset.filter(status_code=status_code)
        if method:
            queryset = queryset.filter(method=method.upper())
        return queryset

    @staticmethod
    def statistics():
        queryset = AuditLog.objects.all()
        summary = queryset.aggregate(
            total_requests=Count('id'),
            average_duration_ms=Avg('duration_ms'),
        )
        summary['error_requests'] = queryset.filter(status_code__gte=400).count()
        summary['by_status'] = list(
            queryset.values('status_code').annotate(count=Count('id')).order_by(
                'status_code',
            )
        )
        return summary
