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
    from pathlib import Path


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
    r"""Create a validator that ensures a string matches a regular expression pattern.

    Args:
        pattern: Regular expression pattern (string or compiled Pattern object)
        error_message: Optional custom error message

    Returns:
        Validator[str]: A validator function that checks pattern matching

    Examples:
        >>> from valid8r.core.validators import matches_regex
        >>> import re
        >>> # String pattern
        >>> validator = matches_regex(r'^\\d{3}-\\d{2}-\\d{4}$')
        >>> validator('123-45-6789')
        Success('123-45-6789')
        >>> validator('invalid').is_failure()
        True
        >>> # Compiled regex pattern
        >>> pattern = re.compile(r'^[A-Z][a-z]+$')
        >>> validator = matches_regex(pattern)
        >>> validator('Hello')
        Success('Hello')
        >>> validator('hello').is_failure()
        True
        >>> # With custom error message
        >>> validator = matches_regex(r'^\\d{5}$', error_message='Must be a 5-digit ZIP code')
        >>> validator('1234').error_or('')
        'Must be a 5-digit ZIP code'

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

    Examples:
        >>> from valid8r.core.validators import in_set
        >>> # String values
        >>> validator = in_set({'red', 'green', 'blue'})
        >>> validator('red')
        Success('red')
        >>> validator('yellow').is_failure()
        True
        >>> # Numeric values
        >>> validator = in_set({1, 2, 3, 4, 5})
        >>> validator(3)
        Success(3)
        >>> validator(10).is_failure()
        True
        >>> # With custom error message
        >>> validator = in_set({'small', 'medium', 'large'}, error_message='Size must be S, M, or L')
        >>> validator('extra-large').error_or('')
        'Size must be S, M, or L'

    """

    def validator(value: T) -> Maybe[T]:
        if value in allowed_values:
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be one of {allowed_values}')

    return Validator(validator)


def non_empty_string(error_message: str | None = None) -> Validator[str]:
    """Create a validator that ensures a string is not empty.

    Validates that a string contains at least one non-whitespace character.
    Both empty strings and whitespace-only strings are rejected.

    Args:
        error_message: Optional custom error message

    Returns:
        Validator[str]: A validator function that checks for non-empty strings

    Examples:
        >>> from valid8r.core.validators import non_empty_string
        >>> validator = non_empty_string()
        >>> validator('hello')
        Success('hello')
        >>> validator('  hello  ')
        Success('  hello  ')
        >>> validator('').is_failure()
        True
        >>> validator('   ').is_failure()
        True
        >>> # With custom error message
        >>> validator = non_empty_string(error_message='Name is required')
        >>> validator('').error_or('')
        'Name is required'

    """

    def validator(value: str) -> Maybe[str]:
        if value.strip():
            return Maybe.success(value)
        return Maybe.failure(error_message or 'String must not be empty')

    return Validator(validator)


def unique_items(error_message: str | None = None) -> Validator[list[T]]:
    """Create a validator that ensures all items in a list are unique.

    Validates that a list contains no duplicate elements by comparing
    the list length to the set length.

    Args:
        error_message: Optional custom error message

    Returns:
        Validator[list[T]]: A validator function that checks for unique items

    Examples:
        >>> from valid8r.core.validators import unique_items
        >>> validator = unique_items()
        >>> validator([1, 2, 3, 4, 5])
        Success([1, 2, 3, 4, 5])
        >>> validator([1, 2, 2, 3]).is_failure()
        True
        >>> # Works with strings
        >>> validator(['a', 'b', 'c'])
        Success(['a', 'b', 'c'])
        >>> validator(['a', 'b', 'a']).is_failure()
        True
        >>> # With custom error message
        >>> validator = unique_items(error_message='Duplicate items found')
        >>> validator([1, 1, 2]).error_or('')
        'Duplicate items found'

    """

    def validator(value: list[T]) -> Maybe[list[T]]:
        if len(value) == len(set(value)):
            return Maybe.success(value)
        return Maybe.failure(error_message or 'All items must be unique')

    return Validator(validator)


def subset_of(allowed_set: set[T], error_message: str | None = None) -> Validator[set[T]]:
    """Create a validator that ensures a set is a subset of allowed values.

    Validates that all elements in the input set are contained within
    the allowed set. An empty set is always a valid subset.

    Args:
        allowed_set: The set of allowed values
        error_message: Optional custom error message

    Returns:
        Validator[set[T]]: A validator function that checks subset relationship

    Examples:
        >>> from valid8r.core.validators import subset_of
        >>> validator = subset_of({1, 2, 3, 4, 5})
        >>> validator({1, 2, 3})
        Success({1, 2, 3})
        >>> validator({1, 2, 3, 4, 5, 6}).is_failure()
        True
        >>> # Empty set is valid subset
        >>> validator(set())
        Success(set())
        >>> # With custom error message
        >>> validator = subset_of({'a', 'b', 'c'}, error_message='Invalid characters')
        >>> validator({'a', 'd'}).error_or('')
        'Invalid characters'

    """

    def validator(value: set[T]) -> Maybe[set[T]]:
        if value.issubset(allowed_set):
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be a subset of {allowed_set}')

    return Validator(validator)


