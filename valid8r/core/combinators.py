"""Combinators for creating complex validation rules.

This module provides functions to combine validators using logical operations like AND, OR, and NOT.
These combinators allow for creation of complex validation chains.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from valid8r.core.maybe import (
    Maybe,
    Success,
)

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar('T')


def and_then(first: Callable[[T], Maybe[T]], second: Callable[[T], Maybe[T]]) -> Callable[[T], Maybe[T]]:
    """Combine two validators with logical AND (both must succeed).

    Args:
        first: The first validator function
        second: The second validator function

    Returns:
        A new validator function that passes only if both validators pass

    """

    def combined_validator(value: T) -> Maybe[T]:
        result = first(value)
        match result:
            case Success(value):
                return second(value)
            case _:
                return result

    return combined_validator


def or_else(first: Callable[[T], Maybe[T]], second: Callable[[T], Maybe[T]]) -> Callable[[T], Maybe[T]]:
    """Combine two validators with logical OR (either can succeed).

    Args:
        first: The first validator function
        second: The second validator function

    Returns:
        A new validator function that passes if either validator passes

    """

    def combined_validator(value: T) -> Maybe[T]:
        result = first(value)
        match result:
            case Success(value):
                return result
            case _:
                return second(value)

    return combined_validator


def not_validator(validator: Callable[[T], Maybe[T]], error_message: str) -> Callable[[T], Maybe[T]]:
    """Negate a validator (success becomes failure and vice versa).

    Args:
        validator: The validator function to negate
        error_message: Error message for when the negated validator fails

    Returns:
        A new validator function that passes if the original validator fails

    """

    def negated_validator(value: T) -> Maybe[T]:
        result = validator(value)
        if result.is_failure():
            return Maybe.success(value)
        return Maybe.failure(error_message)

    return negated_validator
