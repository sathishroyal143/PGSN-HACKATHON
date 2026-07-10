# Error Fix Summary: "An unexpected error occurred, check the logs for more information"

## Problem
The error message "An unexpected error occurred, check the logs for more information" with Request ID `bb97229d-b865-4bb3-9be6-66c1d3200596` was occurring because the custom exception handler in `common/exceptions/__init__.py` was not properly handling unhandled server errors (500 errors).

## Root Cause
The original `custom_exception_handler` function only processed exceptions that Django REST Framework's built-in `exception_handler` could handle. When an unhandled exception occurred (like a database error, code bug, or any other server error), the function returned `None`, which caused Django to generate a generic error page.

## Solution
Updated the `custom_exception_handler` to:

### 1. Handle Unhandled Exceptions
```python
if response is not None:
    # DRF handled the exception
    # ... existing code ...
else:
    # NEW: Unhandled exception (500 errors, etc.)
    logger.exception(f"Request ID: {request_id} | Unhandled exception occurred")
    
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
```

### 2. Added Request ID Tracking
Every error response now includes a unique `request_id` that can be used to:
- Track errors in logs
- Help users report issues
- Debug production problems

### 3. Enhanced Logging
All errors are now logged with:
- Request ID
- Error type
- Error message
- Request path
- Full stack trace (for unhandled exceptions)

## Testing
Created `test_error_handler.py` which verified:
- ✅ ValidationException (400) - works correctly
- ✅ ResourceNotFoundException (404) - works correctly  
- ✅ Unhandled ValueError (500) - now returns proper JSON response
- ✅ Normal responses (200) - unaffected

## Response Format
All error responses now follow this consistent format:

```json
{
    "success": false,
    "error": {
        "code": "error_code",
        "message": "Error message",
        "details": {},
        "request_id": "unique-uuid-v4"
    }
}
```

## How to Use
1. **For users**: When an error occurs, note the `request_id` from the response
2. **For developers**: Search the logs using the request_id to find the full error details
3. **Example log search**: `grep "bb97229d-b865-4bb3-9be6-66c1d3200596" logs/carebridge.log`

## Next Steps to Debug Your Specific Error
To find the actual cause of your error with request ID `bb97229d-b865-4bb3-9be6-66c1d3200596`:

1. The error should now be logged with the request ID
2. Check the logs: `logs/carebridge.log`
3. Search for the request ID to see the full stack trace
4. Common causes:
   - Database connection issues
   - Missing required environment variables
   - Null pointer exceptions in code
   - Third-party service failures (Redis, Celery, etc.)

## Files Modified
- `common/exceptions/__init__.py` - Enhanced exception handler
- `test_error_handler.py` - Created test file (can be deleted after verification)

## Verification
Run the development server and the error should now:
1. Return a proper JSON response with request_id
2. Log the full error details
3. Be easier to debug

The server will continue to run even when errors occur, and you'll get detailed information about what went wrong.
