"""
Standardized API response helpers for CareBridge-AI.
Ensures consistent response structure across all endpoints.
"""

from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK, **kwargs):
    """
    Standard success response format.
    
    Args:
        data: Response data (can be dict, list, or None)
        message: Success message
        status_code: HTTP status code
        **kwargs: Additional response fields
    
    Returns:
        Response with structure:
        {
            "success": true,
            "message": "Success message",
            "data": {...}
        }
    """
    response_data = {
        'success': True,
        'message': message,
    }
    
    if data is not None:
        response_data['data'] = data
    
    # Add any additional fields
    response_data.update(kwargs)
    
    return Response(response_data, status=status_code)


def error_response(message='Error occurred', code='error', details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standard error response format.
    
    Args:
        message: Error message
        code: Error code
        details: Additional error details
        status_code: HTTP status code
    
    Returns:
        Response with structure:
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Error message",
                "details": {...}
            }
        }
    """
    response_data = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }
    
    if details:
        response_data['error']['details'] = details
    
    return Response(response_data, status=status_code)


def paginated_response(queryset, serializer_class, request, message='Data retrieved successfully'):
    """
    Standardized paginated response.
    
    Args:
        queryset: Django queryset
        serializer_class: Serializer class to use
        request: Request object for pagination context
        message: Success message
    
    Returns:
        Response with pagination metadata
    """
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)
    
    return success_response(
        data=serializer.data,
        message=message,
        pagination={
            'count': paginator.page.paginator.count,
            'page': paginator.page.number,
            'page_size': paginator.page_size,
            'total_pages': paginator.page.paginator.num_pages,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        }
    )


def created_response(data=None, message='Resource created successfully'):
    """Success response for resource creation"""
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def updated_response(data=None, message='Resource updated successfully'):
    """Success response for resource update"""
    return success_response(data=data, message=message, status_code=status.HTTP_200_OK)


def deleted_response(message='Resource deleted successfully'):
    """Success response for resource deletion"""
    return success_response(message=message, status_code=status.HTTP_200_OK)


def no_content_response():
    """No content response"""
    return Response(status=status.HTTP_204_NO_CONTENT)


def validation_error_response(errors, message='Validation failed'):
    """Validation error response"""
    return error_response(
        message=message,
        code='validation_error',
        details=errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


def not_found_response(message='Resource not found'):
    """Not found error response"""
    return error_response(
        message=message,
        code='not_found',
        status_code=status.HTTP_404_NOT_FOUND
    )


def permission_denied_response(message='Permission denied'):
    """Permission denied error response"""
    return error_response(
        message=message,
        code='permission_denied',
        status_code=status.HTTP_403_FORBIDDEN
    )


def unauthorized_response(message='Authentication required'):
    """Unauthorized error response"""
    return error_response(
        message=message,
        code='unauthorized',
        status_code=status.HTTP_401_UNAUTHORIZED
    )


__all__ = [
    'success_response',
    'error_response',
    'paginated_response',
    'created_response',
    'updated_response',
    'deleted_response',
    'no_content_response',
    'validation_error_response',
    'not_found_response',
    'permission_denied_response',
    'unauthorized_response',
]
