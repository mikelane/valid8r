"""Type-based parser generation.

This module provides utilities for generating parsers from Python type annotations.
Uses match/case pattern matching for type introspection and dispatch.
"""

from __future__ import annotations

import builtins
import json
import types
import typing
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from collections.abc import Callable

from valid8r.core import parsers
from valid8r.core.maybe import Maybe

T = TypeVar('T')

# DoS protection: Maximum input length for JSON parsing (100KB)
# Prevents processing of arbitrarily large inputs that could cause resource exhaustion
MAX_JSON_LENGTH = 100_000  # 100,000 characters (~100KB)


def from_type(annotation: type[T] | Any) -> Callable[[str], Maybe[T]]:  # noqa: ANN401
    """Generate a parser from a Python type annotation.

    This function uses match/case pattern matching to introspect type annotations
    and automatically generate appropriate parser functions. Supports basic types,
    generics, unions, literals, enums, and nested structures.

    Args:
        annotation: A Python type annotation (int, str, Optional[int], list[str], etc.)

    Returns:
        A parser function that takes a string and returns Maybe[T]

    Raises:
        ValueError: If annotation is None or unsupported type
        TypeError: If annotation is not a valid type

    Supported Types:
        - **Basic types**: int, str, float, bool
        - **Optional types**: Optional[T] treats empty string as None
        - **Collections**: list[T], dict[K,V], set[T] (with element validation)
        - **Union types**: Union[int, str] tries alternatives in order
        - **Literal types**: Literal['red', 'green', 'blue'] restricts to specific values
        - **Enum types**: Python Enum classes with case-insensitive matching
        - **Annotated types**: Annotated[int, validators.minimum(0)] chains validators
        - **Nested types**: list[dict[str, int]], dict[str, list[int]], etc.

    Examples:
        Basic type parsing:

        >>> from valid8r.core.type_adapters import from_type
        >>> parser = from_type(int)
        >>> result = parser('42')
        >>> result.value_or(None)
        42

        Optional type handling:

        >>> from typing import Optional, Union
        >>> parser = from_type(Optional[int])
        >>> parser('').value_or('not none')  # Empty string becomes None
        >>> parser('42').value_or(None)
        42

        Collection parsing with validation:

        >>> parser = from_type(list[int])
        >>> result = parser('[1, 2, 3]')
        >>> result.value_or([])
        [1, 2, 3]
        >>> parser('[1, "invalid", 3]').is_failure()
        True

        Dictionary with typed keys and values:

        >>> parser = from_type(dict[str, int])
        >>> result = parser('{"age": 30, "count": 5}')
        >>> result.value_or({})
        {'age': 30, 'count': 5}

        Union types try alternatives:

        >>> parser = from_type(Union[int, float, str])
        >>> parser('42').value_or(None)  # Parses as int
        42
        >>> parser('3.14').value_or(None)  # Parses as float
        3.14
        >>> parser('hello').value_or(None)  # Parses as str
        'hello'

        Literal types restrict values:

        >>> from typing import Literal
        >>> parser = from_type(Literal['red', 'green', 'blue'])
        >>> parser('red').value_or(None)
        'red'
        >>> parser('yellow').is_failure()
        True

        Enum types with case-insensitive matching:

        >>> from enum import Enum
        >>> class Status(Enum):
        ...     ACTIVE = 'active'
        ...     INACTIVE = 'inactive'
        >>> parser = from_type(Status)
        >>> parser('ACTIVE').value_or(None)
        <Status.ACTIVE: 'active'>
        >>> parser('active').value_or(None)  # Case-insensitive
        <Status.ACTIVE: 'active'>

        Annotated types with validators:

        >>> from typing import Annotated
        >>> from valid8r import validators
        >>> parser = from_type(Annotated[int, validators.minimum(0), validators.maximum(100)])
        >>> parser('50').value_or(None)
        50
        >>> parser('150').is_failure()  # Exceeds maximum
        True
        >>> parser('-5').is_failure()  # Below minimum
        True

        Nested structures:

        >>> parser = from_type(dict[str, list[int]])
        >>> result = parser('{"scores": [95, 87, 92]}')
        >>> result.value_or({})
        {'scores': [95, 87, 92]}

    Notes:
        - Collection parsers expect JSON format: '[1, 2, 3]' for lists, '{"key": "value"}' for dicts
        - Nested structures are fully validated at each level
        - Union types return the first successful parse (order matters)
        - Enum matching is case-insensitive by default
        - Annotated validators are chained using bind() for composition

    """
    # Validate annotation
    if annotation is None:
        msg = 'Type annotation required - cannot be None'
        raise ValueError(msg)

    # Get the origin and args for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Use match/case for type dispatch (CRITICAL REQUIREMENT)
    match origin:
        case None:
            # Simple types without generic parameters
            return _handle_simple_type(annotation)

        case types.UnionType:
            # X | Y (PEP 604 syntax) - Python 3.10+
            return _handle_union_type(args)

        case typing.Union:
            # Union[X, Y] (typing.Union syntax)
            return _handle_union_type(args)

        case builtins.list:
            # list[T]  # noqa: ERA001
            return _handle_list_type(args)  # type: ignore[return-value]

        case builtins.dict:
            # dict[K, V]  # noqa: ERA001
            return _handle_dict_type(args)  # type: ignore[return-value]

        case builtins.set:
            # set[T]  # noqa: ERA001
            return _handle_set_type(args)  # type: ignore[return-value]

        case typing.Literal:
            # Literal[value1, value2, ...]  # noqa: ERA001
            return _handle_literal_type(args)

        case typing.Annotated:
            # Annotated[T, metadata...]
            return _handle_annotated_type(args)

        case _:
            # Unsupported type
            msg = f'Unsupported type: {annotation}'
            raise ValueError(msg)


