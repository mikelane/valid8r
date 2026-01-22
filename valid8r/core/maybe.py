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


class UnwrapError(ValueError):
    """Exception raised when unwrap() or expect() is called on Failure, or unwrap_err() on Success.

    This exception provides type-safe value extraction from Maybe types.
    When users need to extract a value and are certain the operation succeeded,
    they can use unwrap() or expect() which will raise this exception on failure.

    Inherits from ValueError since the error represents an invalid operation
    on a value (attempting to extract from wrong state).

    Examples:
        Using unwrap() on Failure:

        >>> result = Maybe.failure('validation error')
        >>> try:
        ...     result.unwrap()
        ... except UnwrapError as e:
        ...     print(f'Error: {e}')
        Error: Called unwrap() on Failure: validation error

        Using expect() with custom message:

        >>> result = Maybe.failure('internal error')
        >>> try:
        ...     result.expect('User ID is required')
        ... except UnwrapError as e:
        ...     print(f'Error: {e}')
        Error: User ID is required

    """


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
    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail. Python-friendly alias for bind().

        This method is functionally identical to bind() but uses naming more
        familiar to Python developers. Use whichever name fits your style.

        Args:
            f: Function that takes a value and returns Maybe[U]

        Returns:
            Maybe[U]: Result of applying f to the value if Success,
                     or propagated Failure if already failed

        Examples:
            Chain operations using and_then:

            >>> result = Maybe.success(5).and_then(lambda x: Maybe.success(x * 2))
            >>> result.value_or(0)
            10

            Propagates failure:

            >>> result = Maybe.failure('error').and_then(lambda x: Maybe.success(x * 2))
            >>> result.is_failure()
            True

        """

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

    @abstractmethod
    def unwrap(self) -> T:
        """Extract value or raise UnwrapError if Failure.

        This method provides type-safe value extraction when you're confident
        the Maybe is a Success. Unlike value_or(), it doesn't require a default
        value and the return type is T (not T | default_type).

        Returns:
            The contained value of type T

        Raises:
            UnwrapError: If called on a Failure

        Examples:
            Safe extraction after validation:

            >>> result = Maybe.success(42)
            >>> result.unwrap()
            42

            Raises on Failure:

            >>> result = Maybe.failure('invalid input')
            >>> result.unwrap()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            UnwrapError: Called unwrap() on Failure: invalid input

        """

    @abstractmethod
    def expect(self, msg: str) -> T:
        """Extract value or raise UnwrapError with custom message if Failure.

        Similar to unwrap(), but allows providing a custom error message that
        is more meaningful in the context where the extraction happens.

        Args:
            msg: Custom error message to use if this is a Failure

        Returns:
            The contained value of type T

        Raises:
            UnwrapError: If called on a Failure, with the custom message

        Examples:
            With meaningful context:

            >>> result = Maybe.success(42)
            >>> result.expect('User age is required')
            42

            Custom error message on failure:

            >>> result = Maybe.failure('parse error')
            >>> result.expect('Failed to load user profile')  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            UnwrapError: Failed to load user profile

        """

    @abstractmethod
    def unwrap_err(self) -> str:
        """Extract error message or raise UnwrapError if Success.

        This method provides type-safe error extraction when you're confident
        the Maybe is a Failure. Useful in error handling code paths.

        Returns:
            The error message string

        Raises:
            UnwrapError: If called on a Success

        Examples:
            Extract error for logging:

            >>> result = Maybe.failure('validation failed')
            >>> result.unwrap_err()
            'validation failed'

            Raises on Success:

            >>> result = Maybe.success(42)
            >>> result.unwrap_err()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            UnwrapError: Called unwrap_err() on Success

        """

    @abstractmethod
    def to_optional(self) -> T | None:
        """Convert Maybe to an optional value.

        Returns the contained value if Success, or None if Failure.
        This is useful for interoperability with code that uses Optional[T].

        Returns:
            The contained value if Success, None if Failure

        Examples:
            Convert Success to optional:

            >>> result = Maybe.success(42)
            >>> result.to_optional()
            42

            Convert Failure to optional:

            >>> result = Maybe.failure('error')
            >>> result.to_optional() is None
            True

        """

    @staticmethod
    def from_optional(value: T | None, error_msg: str = 'Value was None') -> Maybe[T]:
        """Convert an optional value to Maybe.

        Returns Success(value) if value is not None, otherwise Failure with
        the provided error message. This is useful for interoperability with
        code that uses Optional[T].

        Note: This method distinguishes only None from non-None values.
        Falsy values like 0, '', [], and False are treated as valid values
        and wrapped in Success.

        Args:
            value: The optional value to convert
            error_msg: Error message to use if value is None (default: 'Value was None')

        Returns:
            Success(value) if value is not None, Failure(error_msg) otherwise

        Examples:
            Convert non-None value:

            >>> result = Maybe.from_optional(42)
            >>> result.value_or(0)
            42

            Convert None value:

            >>> result = Maybe.from_optional(None)
            >>> result.is_failure()
            True

            Custom error message:

            >>> result = Maybe.from_optional(None, error_msg='User ID is required')
            >>> result.error_or('')
            'User ID is required'

            Falsy values are valid:

            >>> Maybe.from_optional(0).value_or(-1)
            0
            >>> Maybe.from_optional('').value_or('default')
            ''

        """
        if value is None:
            return Failure(error_msg)
        return Success(value)


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

    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail. Python-friendly alias for bind()."""
        return self.bind(f)

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

    def unwrap(self) -> T:
        """Extract the contained value.

        For Success, always returns the contained value.
        """
        return self.value

    def expect(self, _msg: str) -> T:
        """Extract the contained value, ignoring the message.

        For Success, always returns the contained value. The message
        parameter is ignored since extraction always succeeds.
        """
        return self.value

    def unwrap_err(self) -> str:
        """Raise UnwrapError since Success has no error.

        Raises:
            UnwrapError: Always, since Success doesn't contain an error

        """
        raise UnwrapError('Called unwrap_err() on Success')

    def to_optional(self) -> T | None:
        """Return the contained value.

        For Success, always returns the contained value.
        """
        return self.value

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

    def and_then(self, _f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that might fail. Python-friendly alias for bind().

        Function is unused in Failure case as we always propagate the error.
        """
        return self.bind(_f)

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

    def unwrap(self) -> T:
        """Raise UnwrapError since Failure has no value.

        Raises:
            UnwrapError: Always, with the error message from this Failure

        """
        error_msg = f'Called unwrap() on Failure: {self._validation_error.message}'
        raise UnwrapError(error_msg)

    def expect(self, msg: str) -> T:
        """Raise UnwrapError with custom message.

        Args:
            msg: Custom error message to include in the exception

        Raises:
            UnwrapError: Always, with the custom message

        """
        raise UnwrapError(msg)

    def unwrap_err(self) -> str:
        """Extract the error message.

        For Failure, always returns the error message string.
        """
        return self._validation_error.message

    def to_optional(self) -> T | None:
        """Return None since Failure has no value.

        For Failure, always returns None.
        """
        return None

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
