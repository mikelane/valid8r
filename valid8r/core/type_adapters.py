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

        case types.UnionType():
            # Union[X, Y] or X | Y  # noqa: ERA001
            return _handle_union_type(args)

        case typing.Union:
            # Union[X, Y]  # noqa: ERA001
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


def _handle_simple_type(annotation: type[T]) -> Callable[[str], Maybe[T]]:
    """Handle simple, non-generic types.

    Uses match/case to dispatch to appropriate parser for basic Python types
    and Enum classes. This function is called when the type annotation has
    no generic parameters (e.g., int, str, float, bool, or custom Enum).

    Args:
        annotation: A simple Python type without generic parameters

    Returns:
        Parser function appropriate for the given type

    Raises:
        TypeError: If annotation is a callable, forward reference, or unsupported type

    Security:
        All returned parsers inherit DoS protection from underlying parsers.parse_*
        functions which validate input length before expensive operations.

    Examples:
        int type returns parse_int parser
        str type returns identity parser (all strings are valid)
        bool type returns parse_bool parser
        Enum subclass returns case-insensitive enum parser

    """
    match annotation:
        case builtins.int:
            return parsers.parse_int  # type: ignore[return-value]
        case builtins.str:
            # Strings are always valid - just return Success
            return lambda text: Maybe.success(text)  # type: ignore[arg-type]
        case builtins.float:
            return parsers.parse_float  # type: ignore[return-value]
        case builtins.bool:
            return parsers.parse_bool  # type: ignore[return-value]
        case _ if isinstance(annotation, type) and issubclass(annotation, Enum) and annotation is not bool:
            # Handle Enum types - parse_enum signature is (value, enum_class, error_message)
            # Note: Must explicitly check `annotation is not bool` to avoid matching bool type
            enum_name = annotation.__name__  # type: ignore[union-attr]
            error_msg = f'Input must be a valid {enum_name}'
            return lambda text: parsers.parse_enum(text, annotation, error_msg)  # type: ignore[return-value,type-var]
        case typing.Callable | types.FunctionType:
            msg = f'Unsupported type: {annotation}'
            raise TypeError(msg)  # Use TypeError for type errors
        case _:
            # Check if it's a string (forward reference)
            if isinstance(annotation, str):
                msg = f'Cannot resolve forward reference: {annotation}'
                raise TypeError(msg)  # Use TypeError for type errors
            # Check if it's a valid type but we don't support it
            if isinstance(annotation, type):
                msg = f'Unsupported type: {annotation}'
                raise TypeError(msg)  # Use TypeError for type errors
            msg = f'Invalid type annotation: {annotation}'
            raise TypeError(msg)


