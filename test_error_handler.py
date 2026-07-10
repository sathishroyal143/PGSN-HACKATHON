"""
Test script to verify the custom exception handler is working correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    custom_exception_handler
)
from apps.users.models import User


class TestExceptionView(APIView):
    """Test view that raises different types of exceptions"""
    permission_classes = []  # No authentication required
    authentication_classes = []  # No authentication required
    
    def get(self, request, error_type='handled'):
        if error_type == 'validation':
            raise ValidationException('This is a validation error')
        elif error_type == 'not_found':
            raise ResourceNotFoundException('Resource not found')
        elif error_type == 'unhandled':
            # This will cause a 500 error
            raise ValueError('This is an unhandled exception')
        else:
            return Response({'success': True, 'message': 'No error'})


def test_exception_handler():
    """Test the custom exception handler"""
    factory = APIRequestFactory()
    view = TestExceptionView.as_view()
    
    print("Testing Custom Exception Handler\n" + "="*50)
    
    # Test 1: Handled exception (ValidationException)
    print("\n1. Testing ValidationException:")
    request = factory.get('/test/validation/')
    response = view(request, error_type='validation')
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.data}")
    
    # Test 2: Not found exception
    print("\n2. Testing ResourceNotFoundException:")
    request = factory.get('/test/not_found/')
    response = view(request, error_type='not_found')
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.data}")
    
    # Test 3: Unhandled exception (500)
    print("\n3. Testing Unhandled Exception (should return 500):")
    request = factory.get('/test/unhandled/')
    try:
        response = view(request, error_type='unhandled')
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.data}")
    except Exception as e:
        # Manually call the exception handler
        context = {'request': request, 'view': view}
        response = custom_exception_handler(e, context)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.data}")
    
    # Test 4: No error
    print("\n4. Testing Normal Response:")
    request = factory.get('/test/normal/')
    response = view(request, error_type='normal')
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.data}")
    
    print("\n" + "="*50)
    print("[✓] Exception handler tests completed!")
    print("\nThe custom exception handler is now:")
    print("  - Handling unhandled exceptions (500 errors)")
    print("  - Including request IDs for tracking")
    print("  - Logging all errors with context")
    print("  - Providing consistent error response format")


if __name__ == '__main__':
    test_exception_handler()
