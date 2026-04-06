"""
Global exception handler for Django REST Framework.
Returns consistent, structured JSON error responses.
"""

import logging
import traceback

from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
    NotAuthenticated,
    AuthenticationFailed,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("inventory")


def custom_exception_handler(exc, context):
    """
    Centralized exception handler that returns structured JSON responses.

    Response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": { ... }  // optional
        }
    }
    """

    # Let DRF handle standard exceptions first
    response = exception_handler(exc, context)

    # Build structured error payload
    if isinstance(exc, Http404):
        error_payload = _build_error(
            code="NOT_FOUND",
            message="The requested resource was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif isinstance(exc, PermissionDenied):
        error_payload = _build_error(
            code="PERMISSION_DENIED",
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        error_payload = _build_error(
            code="AUTHENTICATION_FAILED",
            message=str(exc.detail) if hasattr(exc, "detail") else "Authentication credentials were not provided.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    elif isinstance(exc, DRFValidationError):
        error_payload = _build_error(
            code="VALIDATION_ERROR",
            message="Invalid input data.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=exc.detail,
        )
    elif isinstance(exc, DjangoValidationError):
        error_payload = _build_error(
            code="VALIDATION_ERROR",
            message="Invalid input data.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=exc.message_dict if hasattr(exc, "message_dict") else exc.messages,
        )
    elif isinstance(exc, APIException):
        error_payload = _build_error(
            code=exc.default_code.upper() if hasattr(exc, "default_code") else "API_ERROR",
            message=str(exc.detail) if hasattr(exc, "detail") else str(exc),
            status_code=exc.status_code,
        )
    elif response is not None:
        error_payload = _build_error(
            code="ERROR",
            message=str(response.data) if response.data else "An error occurred.",
            status_code=response.status_code,
        )
    else:
        # Unhandled server error
        logger.error(
            "Unhandled exception: %s\n%s",
            str(exc),
            traceback.format_exc(),
        )
        error_payload = _build_error(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Log non-validation errors
    if not isinstance(exc, (DRFValidationError, DjangoValidationError)):
        view = context.get("view", None)
        logger.warning(
            "Exception in %s: [%s] %s",
            view.__class__.__name__ if view else "unknown",
            error_payload["error"]["code"],
            error_payload["error"]["message"],
        )

    return Response(
        error_payload,
        status=error_payload["error"].pop("_status_code"),
    )


def _build_error(code, message, status_code, details=None):
    """Build a structured error response dict."""
    error = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "_status_code": status_code,  # removed before sending
        },
    }
    if details is not None:
        error["error"]["details"] = details
    return error
