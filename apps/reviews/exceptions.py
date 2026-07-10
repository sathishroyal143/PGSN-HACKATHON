"""Reviews exceptions."""
from rest_framework.exceptions import APIException
from rest_framework import status


class ReviewNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Review not found.'


class ReviewNotAllowedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Review not allowed.'


class ReviewAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You have already reviewed this booking.'