def _handle_union_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[Any]]:
    """Handle Union types by trying each alternative in order.

    This function handles both Optional[T] (Union[T, None]) and general Union types.
    For Optional types, empty strings and "none" (case-insensitive) are converted
    to None. For general unions, each type is tried in order until one succeeds.

    Args:
        args: Tuple of type arguments from Union[...] or Optional[...]

    Returns:
        Parser function that tries alternatives until one succeeds

    Behavior:
        - Optional[T]: Empty string or "none" returns None, otherwise parses as T
        - Union[X, Y, Z]: Tries X, then Y, then Z; returns first success
        - If all alternatives fail, returns the last failure message

    Examples:
        Optional[int]: "" -> Success(None), "42" -> Success(42)
        Union[int, str]: "42" -> Success(42), "hello" -> Success("hello")

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


def _handle_list_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[list[Any]]]:  # noqa: C901
    """Handle list[T] types with element validation.

    Parses JSON array format and validates each element against the specified type.
    For bare list (no type parameter), returns unvalidated JSON array.

    Args:
        args: Tuple containing element type, or empty for bare list

    Returns:
        Parser function that parses JSON arrays and validates elements

    Security:
        Inherits DoS protection from parse_json (10,000 character limit).
        Prevents malicious payloads from causing excessive parsing time.

    Error Messages:
        - "Expected a JSON array" if input is not a JSON array
        - "Failed to parse element N: ..." for element validation failures

    Examples:
        list[int]: '[1, 2, 3]' -> Success([1, 2, 3])
        list[int]: '[1, "x", 3]' -> Failure("Failed to parse element 2: ...")
        bare list: '[1, "x", 3]' -> Success([1, "x", 3]) (no validation)

    """
    if not args:
        # Bare list without element type - parse JSON and return as-is
        def bare_list_parser(text: str) -> Maybe[list[Any]]:
            result = parsers.parse_json(text)
            if result.is_failure():
                return result  # type: ignore[return-value]
            value = result.value_or(None)
            if not isinstance(value, list):
                return Maybe.failure('Expected a JSON array')
            return Maybe.success(value)

        return bare_list_parser

    element_type = args[0]
    element_parser = from_type(element_type)

    def typed_list_parser(text: str) -> Maybe[list[Any]]:
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
            # For primitive types, convert to string for parsing
            # For nested structures (dict, list), use JSON serialization
            if isinstance(elem, (dict, list)):
                elem_str = json.dumps(elem)
            elif isinstance(elem, str):
                elem_str = elem
            else:
                elem_str = str(elem)

            elem_result = element_parser(elem_str)
            if elem_result.is_failure():
                return Maybe.failure(f'Failed to parse element {i}: {elem_result.error_or("")}')
            parsed_elements.append(elem_result.value_or(None))

        return Maybe.success(parsed_elements)

    return typed_list_parser


def _handle_dict_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[dict[Any, Any]]]:  # noqa: C901
    """Handle dict[K, V] types with key and value validation.

    Parses JSON object format and validates both keys and values against their
    specified types. For bare dict (no type parameters), returns unvalidated JSON object.

    Args:
        args: Tuple containing (key_type, value_type), or empty for bare dict

    Returns:
        Parser function that parses JSON objects and validates keys/values

    Security:
        Inherits DoS protection from parse_json (10,000 character limit).
        Validates each key and value to prevent injection attacks.

    Error Messages:
        - "Expected a JSON object" if input is not a JSON object
        - 'Failed to parse key "K": ...' for key parsing failures
        - 'Failed to parse value for key "K": ...' for value parsing failures

    Examples:
        dict[str, int]: '{"age": 30}' -> Success({"age": 30})
        dict[str, int]: '{"age": "x"}' -> Failure('Failed to parse value for key "age": ...')
        bare dict: '{"any": "value"}' -> Success({"any": "value"}) (no validation)

    """
    if len(args) != 2:  # noqa: PLR2004
        # Bare dict without type params - parse JSON and return as-is
        def bare_dict_parser(text: str) -> Maybe[dict[Any, Any]]:
            result = parsers.parse_json(text)
            if result.is_failure():
                return result  # type: ignore[return-value]
            value = result.value_or(None)
            if not isinstance(value, dict):
                return Maybe.failure('Expected a JSON object')
            return Maybe.success(value)

        return bare_dict_parser

    key_type, value_type = args
    key_parser = from_type(key_type)
    value_parser = from_type(value_type)

    def typed_dict_parser(text: str) -> Maybe[dict[Any, Any]]:
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
            # Parse key - convert nested structures to JSON
            if isinstance(key, (dict, list)):
                key_str = json.dumps(key)
            elif isinstance(key, str):
                key_str = key
            else:
                key_str = str(key)

            key_result = key_parser(key_str)
            if key_result.is_failure():
                return Maybe.failure(f'Failed to parse key "{key}": {key_result.error_or("")}')

            # Parse value - convert nested structures to JSON
            if isinstance(val, (dict, list)):
                val_str = json.dumps(val)
            elif isinstance(val, str):
                val_str = val
            else:
                val_str = str(val)

            val_result = value_parser(val_str)
            if val_result.is_failure():
                return Maybe.failure(f'Failed to parse value for key "{key}": {val_result.error_or("")}')

            parsed_dict[key_result.value_or(None)] = val_result.value_or(None)

        return Maybe.success(parsed_dict)

    return typed_dict_parser


def _handle_set_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[set[Any]]]:  # noqa: C901
    """Handle set[T] types with element validation.

    Parses JSON array format, validates each element, and returns a set (duplicates removed).
    For bare set (no type parameter), returns unvalidated set from JSON array.

    Args:
        args: Tuple containing element type, or empty for bare set

    Returns:
        Parser function that parses JSON arrays and returns validated sets

    Security:
        Inherits DoS protection from parse_json (10,000 character limit).
        Automatically deduplicates elements to prevent memory exhaustion.

    Error Messages:
        - "Expected a JSON array for set" if input is not a JSON array
        - "Failed to parse element N: ..." for element validation failures

    Examples:
        set[int]: '[1, 2, 2, 3]' -> Success({1, 2, 3})
        set[str]: '["a", "b"]' -> Success({"a", "b"})
        bare set: '[1, "x", 1]' -> Success({1, "x"}) (no validation)

    """
    if not args:
        # Bare set without element type - parse JSON array and convert to set
        def bare_set_parser(text: str) -> Maybe[set[Any]]:
            result = parsers.parse_json(text)
            if result.is_failure():
                return result  # type: ignore[return-value]
            value = result.value_or(None)
            if not isinstance(value, list):
                return Maybe.failure('Expected a JSON array for set')
            return Maybe.success(set(value))

        return bare_set_parser

    element_type = args[0]
    element_parser = from_type(element_type)

    def typed_set_parser(text: str) -> Maybe[set[Any]]:
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
            # Convert nested structures to JSON
            if isinstance(elem, (dict, list)):
                elem_str = json.dumps(elem)
            elif isinstance(elem, str):
                elem_str = elem
            else:
                elem_str = str(elem)

            elem_result = element_parser(elem_str)
            if elem_result.is_failure():
                return Maybe.failure(f'Failed to parse element {i}: {elem_result.error_or("")}')
            parsed_elements.add(elem_result.value_or(None))

        return Maybe.success(parsed_elements)

    return typed_set_parser


def _handle_literal_type(args: tuple[Any, ...]) -> Callable[[str], Maybe[Any]]:
    """Handle Literal[value1, value2, ...] types with strict value matching.

    Validates input against a fixed set of literal values. Supports string, int,
    and bool literals with appropriate parsing for each type.

    Args:
        args: Tuple of allowed literal values

    Returns:
        Parser function that accepts only specified literal values

    Behavior:
        - String literals: Case-sensitive exact match
        - Integer literals: Parses input as int and compares
        - Boolean literals: Uses parse_bool and compares
        - Fails with clear message listing all valid values

    Examples:
        Literal['red', 'green', 'blue']: 'red' -> Success('red')
        Literal['red', 'green', 'blue']: 'yellow' -> Failure("Value must be one of: ...")
        Literal[0, 1]: '1' -> Success(1)

    """

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
    """Handle Annotated[T, metadata...] types with validator chaining.

    Extracts the base type and chains any callable validators from metadata.
    This enables inline validation constraints using Annotated type hints.

    Args:
        args: Tuple where first element is base type, remaining are metadata

    Returns:
        Parser function that applies base parser then chains all validators

    Raises:
        ValueError: If args is empty (no base type provided)

    Behavior:
        - Filters metadata to find callable validators
        - If no validators, returns base parser unchanged
        - If validators exist, chains them using bind()
        - Validators applied in order they appear in metadata

    Examples:
        Annotated[int, validators.minimum(0)]: '5' -> Success(5), '-1' -> Failure
        Annotated[int, validators.minimum(0), validators.maximum(100)]: Chains both
        Annotated[str, "doc string"]: Ignores non-callable metadata

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
