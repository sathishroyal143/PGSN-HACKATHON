"""Constants for Live Tracking module."""

# Location update source
SOURCE_COMPANION_APP = 'companion_app'
SOURCE_FAMILY_APP = 'family_app'
SOURCE_SYSTEM = 'system'

SOURCE_CHOICES = [
    (SOURCE_COMPANION_APP, 'Companion App'),
    (SOURCE_FAMILY_APP, 'Family App'),
    (SOURCE_SYSTEM, 'System'),
]

# Route status
ROUTE_STATUS_PLANNED = 'planned'
ROUTE_STATUS_ACTIVE = 'active'
ROUTE_STATUS_COMPLETED = 'completed'
ROUTE_STATUS_CANCELLED = 'cancelled'

ROUTE_STATUS_CHOICES = [
    (ROUTE_STATUS_PLANNED, 'Planned'),
    (ROUTE_STATUS_ACTIVE, 'Active'),
    (ROUTE_STATUS_COMPLETED, 'Completed'),
    (ROUTE_STATUS_CANCELLED, 'Cancelled'),
]

# Route leg types
LEG_PICKUP = 'pickup'
LEG_HOSPITAL = 'hospital'
LEG_DROP = 'drop'

LEG_TYPE_CHOICES = [
    (LEG_PICKUP, 'Pickup'),
    (LEG_HOSPITAL, 'Hospital'),
    (LEG_DROP, 'Drop Home'),
]

# Geofence types
GEOFENCE_PICKUP = 'pickup'
GEOFENCE_HOSPITAL = 'hospital'
GEOFENCE_DROP = 'drop'
GEOFENCE_CUSTOM = 'custom'

GEOFENCE_TYPE_CHOICES = [
    (GEOFENCE_PICKUP, 'Pickup Zone'),
    (GEOFENCE_HOSPITAL, 'Hospital Zone'),
    (GEOFENCE_DROP, 'Drop Zone'),
    (GEOFENCE_CUSTOM, 'Custom Zone'),
]

# Geofence event types
GEOFENCE_EVENT_ENTER = 'enter'
GEOFENCE_EVENT_EXIT = 'exit'

GEOFENCE_EVENT_CHOICES = [
    (GEOFENCE_EVENT_ENTER, 'Enter'),
    (GEOFENCE_EVENT_EXIT, 'Exit'),
]

# WebSocket message types
WS_TYPE_LOCATION_UPDATE = 'location_update'
WS_TYPE_GEOFENCE_EVENT = 'geofence_event'
WS_TYPE_ROUTE_UPDATE = 'route_update'
WS_TYPE_ETA_UPDATE = 'eta_update'
WS_TYPE_TRACKING_STARTED = 'tracking_started'
WS_TYPE_TRACKING_ENDED = 'tracking_ended'
WS_TYPE_ERROR = 'error'

# Tracking group prefix
TRACKING_GROUP_PREFIX = 'tracking_booking_'

# Default geofence radius (meters)
DEFAULT_GEOFENCE_RADIUS_METERS = 200

# Location accuracy threshold (meters) — discard GPS noise below this
MIN_ACCURACY_METERS = 100

# Max location age before considered stale (seconds)
LOCATION_STALE_SECONDS = 300
