"""Maybe monad for clean error handling using Success and Failure types."""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar('T')
U = TypeVar('U')


class Maybe(Generic[T], ABC):
    """Base class for the Maybe monad."""

    @staticmethod
    def success(value: T) -> Success[T]:
        """Create a Success containing a value."""
        return Success(value)

    @staticmethod
    def failure(error: str) -> Failure[T]:
        """Create a Failure containing an error message."""
        return Failure(error)

    @abstractmethod
    def is_success(self) -> bool:
        """Check if the Maybe is a Success."""

    @abstractmethod
    def is_failure(self) -> bool:
        """Check if the Maybe is a Failure."""

    @abstractmethod
    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail."""

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Transform the value if present."""

    @abstractmethod
    def value_or(self, default: U) -> T | U:
        """Safely get the value or a default."""


class Success(Maybe[T]):
    """Represents a successful computation with a value."""

    __match_args__ = ('value',)

    def __init__(self, value: T) -> None:
        """Initialize a Success with a value.

        Args:
            value: The successful result value

        """
        self.value = value

    def is_success(self) -> bool:
        """Check if the Maybe is a Success."""
        return True

    def is_failure(self) -> bool:
        """Check if the Maybe is a Failure."""
        return False

    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail."""
        return f(self.value)

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Transform the value."""
        return Success(f(self.value))

    def value_or(self, _default: U) -> T:
        """Safely get the value or a default.

        Default is unused in Success case as we always return the value.
        """
        return self.value

    def __str__(self) -> str:
        """Get a string representation."""
        return f'Success({self.value})'


class Failure(Maybe[T]):
    """Represents a failed computation with an error message."""

    __match_args__ = ('error',)

    def __init__(self, error: str) -> None:
        """Initialize a Failure with an error message.

        Args:
            error: The error message explaining the failure

        """
        self.error = error

    def is_success(self) -> bool:
        """Check if the Maybe is a Success."""
        return False

    def is_failure(self) -> bool:
        """Check if the Maybe is a Failure."""
        return True

    def bind(self, _f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail.

        Function is unused in Failure case as we always propagate the error.
        """
        return Failure(self.error)

    def map(self, _f: Callable[[T], U]) -> Maybe[U]:
        """Transform the value if present.

        Function is unused in Failure case as we always propagate the error.
        """
        return Failure(self.error)

    def value_or(self, default: U) -> U:
        """Safely get the value or a default."""
        if self.error:
            return self.error
        return default

    def __str__(self) -> str:
        """Get a string representation."""
        return f'Failure({self.error})'
