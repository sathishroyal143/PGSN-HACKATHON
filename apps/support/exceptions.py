"""Support exceptions."""
from rest_framework.exceptions import APIException
from rest_framework import status


class TicketNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Support ticket not found.'
