"""Read-side selectors for API Gateway."""
from .repositories import APIKeyRepository, AuditLogRepository, RateLimitRepository


class APIKeySelectors:
    list = staticmethod(APIKeyRepository.list)
    get = staticmethod(APIKeyRepository.get)


class RateLimitSelectors:
    list = staticmethod(RateLimitRepository.list)
    get = staticmethod(RateLimitRepository.get)


class AuditLogSelectors:
    list = staticmethod(AuditLogRepository.list)
    statistics = staticmethod(AuditLogRepository.statistics)
