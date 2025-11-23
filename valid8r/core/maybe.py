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
    from collections.abc import Awaitable, Callable

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
    async def bind_async(self, f: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        """Async version of bind for composing async validators.

        This method enables chaining async operations that might fail,
        similar to bind() but for async functions.

        Args:
            f: Async function that takes a value and returns Maybe[U]

        Returns:
            Maybe[U]: Result of applying f to the value if Success,
                     or propagated Failure if already failed

        Examples:
            Async validation:

            >>> import asyncio
            >>> async def async_double(x: int) -> Maybe[int]:
            ...     await asyncio.sleep(0.001)
            ...     return Maybe.success(x * 2)
            >>> result = asyncio.run(Maybe.success(21).bind_async(async_double))
            >>> result.value_or(None)
            42

            Chaining async validators:

            >>> async def async_validator(x: int) -> Maybe[int]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return Maybe.failure('must be non-negative')
            ...     return Maybe.success(x)
            >>> result = asyncio.run(Maybe.success(-5).bind_async(async_validator))
            >>> result.is_failure()
            True

        """

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

    async def bind_async(self, f: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        """Async version of bind for composing async validators."""
        return await f(self.value)

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

    def error_detail(self) -> ValidationError:
        """Get the structured ValidationError instance (RFC-001 Phase 2).

        This method provides access to the full structured error with code, path, and context.
        It returns the same object as the `validation_error` property, but follows the
        RFC-001 specification for the public API.

        For backward compatibility, both `error_detail()` and `validation_error` property
        are maintained.

        Returns:
            ValidationError instance with code, message, path, and context

        Examples:
            Access structured error from string failure:

            >>> failure = Failure('Invalid input')
            >>> error = failure.error_detail()
            >>> error.code
            'VALIDATION_ERROR'
            >>> error.message
            'Invalid input'

            Access structured error from ValidationError failure:

            >>> from valid8r.core.errors import ValidationError, ErrorCode
            >>> error = ValidationError(code=ErrorCode.OUT_OF_RANGE, message='Too high', path='.value')
            >>> failure = Failure(error)
            >>> detail = failure.error_detail()
            >>> detail.code
            'OUT_OF_RANGE'
            >>> detail.path
            '.value'

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

    async def bind_async(self, _f: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        """Async version of bind for composing async validators.

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
        # Handle list of ValidationErrors (from Schema validation)
        if isinstance(self._validation_error, list):
            error_count = len(self._validation_error)
            return f'Failure([{error_count} validation errors])'
        # Handle single ValidationError or string
        if hasattr(self._validation_error, 'message'):
            return f'Failure({self._validation_error.message})'
        return f'Failure({self._validation_error})'

    def __repr__(self) -> str:
        """Get a repr representation for debugging and doctests.

        Returns:
            String showing error message (backward compatible format)

        """
        # Handle list of ValidationErrors (from Schema validation)
        if isinstance(self._validation_error, list):
            error_count = len(self._validation_error)
            return f'Failure([{error_count} validation errors])'
        # Handle single ValidationError or string
        if hasattr(self._validation_error, 'message'):
            return f'Failure({self._validation_error.message!r})'
        return f'Failure({self._validation_error!r})'
