"""Combinators for creating complex validation rules."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from valid8r.core.maybe import Maybe

T = TypeVar('T')


def and_then(first: Callable[[T], Maybe[T]], second: Callable[[T], Maybe[T]]) -> Callable[[T], Maybe[T]]:
    """Combine two validators with logical AND (both must succeed)."""

    def combined_validator(value: T) -> Maybe[T]:
        return first(value).bind(lambda v: second(v))

    return combined_validator


def or_else(first: Callable[[T], Maybe[T]], second: Callable[[T], Maybe[T]]) -> Callable[[T], Maybe[T]]:
    """Combine two validators with logical OR (either can succeed)."""

    def combined_validator(value: T) -> Maybe[T]:
        result = first(value)
        if result.is_just():
            return result
        return second(value)

    return combined_validator


def not_validator(validator: Callable[[T], Maybe[T]], error_message: str) -> Callable[[T], Maybe[T]]:
    """Negate a validator (success becomes failure and vice versa)."""

    def negated_validator(value: T) -> Maybe[T]:
        result = validator(value)
        if result.is_nothing():
            return Maybe.just(value)
        return Maybe.nothing(error_message)

    return negated_validator
