"""Bookings admin."""
from django.contrib import admin
from .models import Booking, BookingStatusLog


class BookingStatusLogInline(admin.TabularInline):
    model = BookingStatusLog
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'notes', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'companion', 'service_package', 'status', 'booking_type', 'scheduled_start', 'quoted_price']
    list_filter = ['status', 'booking_type']
    search_fields = ['patient__first_name', 'family_user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'price_breakdown']
    inlines = [BookingStatusLogInline]


@admin.register(BookingStatusLog)
class BookingStatusLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'from_status', 'to_status', 'changed_by', 'created_at']
    readonly_fields = ['created_at']
