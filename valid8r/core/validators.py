from __future__ import annotations

from collections.abc import Callable
from typing import (
    Generic,
    TypeVar,
)

from valid8r.core.maybe import Maybe

T = TypeVar('T')
U = TypeVar('U')


class Validator(Generic[T]):
    """A wrapper class for validator functions that supports operator overloading."""

    def __init__(self, func: Callable[[T], Maybe[T]]):
        self.func = func

    def __call__(self, value: T) -> Maybe[T]:
        return self.func(value)

    def __and__(self, other: Validator[T]) -> Validator[T]:
        from valid8r.core.combinators import and_then

        return Validator(lambda value: and_then(self.func, other.func)(value))

    def __or__(self, other: Validator[T]) -> Validator[T]:
        from valid8r.core.combinators import or_else

        return Validator(lambda value: or_else(self.func, other.func)(value))

    def __invert__(self) -> Validator[T]:
        from valid8r.core.combinators import not_validator

        return Validator(lambda value: not_validator(self.func, 'Negated validation failed')(value))


def minimum(min_value: T, error_message: str | None = None) -> Validator[T]:
    """Create a validator that ensures a value is at least the minimum."""

    def validator(value: T) -> Maybe[T]:
        if value >= min_value:
            return Maybe.just(value)
        return Maybe.nothing(error_message or f'Value must be at least {min_value}')

    return Validator(validator)


def maximum(max_value: T, error_message: str | None = None) -> Validator[T]:
    """Create a validator that ensures a value is at most the maximum."""

    def validator(value: T) -> Maybe[T]:
        if value <= max_value:
            return Maybe.just(value)
        return Maybe.nothing(error_message or f'Value must be at most {max_value}')

    return Validator(validator)


def between(min_value: T, max_value: T, error_message: str | None = None) -> Validator[T]:
    """Create a validator that ensures a value is between minimum and maximum (inclusive)."""

    def validator(value: T) -> Maybe[T]:
        if min_value <= value <= max_value:
            return Maybe.just(value)
        return Maybe.nothing(error_message or f'Value must be between {min_value} and {max_value}')

    return Validator(validator)


def predicate(pred: Callable[[T], bool], error_message: str) -> Validator[T]:
    """Create a validator using a custom predicate function."""

    def validator(value: T) -> Maybe[T]:
        if pred(value):
            return Maybe.just(value)
        return Maybe.nothing(error_message)

    return Validator(validator)


def length(min_length: int, max_length: int, error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string's length is within bounds."""

    def validator(value: str) -> Maybe[str]:
        if min_length <= len(value) <= max_length:
            return Maybe.just(value)
        return Maybe.nothing(error_message or f'String length must be between {min_length} and {max_length}')

    return Validator(validator)
