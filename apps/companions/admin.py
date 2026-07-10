"""Companions admin."""
from django.contrib import admin
from .models import CompanionProfile, CompanionSkill, CompanionAvailabilitySlot


class CompanionSkillInline(admin.TabularInline):
    model = CompanionSkill
    extra = 0


class CompanionAvailabilityInline(admin.TabularInline):
    model = CompanionAvailabilitySlot
    extra = 0


@admin.register(CompanionProfile)
class CompanionProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'availability_status', 'average_rating', 'ai_trust_score', 'total_bookings_completed']
    list_filter = ['status', 'availability_status', 'vehicle_type']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'average_rating', 'total_reviews', 'ai_trust_score']
    inlines = [CompanionSkillInline, CompanionAvailabilityInline]
