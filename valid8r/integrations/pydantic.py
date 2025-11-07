"""Pydantic integration for valid8r parsers.

This module provides utilities to convert valid8r parsers (which return Maybe[T])
into Pydantic field validators, enabling seamless integration with FastAPI and
other Pydantic-based frameworks.

Example:
    >>> from pydantic import BaseModel, field_validator
    >>> from valid8r.core import parsers, validators
    >>> from valid8r.integrations.pydantic import validator_from_parser
    >>>
    >>> class User(BaseModel):
    ...     age: int
    ...
    ...     @field_validator('age', mode='before')
    ...     @classmethod
    ...     def validate_age(cls, v):
    ...         return validator_from_parser(
    ...             parsers.parse_int & validators.between(0, 120)
    ...         )(v)

"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from valid8r.core.maybe import Maybe

T = TypeVar('T')


def validator_from_parser(
    parser: Callable[[Any], Maybe[T]],
    *,
    error_prefix: str | None = None,
) -> Callable[[Any], T]:
    """Convert a valid8r parser into a Pydantic field validator.

    This function takes a valid8r parser (any callable that returns Maybe[T])
    and converts it into a function suitable for use with Pydantic's
    field_validator decorator.

    Args:
        parser: A valid8r parser function that returns Maybe[T].
        error_prefix: Optional prefix to prepend to error messages.

    Returns:
        A validator function that returns T on success or raises ValueError
        on failure.

    Raises:
        ValueError: When the parser returns a Failure with the error message.

    Example:
        >>> from valid8r.core import parsers
        >>> validator = validator_from_parser(parsers.parse_int)
        >>> validator('42')
        42
        >>> validator('invalid')  # doctest: +SKIP
        Traceback (most recent call last):
            ...
        ValueError: ...

        >>> # With custom error prefix
        >>> validator = validator_from_parser(parsers.parse_int, error_prefix='User ID')
        >>> validator('invalid')  # doctest: +SKIP
        Traceback (most recent call last):
            ...
        ValueError: User ID: ...

    """
    from valid8r.core.maybe import (  # noqa: PLC0415
        Failure,
        Success,
    )

    def validate(value: Any) -> T:  # noqa: ANN401
        """Validate the value using the parser.

        Args:
            value: The value to validate.

        Returns:
            The parsed value if successful.

        Raises:
            ValueError: If parsing fails.

        """
        result = parser(value)

        match result:
            case Success(parsed_value):
                return parsed_value  # type: ignore[no-any-return]
            case Failure(error_msg):
                if error_prefix:
                    msg = f'{error_prefix}: {error_msg}'
                    raise ValueError(msg)
                raise ValueError(error_msg)
            case _:  # pragma: no cover
                # This should never happen as Maybe only has Success and Failure
                msg = f'Unexpected Maybe type: {type(result)}'
                raise TypeError(msg)

    return validate


__all__ = ['validator_from_parser']
