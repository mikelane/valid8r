"""Core validators for validating values against specific criteria.

This module provides a collection of validator functions for common validation scenarios.
All validators follow the same pattern - they take a value and return a Maybe object
that either contains the validated value or an error message.
"""

from __future__ import annotations

import re
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
        min_value: The minimum allowed value (inclusive)
        error_message: Optional custom error message

    Returns:
        Validator[N]: A validator function that accepts values >= min_value

    Examples:
        >>> from valid8r.core.validators import minimum
        >>> validator = minimum(0)
        >>> validator(5)
        Success(5)
        >>> validator(0)
        Success(0)
        >>> validator(-1).is_failure()
        True
        >>> # With custom error message
        >>> validator = minimum(18, error_message="Must be an adult")
        >>> validator(17).error_or("")
        'Must be an adult'

    """

    def validator(value: N) -> Maybe[N]:
        if value >= min_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be at least {min_value}')

    return Validator(validator)


def maximum(max_value: N, error_message: str | None = None) -> Validator[N]:
    """Create a validator that ensures a value is at most the maximum.

    Args:
        max_value: The maximum allowed value (inclusive)
        error_message: Optional custom error message

    Returns:
        Validator[N]: A validator function that accepts values <= max_value

    Examples:
        >>> from valid8r.core.validators import maximum
        >>> validator = maximum(100)
        >>> validator(50)
        Success(50)
        >>> validator(100)
        Success(100)
        >>> validator(101).is_failure()
        True
        >>> # With custom error message
        >>> validator = maximum(120, error_message="Age too high")
        >>> validator(150).error_or("")
        'Age too high'

    """

    def validator(value: N) -> Maybe[N]:
        if value <= max_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be at most {max_value}')

    return Validator(validator)


def between(min_value: N, max_value: N, error_message: str | None = None) -> Validator[N]:
    """Create a validator that ensures a value is between minimum and maximum (inclusive).

    Args:
        min_value: The minimum allowed value (inclusive)
        max_value: The maximum allowed value (inclusive)
        error_message: Optional custom error message

    Returns:
        Validator[N]: A validator function that accepts values where min_value <= value <= max_value

    Examples:
        >>> from valid8r.core.validators import between
        >>> validator = between(0, 100)
        >>> validator(50)
        Success(50)
        >>> validator(0)
        Success(0)
        >>> validator(100)
        Success(100)
        >>> validator(-1).is_failure()
        True
        >>> validator(101).is_failure()
        True
        >>> # With custom error message
        >>> validator = between(1, 10, error_message="Rating must be 1-10")
        >>> validator(11).error_or("")
        'Rating must be 1-10'

    """

    def validator(value: N) -> Maybe[N]:
        if min_value <= value <= max_value:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be between {min_value} and {max_value}')

    return Validator(validator)


def predicate(pred: Callable[[T], bool], error_message: str) -> Validator[T]:
    """Create a validator using a custom predicate function.

    Allows creating custom validators for any validation logic by providing
    a predicate function that returns True for valid values.

    Args:
        pred: A function that takes a value and returns True if valid, False otherwise
        error_message: Error message to return when validation fails

    Returns:
        Validator[T]: A validator function that applies the predicate

    Examples:
        >>> from valid8r.core.validators import predicate
        >>> # Validate even numbers
        >>> is_even = predicate(lambda x: x % 2 == 0, "Must be even")
        >>> is_even(4)
        Success(4)
        >>> is_even(3).is_failure()
        True
        >>> # Validate string patterns
        >>> starts_with_a = predicate(lambda s: s.startswith('a'), "Must start with 'a'")
        >>> starts_with_a("apple")
        Success('apple')
        >>> starts_with_a("banana").error_or("")
        "Must start with 'a'"

    """

    def validator(value: T) -> Maybe[T]:
        if pred(value):
            return Maybe.success(value)
        return Maybe.failure(error_message)

    return Validator(validator)


def length(min_length: int, max_length: int, error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string's length is within bounds.

    Args:
        min_length: Minimum length of the string (inclusive)
        max_length: Maximum length of the string (inclusive)
        error_message: Optional custom error message

    Returns:
        Validator[str]: A validator function that checks string length

    Examples:
        >>> from valid8r.core.validators import length
        >>> validator = length(3, 10)
        >>> validator("hello")
        Success('hello')
        >>> validator("abc")
        Success('abc')
        >>> validator("abcdefghij")
        Success('abcdefghij')
        >>> validator("ab").is_failure()
        True
        >>> validator("abcdefghijk").is_failure()
        True
        >>> # With custom error message
        >>> validator = length(8, 20, error_message="Password must be 8-20 characters")
        >>> validator("short").error_or("")
        'Password must be 8-20 characters'

    """

    def validator(value: str) -> Maybe[str]:
        if min_length <= len(value) <= max_length:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'String length must be between {min_length} and {max_length}')

    return Validator(validator)


def matches_regex(pattern: str | re.Pattern[str], error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string matches a regular expression pattern.

    Args:
        pattern: Regular expression pattern (string or compiled Pattern object)
        error_message: Optional custom error message

    Returns:
        Validator[str]: A validator function that checks pattern matching

    """
    compiled_pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    def validator(value: str) -> Maybe[str]:
        if compiled_pattern.match(value):
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must match pattern {compiled_pattern.pattern}')

    return Validator(validator)


def in_set(allowed_values: set[T], error_message: str | None = None) -> Validator[T]:
    """Create a validator that ensures a value is in a set of allowed values.

    Args:
        allowed_values: Set of allowed values
        error_message: Optional custom error message

    Returns:
        Validator[T]: A validator function that checks membership

    """

    def validator(value: T) -> Maybe[T]:
        if value in allowed_values:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be one of {allowed_values}')

    return Validator(validator)


def non_empty_string(error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string is not empty.

    Args:
        error_message: Optional custom error message

    Returns:
        Validator[str]: A validator function that checks for non-empty strings

    """

    def validator(value: str) -> Maybe[str]:
        if value.strip():
            return Maybe.success(value)
        return Maybe.failure(error_message or 'String must not be empty')

    return Validator(validator)


def unique_items(error_message: str | None = None) -> Validator[list[T]]:
    """Create a validator that ensures all items in a list are unique.

    Args:
        error_message: Optional custom error message

    Returns:
        Validator[list[T]]: A validator function that checks for unique items

    """

    def validator(value: list[T]) -> Maybe[list[T]]:
        if len(value) == len(set(value)):
            return Maybe.success(value)
        return Maybe.failure(error_message or 'All items must be unique')

    return Validator(validator)
