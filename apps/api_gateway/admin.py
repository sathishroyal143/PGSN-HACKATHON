from django.contrib import admin

from .models import APIKey, AuditLog, RateLimit


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'prefix', 'owner', 'status', 'rate_limit_per_minute',
        'last_used_at', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'prefix', 'owner__email')
    readonly_fields = ('id', 'prefix', 'hashed_key', 'last_used_at', 'created_at', 'revoked_at')


@admin.register(RateLimit)
class RateLimitAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'path_pattern', 'requests_per_minute', 'is_active', 'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'path_pattern')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'method', 'path', 'status_code', 'user', 'api_key', 'duration_ms', 'created_at',
    )
    list_filter = ('method', 'status_code', 'created_at')
    search_fields = ('path', 'user__email', 'api_key__name', 'request_id')
    readonly_fields = [field.name for field in AuditLog._meta.fields]
