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

from valid8r.core.errors import ValidationError

T = TypeVar('T')
U = TypeVar('U')


class Maybe(ABC, Generic[T]):
    """Base class for the Maybe monad."""

    @staticmethod
    def success(value: T) -> Success[T]:
        """Create a Success containing a value."""
        return Success(value)

    @staticmethod
    def failure(error: str | ValidationError) -> Failure[T]:
        """Create a Failure containing an error message or ValidationError.

        Args:
            error: Error message string or ValidationError instance

        Returns:
            Failure instance with the error

        """
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
    def value_or(self, default: T) -> T:
        """Return the contained value or the provided default if this is a Failure."""

    @abstractmethod
    def error_or(self, default: str) -> str:
        """Return the error message or the provided default if this is a Success."""

    @abstractmethod
    def get_error(self) -> str | None:
        """Get the error message if present, otherwise None."""


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

    def value_or(self, _default: T) -> T:
        """Return the contained value (default is ignored for Success)."""
        return self.value

    def error_or(self, default: str) -> str:
        """Return the provided default since Success has no error."""
        return default

    def get_error(self) -> str | None:
        """Get None since Success has no error."""
        return None

    def __str__(self) -> str:
        """Get a string representation."""
        return f'Success({self.value})'

    def __repr__(self) -> str:
        """Get a repr representation for debugging and doctests."""
        return f'Success({self.value!r})'


class Failure(Maybe[T]):
    """Represents a failed computation with an error message or ValidationError.

    Failure now accepts both string error messages (backward compatible) and
    ValidationError instances (new structured error support).

    When a string is provided, it's automatically wrapped in a ValidationError
    with code='VALIDATION_ERROR' for consistent internal handling.

    Examples:
        Backward compatible string error:

        >>> failure = Failure('Something went wrong')
        >>> failure.error_or('')
        'Something went wrong'

        New structured error:

        >>> from valid8r.core.errors import ValidationError, ErrorCode
        >>> error = ValidationError(code=ErrorCode.INVALID_EMAIL, message='Bad email')
        >>> failure = Failure(error)
        >>> failure.validation_error.code
        'INVALID_EMAIL'

    """

    __match_args__ = ('error',)

    def __init__(self, error: str | ValidationError) -> None:
        """Initialize a Failure with an error message or ValidationError.

        Args:
            error: Error message string or ValidationError instance

        """
        if isinstance(error, str):
            # Backward compatibility: wrap string in ValidationError
            self._validation_error = ValidationError(
                code='VALIDATION_ERROR',
                message=error,
                path='',
                context=None,
            )
        else:
            self._validation_error = error

    @property
    def error(self) -> str:
        """Get the error message string (backward compatible for pattern matching).

        This property returns the message string to maintain backward compatibility
        with existing pattern matching code: `case Failure(error): assert error == "message"`

        For structured error access, use the `validation_error` property instead.

        Returns:
            Error message string

        """
        return self._validation_error.message

    @property
    def validation_error(self) -> ValidationError:
        """Get the structured ValidationError instance.

        Use this property to access the full structured error with code, path, and context.

        Returns:
            ValidationError instance

        Examples:
            >>> from valid8r.core.errors import ValidationError, ErrorCode
            >>> error = ValidationError(code=ErrorCode.INVALID_EMAIL, message='Bad email', path='.email')
            >>> failure = Failure(error)
            >>> failure.validation_error.code
            'INVALID_EMAIL'
            >>> failure.validation_error.path
            '.email'

        """
        return self._validation_error

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
        return Failure(self._validation_error)

    def map(self, _f: Callable[[T], U]) -> Maybe[U]:
        """Transform the value if present.

        Function is unused in Failure case as we always propagate the error.
        """
        return Failure(self._validation_error)

    def value_or(self, default: T) -> T:
        """Return the provided default for Failure."""
        return default

    def error_or(self, default: str) -> str:
        """Return the error message string (backward compatible).

        Returns:
            Error message from ValidationError, or default if message is empty

        """
        return self._validation_error.message or default

    def get_error(self) -> str | None:
        """Get the error message string (backward compatible).

        Returns:
            Error message from ValidationError

        """
        return self._validation_error.message

    def __str__(self) -> str:
        """Get a string representation.

        Returns:
            String showing error message (backward compatible format)

        """
        return f'Failure({self._validation_error.message})'

    def __repr__(self) -> str:
        """Get a repr representation for debugging and doctests.

        Returns:
            String showing error message (backward compatible format)

        """
        return f'Failure({self._validation_error.message!r})'
