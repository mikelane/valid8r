"""Structured error model for validation failures.

This module provides the ValidationError dataclass and ErrorCode constants
for structured error handling in the valid8r library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ErrorCode:
    """Standard validation error codes for programmatic error handling.

    Error codes are organized by category to make it easy to find and use
    the appropriate code for different validation scenarios.

    Usage:
        >>> from valid8r.core.errors import ErrorCode, ValidationError
        >>> error = ValidationError(
        ...     code=ErrorCode.INVALID_EMAIL,
        ...     message='Email format is invalid'
        ... )
        >>> error.code == ErrorCode.INVALID_EMAIL
        True

    Categories:
        - Parsing: INVALID_TYPE, INVALID_FORMAT, PARSE_ERROR
        - Numeric: OUT_OF_RANGE, BELOW_MINIMUM, ABOVE_MAXIMUM
        - String: TOO_SHORT, TOO_LONG, PATTERN_MISMATCH, EMPTY_STRING
        - Collection: NOT_IN_SET, DUPLICATE_ITEMS, INVALID_SUBSET
        - Network: INVALID_EMAIL, INVALID_URL, INVALID_IP, INVALID_PHONE
        - Filesystem: PATH_NOT_FOUND, NOT_A_FILE, NOT_A_DIRECTORY, FILE_TOO_LARGE
        - DoS Protection: INPUT_TOO_LONG
        - Generic: CUSTOM_ERROR, VALIDATION_ERROR

    """

    # Parsing errors
    INVALID_TYPE = 'INVALID_TYPE'
    """Type conversion failed (e.g., string to int)"""

    INVALID_FORMAT = 'INVALID_FORMAT'
    """Input format does not match expected pattern"""

    PARSE_ERROR = 'PARSE_ERROR'
    """General parsing failure"""

    # Numeric validators
    OUT_OF_RANGE = 'OUT_OF_RANGE'
    """Value is outside the allowed range"""

    BELOW_MINIMUM = 'BELOW_MINIMUM'
    """Value is below the minimum allowed value"""

    ABOVE_MAXIMUM = 'ABOVE_MAXIMUM'
    """Value is above the maximum allowed value"""

    # String validators
    TOO_SHORT = 'TOO_SHORT'
    """String length is below minimum"""

    TOO_LONG = 'TOO_LONG'
    """String length exceeds maximum"""

    PATTERN_MISMATCH = 'PATTERN_MISMATCH'
    """String does not match required regex pattern"""

    EMPTY_STRING = 'EMPTY_STRING'
    """String is empty when a value is required"""

    # Collection validators
    NOT_IN_SET = 'NOT_IN_SET'
    """Value is not in the allowed set of values"""

    DUPLICATE_ITEMS = 'DUPLICATE_ITEMS'
    """Collection contains duplicate items when uniqueness is required"""

    INVALID_SUBSET = 'INVALID_SUBSET'
    """Collection is not a valid subset of allowed values"""

    # Network validators
    INVALID_EMAIL = 'INVALID_EMAIL'
    """Email address format is invalid"""

    INVALID_URL = 'INVALID_URL'
    """URL format is invalid"""

    INVALID_IP = 'INVALID_IP'
    """IP address format is invalid"""

    INVALID_PHONE = 'INVALID_PHONE'
    """Phone number format is invalid"""

    # Filesystem validators
    PATH_NOT_FOUND = 'PATH_NOT_FOUND'
    """File or directory path does not exist"""

    NOT_A_FILE = 'NOT_A_FILE'
    """Path exists but is not a file"""

    NOT_A_DIRECTORY = 'NOT_A_DIRECTORY'
    """Path exists but is not a directory"""

    FILE_TOO_LARGE = 'FILE_TOO_LARGE'
    """File size exceeds maximum allowed size"""

    # DoS protection
    INPUT_TOO_LONG = 'INPUT_TOO_LONG'
    """Input exceeds maximum length (DoS protection)"""

    # Custom/Generic
    CUSTOM_ERROR = 'CUSTOM_ERROR'
    """User-defined custom validation error"""

    VALIDATION_ERROR = 'VALIDATION_ERROR'
    """Generic validation failure"""


@dataclass(frozen=True)
class ValidationError:
    """Structured validation error with code, message, path, and context.

    ValidationError provides a machine-readable error representation that includes:
    - Error code for programmatic handling
    - Human-readable error message
    - Field path for multi-field validation
    - Additional context for debugging

    The error is immutable (frozen) to prevent accidental modification after creation.

    Attributes:
        code: Machine-readable error code (e.g., 'INVALID_EMAIL', 'OUT_OF_RANGE')
        message: Human-readable error message describing the failure
        path: JSON path to the field that failed (e.g., '.user.email', '.items[0].name')
        context: Additional context dict with debugging information (e.g., {'min': 0, 'max': 100, 'value': 150})

    Examples:
        Basic error with code and message:

        >>> error = ValidationError(code='PARSE_ERROR', message='Failed to parse input')
        >>> error.code
        'PARSE_ERROR'
        >>> error.message
        'Failed to parse input'

        Error with field path:

        >>> error = ValidationError(
        ...     code='INVALID_EMAIL',
        ...     message='Email address format is invalid',
        ...     path='.user.email'
        ... )
        >>> str(error)
        '.user.email: Email address format is invalid'

        Error with validation context:

        >>> error = ValidationError(
        ...     code='OUT_OF_RANGE',
        ...     message='Value must be between 0 and 100',
        ...     path='.user.age',
        ...     context={'value': 150, 'min': 0, 'max': 100}
        ... )
        >>> error.to_dict()  # doctest: +NORMALIZE_WHITESPACE
        {'code': 'OUT_OF_RANGE', 'message': 'Value must be between 0 and 100',
         'path': '.user.age', 'context': {'value': 150, 'min': 0, 'max': 100}}

    """

    code: str
    message: str
    path: str = ''
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """Return human-readable representation with optional path prefix.

        Returns:
            String in format 'path: message' if path is present, otherwise just 'message'

        Examples:
            >>> error = ValidationError(code='TEST', message='Error message', path='.field')
            >>> str(error)
            '.field: Error message'

            >>> error = ValidationError(code='TEST', message='Error message')
            >>> str(error)
            'Error message'

        """
        if self.path:
            return f'{self.path}: {self.message}'
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON serialization.

        Returns empty dict for context if None to ensure consistent JSON structure.

        Returns:
            Dictionary with keys: code, message, path, context

        Examples:
            >>> error = ValidationError(
            ...     code='INVALID_TYPE',
            ...     message='Expected integer',
            ...     path='.age',
            ...     context={'input': 'abc'}
            ... )
            >>> error.to_dict()
            {'code': 'INVALID_TYPE', 'message': 'Expected integer', 'path': '.age', 'context': {'input': 'abc'}}

            >>> error = ValidationError(code='PARSE_ERROR', message='Failed to parse')
            >>> error.to_dict()
            {'code': 'PARSE_ERROR', 'message': 'Failed to parse', 'path': '', 'context': {}}

        """
        return {
            'code': self.code,
            'message': self.message,
            'path': self.path,
            'context': self.context or {},
        }
