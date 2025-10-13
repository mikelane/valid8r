"""Assertion helpers for testing with Maybe monads."""

from __future__ import annotations

from typing import (
    Any,
    TypeVar,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

T = TypeVar('T')


def assert_maybe_success(result: Maybe[T], expected_value: Any) -> bool:  # noqa: ANN401
    """Assert that a Maybe is a Success with the expected value.

    Args:
        result: The Maybe instance to check
        expected_value: The expected value inside the Maybe

    Returns:
        True if result is a Success with the expected value, False otherwise

    Examples:
        >>> result = Maybe.success(42)
        >>> assert_maybe_success(result, 42)  # Returns True
        >>> assert_maybe_success(result, 43)  # Returns False

    """
    match result:
        case Success(value):
            return bool(value == expected_value)
        case _:
            return False


def assert_maybe_failure(result: Maybe[T], expected_error: str) -> bool:
    """Assert that a Maybe is a Failure with the expected error message.

    Args:
        result: The Maybe instance to check
        expected_error: The expected error message inside the Maybe

    Returns:
        True if result is a Failure with the expected error, False otherwise

    Examples:
        >>> result = Maybe.failure("Invalid input")
        >>> assert_maybe_failure(result, "Invalid input")  # Returns True
        >>> assert_maybe_failure(result, "Other error")  # Returns False

    """
    match result:
        case Failure(error):
            return error == expected_error
        case _:
            return False


def assert_error_equals(result: Maybe[T], expected_error: str, default: str = '') -> bool:
    """Assert error via error_or helper."""
    return result.error_or(default) == expected_error
