"""
Care Services admin panel.
Provides search, filters, bulk activate/deactivate, ordering, and list display.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceType, ServicePackage, ServicePricing, ServiceCategory, CareService
from . import constants


# ── Legacy admin (kept intact) ────────────────────────────────────────────────

class ServicePricingInline(admin.StackedInline):
    model = ServicePricing
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_emergency', 'status', 'sort_order', 'created_at']
    list_filter = ['status', 'is_emergency']
    search_fields = ['name', 'code']
    ordering = ['sort_order', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'status', 'is_featured', 'sort_order', 'created_at']
    list_filter = ['status', 'is_featured', 'service_type']
    search_fields = ['name', 'slug']
    inlines = [ServicePricingInline]
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['sort_order', 'name']


@admin.register(ServicePricing)
class ServicePricingAdmin(admin.ModelAdmin):
    list_display = ['package', 'pricing_type', 'base_price', 'is_active', 'effective_from', 'effective_until']
    list_filter = ['pricing_type', 'is_active']
    search_fields = ['package__name']
    readonly_fields = ['created_at', 'updated_at']


# ── New admin ──────────────────────────────────────────────────────────────────

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'code']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('id', 'name', 'code', 'description', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


def _bulk_activate(modeladmin, request, queryset):
    count = queryset.filter(is_deleted=False).update(status=constants.STATUS_ACTIVE)
    modeladmin.message_user(request, f'{count} service(s) activated.')


_bulk_activate.short_description = 'Activate selected services'


def _bulk_deactivate(modeladmin, request, queryset):
    count = queryset.filter(is_deleted=False).update(status=constants.STATUS_INACTIVE)
    modeladmin.message_user(request, f'{count} service(s) deactivated.')


_bulk_deactivate.short_description = 'Deactivate selected services'


@admin.register(CareService)
class CareServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_name', 'service_code', 'service_category', 'base_price',
        'estimated_duration', 'status', 'home_visit_supported',
        'hospital_visit_supported', 'emergency_supported', 'ai_recommended',
        'is_deleted', 'created_at',
    ]
    list_filter = [
        'status', 'service_category', 'home_visit_supported',
        'hospital_visit_supported', 'emergency_supported', 'ai_recommended', 'is_deleted',
    ]
    search_fields = ['service_name', 'service_code', 'description']
    ordering = ['service_name']
    readonly_fields = ['id', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
    actions = [_bulk_activate, _bulk_deactivate]
    raw_id_fields = ['created_by', 'updated_by']
    fieldsets = (
        ('Service Info', {
            'fields': (
                'id', 'service_category', 'service_name', 'service_code',
                'description', 'icon', 'status',
            )
        }),
        ('Pricing & Duration', {
            'fields': ('base_price', 'estimated_duration'),
        }),
        ('Visit Types', {
            'fields': ('home_visit_supported', 'hospital_visit_supported', 'emergency_supported'),
        }),
        ('Feature Flags', {
            'fields': ('ai_recommended',),
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Show all records including soft-deleted in admin."""
        return CareService.objects.select_related(
            'service_category', 'created_by', 'updated_by'
        ).all()
