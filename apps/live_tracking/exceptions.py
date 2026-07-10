"""Live Tracking custom exceptions."""
from common.exceptions import CareBridgeBaseException
from rest_framework import status


class TrackingNotActiveException(CareBridgeBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tracking is not active for this booking.'
    default_code = 'tracking_not_active'


class GeofenceNotFoundException(CareBridgeBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Geofence not found.'
    default_code = 'geofence_not_found'


class RouteNotFoundException(CareBridgeBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Route not found.'
    default_code = 'route_not_found'


class InvalidLocationException(CareBridgeBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid location coordinates.'
    default_code = 'invalid_location'


class UnauthorizedTrackingAccessException(CareBridgeBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You are not authorized to access tracking for this booking.'
    default_code = 'unauthorized_tracking_access'
