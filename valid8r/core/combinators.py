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
    Failure,
    Maybe,
    Success,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Sequence,
    )

    from valid8r.core.errors import ValidationError

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


def validate_all(
    value: str,
    parser: Callable[[str], Maybe[T]],
    validators: Sequence[Callable[[T], Maybe[T]]],
) -> Maybe[T]:
    """Parse and validate a value, collecting ALL validation errors.

    Unlike bind() which stops at the first failure, validate_all() runs all
    validators and collects every error. This is useful for form validation
    where users need to see all problems at once.

    Args:
        value: The string value to parse and validate
        parser: A parser function that converts the string to type T
        validators: A sequence of validator functions to apply to the parsed value

    Returns:
        Success containing the validated value if all validators pass,
        or Failure containing a list of ValidationErrors if any validators fail.
        If the parser fails, returns the parser's Failure immediately.

    Examples:
        Collect all validation errors:

        >>> from valid8r.core.parsers import parse_int
        >>> from valid8r.core.validators import minimum, maximum, predicate
        >>> is_positive = minimum(0, 'Must be positive')
        >>> is_even = predicate(lambda x: x % 2 == 0, 'Must be even')
        >>> result = validate_all('-5', parse_int, [is_positive, is_even])
        >>> result.is_failure()
        True

        Success when all validators pass:

        >>> result = validate_all('42', parse_int, [is_positive, is_even])
        >>> result.is_success()
        True
        >>> result.value_or(0)
        42

    """
    parse_result = parser(value)

    if parse_result.is_failure():
        return parse_result

    parsed_value = parse_result.value_or(None)  # type: ignore[arg-type]
    if parsed_value is None:
        return parse_result

    if not validators:
        return parse_result

    errors: list[ValidationError] = []
    for validator in validators:
        result = validator(parsed_value)
        if result.is_failure() and isinstance(result, Failure):
            errors.append(result.validation_error)

    if errors:
        return Failure(errors)  # type: ignore[arg-type]

    return Maybe.success(parsed_value)
