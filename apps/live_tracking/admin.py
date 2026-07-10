"""Live Tracking admin configuration."""
from django.contrib import admin
from .models import Geofence, GeofenceEvent, LocationUpdate, Route


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'companion', 'latitude', 'longitude', 'speed', 'source', 'recorded_at']
    list_filter = ['source', 'recorded_at']
    search_fields = ['booking__id', 'companion__email']
    readonly_fields = ['id', 'created_at']
    ordering = ['-recorded_at']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'leg', 'status', 'distance_meters', 'estimated_arrival', 'created_at']
    list_filter = ['leg', 'status']
    search_fields = ['booking__id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'fence_type', 'name', 'radius_meters', 'is_active', 'created_at']
    list_filter = ['fence_type', 'is_active']
    search_fields = ['booking__id', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'geofence', 'booking', 'companion', 'event_type', 'occurred_at']
    list_filter = ['event_type', 'occurred_at']
    search_fields = ['booking__id', 'companion__email']
    readonly_fields = ['id', 'created_at']
    ordering = ['-occurred_at']
