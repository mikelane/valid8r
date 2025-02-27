"""Maybe monad for clean error handling."""

from __future__ import annotations

from collections.abc import Callable
from typing import (
    Generic,
    TypeVar,
)

T = TypeVar('T')
U = TypeVar('U')


class Maybe(Generic[T]):
    """A Maybe monad implementation that handles computations which might fail.

    The Maybe monad is a functional programming concept that provides a clean
    way to handle operations that might fail, without using exceptions for
    control flow.

    Examples:
        >>> from valid8r.core.maybe import Maybe
        >>> Maybe.just(5)
        Just(5)
        >>> Maybe.nothing("Error")
        Nothing(Error)
        >>> Maybe.just(5).bind(lambda x: Maybe.just(x * 2))
        Just(10)

    """

    def __init__(self, value: T | None = None, error: str | None = None):
        self._value = value
        self._error = error
        self._has_value = error is None

    @staticmethod
    def just(value: T) -> Maybe[T]:
        """Create a Maybe containing a value."""
        return Maybe(value=value)

    @staticmethod
    def nothing(error: str) -> Maybe[T]:
        """Create a Maybe containing an error."""
        return Maybe(error=error)

    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail."""
        if self._has_value:
            return f(self._value)
        return Maybe(error=self._error)

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Transform the value if present."""
        if self._has_value:
            return Maybe.just(f(self._value))
        return Maybe(error=self._error)

    def is_just(self) -> bool:
        """Check if this Maybe contains a value."""
        return self._has_value

    def is_nothing(self) -> bool:
        """Check if this Maybe contains an error."""
        return not self._has_value

    def value(self) -> T:
        """Get the contained value. Unsafe if is_nothing()."""
        if not self._has_value:
            raise ValueError('Cannot get value from Nothing')
        return self._value

    def error(self) -> str:
        """Get the error message. Unsafe if is_just()."""
        if self._has_value:
            raise ValueError('Cannot get error from Just')
        return self._error

    def value_or(self, default: U) -> T | U:
        """Safely get the value or a default."""
        if self._has_value:
            return self._value
        return default

    def __str__(self) -> str:
        if self._has_value:
            return f'Just({self._value})'
        return f'Nothing({self._error})'