def _is_enum_type(annotation: type) -> bool:
    """Check if annotation is an Enum type."""
    return isinstance(annotation, type) and issubclass(annotation, Enum)


def _handle_simple_type(annotation: type[T]) -> Callable[[str], Maybe[T]]:
    """Handle simple, non-generic types.

    Uses match/case to dispatch to appropriate parser.
    """
    # Handle builtin types
    if annotation is builtins.int:
        return parsers.parse_int  # type: ignore[return-value]
    if annotation is builtins.str:
        return lambda text: Maybe.success(text)  # type: ignore[arg-type]
    if annotation is builtins.float:
        return parsers.parse_float  # type: ignore[return-value]
    if annotation is builtins.bool:
        return parsers.parse_bool  # type: ignore[return-value]
    if annotation is builtins.list:
        return _create_bare_list_parser()  # type: ignore[return-value]
    if annotation is builtins.dict:
        return _create_bare_dict_parser()  # type: ignore[return-value]
    if annotation is builtins.set:
        return _create_bare_set_parser()  # type: ignore[return-value]

    # Handle Enum types
    if _is_enum_type(annotation):
        return lambda text: parsers.parse_enum(text, annotation)  # type: ignore[type-var,return-value]

    # Handle unsupported/invalid types
    if annotation in (typing.Callable, types.FunctionType) or isinstance(annotation, type):
        msg = f'Unsupported type: {annotation}'
        raise TypeError(msg)

    msg = f'Invalid type annotation: {annotation}'
    raise TypeError(msg)


def _handle_union_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[Any]]:
    """Handle Union types by trying each alternative in order.

    For Optional[T] (which is Union[T, None]), treat empty string as None.
    """
    optional_union_size = 2  # Optional[T] is Union[T, None] with 2 types
    # Check if this is Optional[T] (Union[T, None])
    if len(args) == optional_union_size and type(None) in args:
        # This is Optional[T]  # noqa: ERA001
        inner_type = args[0] if args[1] is type(None) else args[1]
        inner_parser = from_type(inner_type)

        def optional_parser(text: str) -> Maybe[Any]:
            if text == '' or text.lower() == 'none':
                return Maybe.success(None)
            return inner_parser(text)

        return optional_parser

    # Regular Union - try each type in order
    parsers_list = [from_type(arg) for arg in args]

    def union_parser(text: str) -> Maybe[Any]:
        for parser in parsers_list:
            result = parser(text)
            if result.is_success():
                return result
        # All failed - return last failure
        return result

    return union_parser


