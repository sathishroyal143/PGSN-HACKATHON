"""Care Journey admin."""
from django.contrib import admin
from .models import CareJourney, JourneyStep


class JourneyStepInline(admin.TabularInline):
    model = JourneyStep
    extra = 0
    readonly_fields = ['started_at', 'completed_at']


@admin.register(CareJourney)
class CareJourneyAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'status', 'current_step', 'started_at', 'completed_at']
    list_filter = ['status', 'current_step']
    search_fields = ['booking__id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [JourneyStepInline]


@admin.register(JourneyStep)
class JourneyStepAdmin(admin.ModelAdmin):
    list_display = ['id', 'journey', 'step_code', 'step_order', 'status']
    list_filter = ['status', 'step_code']
    readonly_fields = ['id']
