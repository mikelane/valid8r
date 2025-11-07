"""Pydantic integration for valid8r parsers.

This module provides utilities to convert valid8r parsers (which return Maybe[T])
into Pydantic field validators, enabling seamless integration with FastAPI and
other Pydantic-based frameworks.

The integration supports:
- Simple field validation with type parsing and validation
- Nested model validation with field path error reporting
- List[Model] validation with per-item error reporting
- Dict[K, V] validation with per-value validation
- Optional fields and complex structures

Example - Simple Field Validation:
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

Example - Nested Model Validation:
    >>> from valid8r.core.parsers import PhoneNumber
    >>>
    >>> class Address(BaseModel):
    ...     phone: PhoneNumber
    ...
    ...     @field_validator('phone', mode='before')
    ...     @classmethod
    ...     def validate_phone(cls, v):
    ...         return validator_from_parser(parsers.parse_phone)(v)
    >>>
    >>> class User(BaseModel):
    ...     name: str
    ...     address: Address
    >>>
    >>> # Validation errors include full field path (e.g., 'address.phone')
    >>> user = User(name='Alice', address={'phone': '(206) 234-5678'})

Example - List of Models:
    >>> class LineItem(BaseModel):
    ...     quantity: int
    ...
    ...     @field_validator('quantity', mode='before')
    ...     @classmethod
    ...     def validate_quantity(cls, v):
    ...         def parser(value):
    ...             return parsers.parse_int(value).bind(validators.minimum(1))
    ...         return validator_from_parser(parser)(v)
    >>>
    >>> class Order(BaseModel):
    ...     items: list[LineItem]
    >>>
    >>> # Validation errors include list index (e.g., 'items[1].quantity')
    >>> order = Order(items=[{'quantity': '5'}, {'quantity': '10'}])

Example - Dict Value Validation:
    >>> class Config(BaseModel):
    ...     ports: dict[str, int]
    ...
    ...     @field_validator('ports', mode='before')
    ...     @classmethod
    ...     def validate_ports(cls, v):
    ...         if not isinstance(v, dict):
    ...             raise ValueError('ports must be a dict')
    ...         return {k: validator_from_parser(parsers.parse_int)(val) for k, val in v.items()}
    >>>
    >>> config = Config(ports={'http': '80', 'https': '443'})

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

    Works seamlessly with:
    - Simple fields (str, int, custom types)
    - Nested models (User -> Address -> phone)
    - Lists of models (Order with list[LineItem])
    - Dicts with validated values (Config with dict[str, int])
    - Optional fields (field: Model | None)

    Pydantic automatically handles field path reporting for nested structures,
    so validation errors will include the full path (e.g., 'address.phone' or
    'items[1].quantity').

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

        >>> # Nested model validation
        >>> from pydantic import BaseModel, field_validator
        >>> from valid8r.core.parsers import EmailAddress
        >>>
        >>> class Contact(BaseModel):
        ...     email: EmailAddress
        ...
        ...     @field_validator('email', mode='before')
        ...     @classmethod
        ...     def validate_email(cls, v):
        ...         return validator_from_parser(parsers.parse_email)(v)
        >>>
        >>> contact = Contact(email='user@example.com')  # doctest: +SKIP

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
