"""
Custom exception handlers and responses.
"""
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status


class CustomAPIException(APIException):
    """
    Base custom exception for the API.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred.'


class ValidationException(CustomAPIException):
    """Exception for validation errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error occurred.'


class NotFoundException(CustomAPIException):
    """Exception for resource not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'


class UnauthorizedException(CustomAPIException):
    """Exception for unauthorized access."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication required.'


class PermissionDeniedException(CustomAPIException):
    """Exception for permission denied."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns a consistent response format.
    """
    from rest_framework.views import exception_handler
    
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': 'An error occurred',
            'data': response.data
        }
        
        # Customize message based on status code
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Bad request'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            custom_response_data['message'] = 'Internal server error'
        
        response.data = custom_response_data
    
    return response


class SuccessResponse(Response):
    """
    Custom success response with consistent format.
    """
    def __init__(self, data=None, message='Success', status=status.HTTP_200_OK, **kwargs):
        response_data = {
            'success': True,
            'message': message,
            'data': data
        }
        super().__init__(response_data, status=status, **kwargs)
