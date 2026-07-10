"""Request auditing middleware for API v1 traffic."""
import time

from .services import AuditService


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')


class APIGatewayAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)

        if request.path.startswith('/api/v1/'):
            try:
                user = getattr(request, 'user', None)
                AuditService.record(
                    user_id=user.id if user and user.is_authenticated else None,
                    api_key_id=getattr(
                        getattr(request, '_carebridge_api_key', None), 'id', None,
                    ),
                    method=request.method,
                    path=request.path[:500],
                    status_code=response.status_code,
                    ip_address=_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    duration_ms=max(
                        0, int((time.perf_counter() - started) * 1000),
                    ),
                )
            except Exception:
                # Auditing must never break an API response.
                pass
        return response
