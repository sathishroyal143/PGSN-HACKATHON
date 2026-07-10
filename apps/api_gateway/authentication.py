"""DRF authentication using a CareBridge API key."""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, Throttled

from .services import APIKeyService, RateLimitService


class APIKeyAuthentication(BaseAuthentication):
    header = 'HTTP_X_API_KEY'

    def authenticate(self, request):
        raw_key = request.META.get(self.header)
        if not raw_key:
            return None

        api_key = APIKeyService.authenticate(raw_key)
        if not api_key:
            raise AuthenticationFailed('Invalid, revoked, or expired API key.')

        allowed, limit = RateLimitService.check(
            identifier=str(api_key.id),
            path=request.path,
            method=request.method,
            default_limit=api_key.rate_limit_per_minute,
        )
        if not allowed:
            raise Throttled(detail=f'API key limit exceeded ({limit}/minute).')

        request._request._carebridge_api_key = api_key
        return api_key.owner, api_key

    def authenticate_header(self, request):
        """Return WWW-Authenticate header so DRF returns 401 not 403 for unauthenticated requests."""
        return 'Bearer realm="api"'
