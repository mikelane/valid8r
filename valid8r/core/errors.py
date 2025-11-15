"""Structured error model for validation failures.

This module provides the ValidationError dataclass and ErrorCode constants
for structured error handling in the valid8r library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