def _create_bare_list_parser() -> Callable[[str], Maybe[list[Any]]]:
    """Create parser for untyped list (bare list without type parameter)."""

    def bare_list_parser(text: str) -> Maybe[list[Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        result = parsers.parse_json(text)
        if result.is_failure():
            return result  # type: ignore[return-value]
        value = result.value_or(None)
        if not isinstance(value, list):
            return Maybe.failure('Expected a JSON array')
        return Maybe.success(value)

    return bare_list_parser


def _create_typed_list_parser(element_type: type) -> Callable[[str], Maybe[list[Any]]]:
    """Create parser for typed list (list[T] with element type)."""
    element_parser: Callable[[str], Maybe[Any]] = from_type(element_type)

    def typed_list_parser(text: str) -> Maybe[list[Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        # Parse as JSON first
        json_result = parsers.parse_json(text)
        if json_result.is_failure():
            return json_result  # type: ignore[return-value]

        value = json_result.value_or(None)
        if not isinstance(value, list):
            return Maybe.failure('Expected a JSON array')

        # Validate and parse each element
        parsed_elements: list[Any] = []
        for i, elem in enumerate(value, start=1):
            elem_result = element_parser(_to_string(elem))
            if elem_result.is_failure():
                return Maybe.failure(f'Failed to parse element {i}: {elem_result.error_or("")}')
            parsed_elements.append(elem_result.value_or(None))

        return Maybe.success(parsed_elements)

    return typed_list_parser


def _handle_list_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[list[Any]]]:
    """Handle list[T] types.

    Parses JSON array format and validates each element.
    """
    if not args:
        return _create_bare_list_parser()
    return _create_typed_list_parser(args[0])


def _create_bare_dict_parser() -> Callable[[str], Maybe[dict[Any, Any]]]:
    """Create parser for untyped dict (bare dict without type parameters)."""

    def bare_dict_parser(text: str) -> Maybe[dict[Any, Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        result = parsers.parse_json(text)
        if result.is_failure():
            return result  # type: ignore[return-value]
        value = result.value_or(None)
        if not isinstance(value, dict):
            return Maybe.failure('Expected a JSON object')
        return Maybe.success(value)

    return bare_dict_parser


def _to_string(value: Any) -> str:  # noqa: ANN401
    """Convert a value to string, handling nested structures."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    if isinstance(value, str):
        return value
    return str(value)


def _create_typed_dict_parser(key_type: type, value_type: type) -> Callable[[str], Maybe[dict[Any, Any]]]:
    """Create parser for typed dict (dict[K, V] with key and value types)."""
    key_parser: Callable[[str], Maybe[Any]] = from_type(key_type)
    value_parser: Callable[[str], Maybe[Any]] = from_type(value_type)

    def typed_dict_parser(text: str) -> Maybe[dict[Any, Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        # Parse as JSON first
        json_result = parsers.parse_json(text)
        if json_result.is_failure():
            return json_result  # type: ignore[return-value]

        value = json_result.value_or(None)
        if not isinstance(value, dict):
            return Maybe.failure('Expected a JSON object')

        # Validate and parse each key-value pair
        parsed_dict: dict[Any, Any] = {}
        for key, val in value.items():
            # Parse key
            key_result = key_parser(_to_string(key))
            if key_result.is_failure():
                return Maybe.failure(f'Failed to parse key "{key}": {key_result.error_or("")}')

            # Parse value
            val_result = value_parser(_to_string(val))
            if val_result.is_failure():
                return Maybe.failure(f'Failed to parse value for key "{key}": {val_result.error_or("")}')

            parsed_dict[key_result.value_or(None)] = val_result.value_or(None)

        return Maybe.success(parsed_dict)

    return typed_dict_parser


def _handle_dict_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[dict[Any, Any]]]:
    """Handle dict[K, V] types.

    Parses JSON object format and validates keys and values.
    """
    if len(args) != 2:  # noqa: PLR2004
        return _create_bare_dict_parser()
    key_type, value_type = args
    return _create_typed_dict_parser(key_type, value_type)


def _create_bare_set_parser() -> Callable[[str], Maybe[set[Any]]]:
    """Create parser for untyped set (bare set without type parameter)."""

    def bare_set_parser(text: str) -> Maybe[set[Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        result = parsers.parse_json(text)
        if result.is_failure():
            return result  # type: ignore[return-value]
        value = result.value_or(None)
        if not isinstance(value, list):
            return Maybe.failure('Expected a JSON array for set')
        return Maybe.success(set(value))

    return bare_set_parser


def _create_typed_set_parser(element_type: type) -> Callable[[str], Maybe[set[Any]]]:
    """Create parser for typed set (set[T] with element type)."""
    element_parser: Callable[[str], Maybe[Any]] = from_type(element_type)

    def typed_set_parser(text: str) -> Maybe[set[Any]]:
        # DoS protection: Early length guard BEFORE JSON parsing
        if len(text) > MAX_JSON_LENGTH:
            return Maybe.failure(f'Input too large: maximum {MAX_JSON_LENGTH} characters')

        # Parse as JSON array first
        json_result = parsers.parse_json(text)
        if json_result.is_failure():
            return json_result  # type: ignore[return-value]

        value = json_result.value_or(None)
        if not isinstance(value, list):
            return Maybe.failure('Expected a JSON array for set')

        # Validate and parse each element
        parsed_elements: set[Any] = set()
        for i, elem in enumerate(value, start=1):
            elem_result = element_parser(_to_string(elem))
            if elem_result.is_failure():
                return Maybe.failure(f'Failed to parse element {i}: {elem_result.error_or("")}')
            parsed_elements.add(elem_result.value_or(None))

        return Maybe.success(parsed_elements)

    return typed_set_parser


def _handle_set_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[set[Any]]]:
    """Handle set[T] types.

    Parses JSON array format and converts to set after validating elements.
    """
    if not args:
        return _create_bare_set_parser()
    return _create_typed_set_parser(args[0])


def _handle_literal_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[Any]]:
    """Handle Literal[value1, value2, ...] types."""

    def literal_parser(text: str) -> Maybe[Any]:
        # Try to match against each literal value
        for literal_value in args:
            # Convert literal value to string for comparison
            if str(literal_value) == text:
                return Maybe.success(literal_value)
            # For string literals, try case-sensitive match
            if isinstance(literal_value, str) and literal_value == text:
                return Maybe.success(literal_value)
            # For int/bool literals, try parsing
            if isinstance(literal_value, int) and not isinstance(literal_value, bool):
                try:
                    if int(text) == literal_value:
                        return Maybe.success(literal_value)
                except ValueError:
                    pass
            # For bool literals
            if isinstance(literal_value, bool):
                parsed = parsers.parse_bool(text)
                default_bool = False
                if parsed.is_success() and parsed.value_or(default_bool) == literal_value:
                    return Maybe.success(literal_value)

        # No match found
        valid_values = ', '.join(repr(v) for v in args)
        return Maybe.failure(f'Value must be one of: {valid_values}')

    return literal_parser


def _handle_annotated_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[Any]]:
    """Handle Annotated[T, metadata...] types.

    Extracts the base type and applies validators from metadata.
    """
    if not args:
        msg = 'Annotated type requires at least a base type'
        raise ValueError(msg)

    base_type = args[0]
    metadata = args[1:]

    # Get base parser
    base_parser = from_type(base_type)

    # Extract validator functions from metadata
    validators = [m for m in metadata if callable(m)]

    if not validators:
        # No validators, just return base parser
        return base_parser

    # Chain validators
    def annotated_parser(text: str) -> Maybe[Any]:
        result = base_parser(text)
        for validator in validators:
            result = result.bind(validator)
        return result

    return annotated_parser


__all__ = ['from_type']
