"""AI Engine admin."""
from django.contrib import admin
from .models import AIRequest, AIResponse, MatchScore


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'request_type', 'status', 'processing_time_ms', 'created_at']
    list_filter = ['request_type', 'status']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'model_used', 'tokens_used', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(MatchScore)
class MatchScoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'companion', 'rank', 'total_score', 'created_at']
    list_filter = ['rank']
    readonly_fields = ['id', 'created_at']
