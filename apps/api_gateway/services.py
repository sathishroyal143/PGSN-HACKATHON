"""Application services for API Gateway."""
import hashlib
import secrets

from django.core.cache import cache
from django.utils import timezone

from . import constants
from .repositories import APIKeyRepository, AuditLogRepository, RateLimitRepository


class APIKeyService:
    @staticmethod
    def _hash(raw_key):
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    @classmethod
    def create(cls, owner_id, name, scopes=None, rate_limit_per_minute=60, expires_at=None):
        raw_key = f'cb_{secrets.token_urlsafe(32)}'
        api_key = APIKeyRepository.create(
            owner_id=owner_id,
            name=name,
            prefix=raw_key[:12],
            hashed_key=cls._hash(raw_key),
            scopes=scopes or [constants.SCOPE_READ],
            rate_limit_per_minute=rate_limit_per_minute,
            expires_at=expires_at,
        )
        return api_key, raw_key

    @classmethod
    def authenticate(cls, raw_key):
        api_key = APIKeyRepository.find_by_hash(cls._hash(raw_key))
        if not api_key or api_key.status != constants.KEY_ACTIVE:
            return None
        if api_key.expires_at and api_key.expires_at <= timezone.now():
            api_key.status = constants.KEY_EXPIRED
            api_key.save(update_fields=['status'])
            return None
        APIKeyRepository.touch(api_key)
        return api_key

    @staticmethod
    def revoke(api_key):
        return APIKeyRepository.revoke(api_key)


class RateLimitService:
    @staticmethod
    def check(identifier, path, method, default_limit=60):
        policy = RateLimitRepository.for_path(path, method)
        limit = policy.requests_per_minute if policy else default_limit
        minute = int(timezone.now().timestamp() // 60)
        cache_key = f'gateway-rate:{identifier}:{path}:{minute}'
        try:
            count = cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, timeout=70)
            count = 1
        return count <= limit, limit


class AuditService:
    @staticmethod
    def record(**data):
        return AuditLogRepository.create(**data)
