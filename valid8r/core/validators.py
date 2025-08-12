"""Core validators for validating values against specific criteria.

This module provides a collection of validator functions for common validation scenarios.
All validators follow the same pattern - they take a value and return a Maybe object
that either contains the validated value or an error message.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Generic,
    Protocol,
    TypeVar,
)

from valid8r.core.combinators import (
    and_then,
    not_validator,
    or_else,
)
from valid8r.core.maybe import Maybe

if TYPE_CHECKING:
    from collections.abc import Callable


class SupportsComparison(Protocol):  # noqa: D101
    def __le__(self, other: object, /) -> bool: ...  # noqa: D105
    def __lt__(self, other: object, /) -> bool: ...  # noqa: D105
    def __ge__(self, other: object, /) -> bool: ...  # noqa: D105
    def __gt__(self, other: object, /) -> bool: ...  # noqa: D105
    def __eq__(self, other: object, /) -> bool: ...  # noqa: D105
    def __ne__(self, other: object, /) -> bool: ...  # noqa: D105
    def __hash__(self, /) -> int: ...  # noqa: D105


T = TypeVar('T')
U = TypeVar('U')
N = TypeVar('N', bound=SupportsComparison)


class Validator(Generic[T]):
    """A wrapper class for validator functions that supports operator overloading."""

    def __init__(self, func: Callable[[T], Maybe[T]]) -> None:
        """Initialize a validator with a validation function.

        Args:
            func: A function that takes a value and returns a Maybe

        """
        self.func = func

    def __call__(self, value: T) -> Maybe[T]:
        """Apply the validator to a value.

        Args:
            value: The value to validate

        Returns:
            A Maybe containing either the validated value or an error

        """
        return self.func(value)

    def __and__(self, other: Validator[T]) -> Validator[T]:
        """Combine with another validator using logical AND.

        Args:
            other: Another validator to combine with

        Returns:
            A new validator that passes only if both validators pass

        """
        return Validator(lambda value: and_then(self.func, other.func)(value))

    def __or__(self, other: Validator[T]) -> Validator[T]:
        """Combine with another validator using logical OR.

        Args:
            other: Another validator to combine with

        Returns:
            A new validator that passes if either validator passes

        """
        return Validator(lambda value: or_else(self.func, other.func)(value))

    def __invert__(self) -> Validator[T]:
        """Negate this validator.

        Returns:
            A new validator that passes if this validator fails

        """
        return Validator(lambda value: not_validator(self.func, 'Negated validation failed')(value))


def minimum(min_value: N, error_message: str | None = None) -> Validator[N]:
    """Create a validator that ensures a value is at least the minimum.

    Args:
        min_value: The minimum allowed value
        error_message: Optional custom error message

    Returns:
        A validator function

    """

    def validator(value: N) -> Maybe[N]:
        if value >= min_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be at least {min_value}')

    return Validator(validator)


def maximum(max_value: N, error_message: str | None = None) -> Validator[N]:
    """Create a validator that ensures a value is at most the maximum.

    Args:
        max_value: The maximum allowed value
        error_message: Optional custom error message

    Returns:
        A validator function

    """

    def validator(value: N) -> Maybe[N]:
        if value <= max_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be at most {max_value}')

    return Validator(validator)


def between(min_value: N, max_value: N, error_message: str | None = None) -> Validator[N]:
    """Create a validator that ensures a value is between minimum and maximum (inclusive).

    Args:
        min_value: The minimum allowed value
        max_value: The maximum allowed value
        error_message: Optional custom error message

    Returns:
        A validator function

    """

    def validator(value: N) -> Maybe[N]:
        if min_value <= value <= max_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be between {min_value} and {max_value}')

    return Validator(validator)


def predicate(pred: Callable[[T], bool], error_message: str) -> Validator[T]:
    """Create a validator using a custom predicate function.

    Args:
        pred: A function that takes a value and returns a boolean
        error_message: Error message when validation fails

    Returns:
        A validator function

    """

    def validator(value: T) -> Maybe[T]:
        if pred(value):
            return Maybe.success(value)
        return Maybe.failure(error_message)

    return Validator(validator)


def length(min_length: int, max_length: int, error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string's length is within bounds.

    Args:
        min_length: Minimum length of the string
        max_length: Maximum length of the string
        error_message: Optional custom error message

    Returns:
        A validator function

    """

    def validator(value: str) -> Maybe[str]:
        if min_length <= len(value) <= max_length:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'String length must be between {min_length} and {max_length}')

    return Validator(validator)
