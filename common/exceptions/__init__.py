"""
Custom exceptions for CareBridge-AI.
Provides standardized error handling across the application.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class CareBridgeBaseException(APIException):
    """Base exception for all CareBridge custom exceptions"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred'
    default_code = 'error'


class ValidationException(CareBridgeBaseException):
    """Exception for validation errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error'
    default_code = 'validation_error'


class ResourceNotFoundException(CareBridgeBaseException):
    """Exception when a resource is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'not_found'


class PermissionDeniedException(CareBridgeBaseException):
    """Exception for permission denied errors"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied'
    default_code = 'permission_denied'


class AuthenticationException(CareBridgeBaseException):
    """Exception for authentication errors"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed'
    default_code = 'authentication_failed'


class BusinessLogicException(CareBridgeBaseException):
    """Exception for business logic violations"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Business logic error'
    default_code = 'business_logic_error'


class ServiceUnavailableException(CareBridgeBaseException):
    """Exception for service unavailability"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable'
    default_code = 'service_unavailable'


class ConflictException(CareBridgeBaseException):
    """Exception for resource conflicts"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict'
    default_code = 'conflict'


class RateLimitException(CareBridgeBaseException):
    """Exception for rate limit exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'rate_limit_exceeded'


class PaymentException(CareBridgeBaseException):
    """Exception for payment processing errors"""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed'
    default_code = 'payment_failed'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Returns:
        Response with structure:
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Error message",
                "details": {},
                "request_id": "unique_request_id"
            }
        }
    """
    import logging
    import uuid
    from rest_framework.response import Response
    
    logger = logging.getLogger('carebridge')
    
    # Get the request ID or generate a new one
    request = context.get('request')
    request_id = str(uuid.uuid4())
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF handled the exception
        custom_response_data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                'details': response.data if isinstance(response.data, dict) else {},
                'request_id': request_id
            }
        }
        response.data = custom_response_data
        
        # Log the error
        logger.error(
            f"Request ID: {request_id} | Error: {exc.__class__.__name__} | "
            f"Message: {str(exc)} | Path: {request.path if request else 'N/A'}"
        )
    else:
        # Unhandled exception (500 errors, etc.)
        logger.exception(
            f"Request ID: {request_id} | Unhandled exception occurred | "
            f"Path: {request.path if request else 'N/A'}",
            exc_info=exc
        )
        
        # Return a generic error response for unhandled exceptions
        custom_response_data = {
            'success': False,
            'error': {
                'code': 'server_error',
                'message': 'An unexpected error occurred, check the logs for more information.',
                'details': {},
                'request_id': request_id
            }
        }
        
        response = Response(
            custom_response_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


__all__ = [
    'CareBridgeBaseException',
    'ValidationException',
    'ResourceNotFoundException',
    'PermissionDeniedException',
    'AuthenticationException',
    'BusinessLogicException',
    'ServiceUnavailableException',
    'ConflictException',
    'RateLimitException',
    'PaymentException',
    'custom_exception_handler',
]