def superset_of(required_set: set[T], error_message: str | None = None) -> Validator[set[T]]:
    """Create a validator that ensures a set is a superset of required values.

    Validates that the input set contains all elements from the required set.
    The input set may contain additional elements beyond those required.

    Args:
        required_set: The set of required values
        error_message: Optional custom error message

    Returns:
        Validator[set[T]]: A validator function that checks superset relationship

    Examples:
        >>> from valid8r.core.validators import superset_of
        >>> validator = superset_of({1, 2, 3})
        >>> validator({1, 2, 3, 4, 5})
        Success({1, 2, 3, 4, 5})
        >>> validator({1, 2}).is_failure()
        True
        >>> # Exact match is valid
        >>> validator({1, 2, 3})
        Success({1, 2, 3})
        >>> # With custom error message
        >>> validator = superset_of({'read', 'write'}, error_message='Missing required permissions')
        >>> validator({'read'}).error_or('')
        'Missing required permissions'

    """

    def validator(value: set[T]) -> Maybe[set[T]]:
        if value.issuperset(required_set):
            return Maybe.success(value)
        return Maybe.failure(error_message or f'Value must be a superset of {required_set}')

    return Validator(validator)


def is_sorted(*, reverse: bool = False, error_message: str | None = None) -> Validator[list[N]]:
    """Create a validator that ensures a list is sorted.

    Validates that a list is sorted in either ascending or descending order.
    Uses keyword-only parameters to avoid boolean trap anti-pattern.

    Args:
        reverse: If True, checks for descending order; otherwise ascending (default)
        error_message: Optional custom error message

    Returns:
        Validator[list[N]]: A validator function that checks if list is sorted

    Examples:
        >>> from valid8r.core.validators import is_sorted
        >>> # Ascending order (default)
        >>> validator = is_sorted()
        >>> validator([1, 2, 3, 4, 5])
        Success([1, 2, 3, 4, 5])
        >>> validator([3, 1, 4, 2]).is_failure()
        True
        >>> # Descending order
        >>> validator = is_sorted(reverse=True)
        >>> validator([5, 4, 3, 2, 1])
        Success([5, 4, 3, 2, 1])
        >>> validator([1, 2, 3]).is_failure()
        True
        >>> # Works with strings
        >>> validator = is_sorted()
        >>> validator(['a', 'b', 'c'])
        Success(['a', 'b', 'c'])
        >>> # With custom error message
        >>> validator = is_sorted(error_message='List must be in order')
        >>> validator([3, 1, 2]).error_or('')
        'List must be in order'

    """

    def validator(value: list[N]) -> Maybe[list[N]]:
        sorted_value = sorted(value, reverse=reverse)
        if value == sorted_value:
            return Maybe.success(value)
        direction = 'descending' if reverse else 'ascending'
        return Maybe.failure(error_message or f'List must be sorted in {direction} order')

    return Validator(validator)


def exists() -> Validator[Path]:
    """Create a validator that ensures a path exists on the filesystem.

    Validates that a Path object points to an existing file or directory.
    Follows symbolic links by default (uses Path.exists()).

    Returns:
        Validator[Path]: A validator function that checks path existence

    Examples:
        >>> from pathlib import Path
        >>> from valid8r.core.validators import exists
        >>> # Existing path (doctest creates temp file)
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile() as tmp:
        ...     path = Path(tmp.name)
        ...     exists()(path).is_success()
        True
        >>> # Non-existent path
        >>> path = Path('/nonexistent/file.txt')
        >>> exists()(path).is_failure()
        True
        >>> exists()(path).error_or('')
        'Path does not exist: /nonexistent/file.txt'

    """

    def validator(value: Path) -> Maybe[Path]:
        if value.exists():
            return Maybe.success(value)
        return Maybe.failure(f'Path does not exist: {value}')

    return Validator(validator)


def is_file() -> Validator[Path]:
    """Create a validator that ensures a path is a regular file.

    Validates that a Path object points to an existing regular file
    (not a directory, symlink, socket, etc.). Note that this also checks
    that the path exists. For better error messages, chain with exists() first.

    Returns:
        Validator[Path]: A validator function that checks path is a file

    Examples:
        >>> from pathlib import Path
        >>> from valid8r.core.validators import is_file
        >>> # Regular file
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile() as tmp:
        ...     path = Path(tmp.name)
        ...     is_file()(path).is_success()
        True
        >>> # Directory
        >>> import os
        >>> path = Path(os.getcwd())
        >>> result = is_file()(path)
        >>> result.is_failure()
        True
        >>> 'not a file' in result.error_or('').lower()
        True

    """

    def validator(value: Path) -> Maybe[Path]:
        if value.is_file():
            return Maybe.success(value)
        return Maybe.failure(f'Path is not a file: {value}')

    return Validator(validator)


def is_dir() -> Validator[Path]:
    """Create a validator that ensures a path is a directory.

    Validates that a Path object points to an existing directory.
    Note that this also checks that the path exists. For better error
    messages, chain with exists() first.

    Returns:
        Validator[Path]: A validator function that checks path is a directory

    Examples:
        >>> from pathlib import Path
        >>> from valid8r.core.validators import is_dir
        >>> # Directory
        >>> import os
        >>> path = Path(os.getcwd())
        >>> is_dir()(path).is_success()
        True
        >>> # Regular file
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile() as tmp:
        ...     path = Path(tmp.name)
        ...     result = is_dir()(path)
        ...     result.is_failure()
        True
        >>> # Non-existent path
        >>> path = Path('/nonexistent/dir')
        >>> result = is_dir()(path)
        >>> result.is_failure()
        True
        >>> 'not a directory' in result.error_or('').lower()
        True

    """

    def validator(value: Path) -> Maybe[Path]:
        if value.is_dir():
            return Maybe.success(value)
        return Maybe.failure(f'Path is not a directory: {value}')

    return Validator(validator)
