from django.contrib import admin

from .models import AnalyticsEvent, Insight, Report


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'actor', 'entity_type', 'entity_id', 'occurred_at')
    list_filter = ('event_type', 'entity_type', 'occurred_at')
    search_fields = ('actor__email', 'entity_id')
    readonly_fields = ('id', 'occurred_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'report_type', 'status', 'requested_by', 'date_from',
        'date_to', 'generated_at',
    )
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('title', 'requested_by__email')
    readonly_fields = ('id', 'generated_at', 'created_at', 'updated_at')


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'severity', 'metric_value', 'is_active', 'generated_at',
    )
    list_filter = ('category', 'severity', 'is_active')
    search_fields = ('title', 'description', 'metric_name')
    readonly_fields = ('id', 'generated_at')
