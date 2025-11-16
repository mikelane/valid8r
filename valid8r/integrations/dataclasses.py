"""Dataclass integration for field-level validation.

This module provides decorators and functions for validating dataclass fields
using Valid8r validators and automatic type coercion from strings.

Example:
    >>> from dataclasses import dataclass, field
    >>> from valid8r.integrations.dataclasses import validate
    >>> from valid8r.core.validators import minimum, length
    >>>
    >>> @validate
    >>> @dataclass
    >>> class Product:
    ...     name: str = field(metadata={'validator': length(1, 100)})
    ...     price: float = field(metadata={'validator': minimum(0.0)})
    >>>
    >>> result = Product.from_dict({'name': 'Laptop', 'price': '999.99'})
    >>> match result:
    ...     case Success(product):
    ...         print(f"{product.name}: ${product.price}")
    ...     case Failure(error):
    ...         print(f"Validation failed: {error}")

"""

from __future__ import annotations

from dataclasses import (
    MISSING,
    fields,
    is_dataclass,
)
from typing import (
    Any,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.parsers import (
    parse_bool,
    parse_float,
    parse_int,
)

T = TypeVar('T')


def validate(cls: type[T]) -> type[T]:
    """Decorate a dataclass to add validation through from_dict class method.

    This decorator adds a `from_dict` class method to the dataclass that validates
    field values using validators specified in field metadata. The method automatically:

    - Coerces string values to target types (int, float, bool)
    - Validates nested dataclasses recursively
    - Applies validators from field metadata
    - Aggregates all field errors before returning
    - Returns Maybe[T] for clean error handling

    Args:
        cls: A dataclass to enhance with validation. Must be decorated with @dataclass.

    Returns:
        The same dataclass with added from_dict classmethod that returns Maybe[T]

    Raises:
        TypeError: If cls is not a dataclass

    Example:
        Basic validation with type coercion::

            >>> from dataclasses import dataclass, field
            >>> from valid8r.integrations.dataclasses import validate
            >>> from valid8r.core.validators import minimum, length
            >>>
            >>> @validate
            >>> @dataclass
            >>> class Person:
            ...     name: str = field(metadata={'validator': length(2, 100)})
            ...     age: int = field(metadata={'validator': minimum(0)})
            >>>
            >>> result = Person.from_dict({'name': 'Alice', 'age': '30'})
            >>> match result:
            ...     case Success(person):
            ...         print(f"{person.name} is {person.age}")
            ...     case Failure(error):
            ...         print(f"Validation failed: {error}")

        Nested dataclasses::

            >>> @dataclass
            >>> class Address:
            ...     city: str
            ...     zip_code: str = field(metadata={'validator': length(5, 5)})
            >>>
            >>> @validate
            >>> @dataclass
            >>> class Person:
            ...     name: str
            ...     address: Address
            >>>
            >>> Person.from_dict({
            ...     'name': 'Bob',
            ...     'address': {'city': 'Portland', 'zip_code': '97201'}
            ... })

    Note:
        The @validate decorator must be placed BEFORE @dataclass:

        .. code-block:: python

            @validate  # First
            @dataclass  # Second
            class MyClass:
                ...

    """
    if not is_dataclass(cls):
        msg = f'{cls.__name__} must be a dataclass'
        raise TypeError(msg)

    def from_dict(class_ref: type[T], data: dict[str, Any]) -> Maybe[T]:
        """Validate and construct dataclass instance from dictionary.

        Args:
            class_ref: The class (automatically passed by classmethod)
            data: Dictionary of field names to values

        Returns:
            Success with dataclass instance or Failure with error message

        """
        return validate_dataclass(class_ref, data)

    # Add the from_dict method to the class
    cls.from_dict = classmethod(from_dict)  # type: ignore[attr-defined]

    return cls


def validate_dataclass(cls: type[T], data: dict[str, Any]) -> Maybe[T]:  # noqa: C901, PLR0912, PLR0915
    """Validate and construct a dataclass instance from a dictionary.

    This function validates field values and constructs a dataclass instance. It performs:

    1. **Type Coercion**: Automatically parses strings to int, float, bool
    2. **Nested Validation**: Recursively validates nested dataclass fields
    3. **Field Validation**: Applies validators from field metadata
    4. **Error Aggregation**: Collects all field errors before returning
    5. **Type Safety**: Respects Optional types and default values

    Args:
        cls: The dataclass type to construct. Must be decorated with @dataclass.
        data: Dictionary mapping field names to values. String values are auto-coerced
            to match field types.

    Returns:
        Success containing the validated dataclass instance, or Failure with aggregated
        error messages in format "field1: error1; field2: error2".

    Example:
        Direct validation without decorator::

            >>> from dataclasses import dataclass, field
            >>> from valid8r.integrations.dataclasses import validate_dataclass
            >>> from valid8r.core.validators import minimum, length
            >>>
            >>> @dataclass
            >>> class Product:
            ...     name: str = field(metadata={'validator': length(1, 100)})
            ...     price: float = field(metadata={'validator': minimum(0.0)})
            >>>
            >>> result = validate_dataclass(Product, {
            ...     'name': 'Widget',
            ...     'price': '19.99'  # String auto-coerced to float
            ... })

        Error aggregation::

            >>> result = validate_dataclass(Product, {
            ...     'name': '',        # Too short
            ...     'price': '-10.0'   # Negative
            ... })
            >>> # Failure('name: must have length between 1 and 100; price: must be >= 0.0')

        Nested dataclasses::

            >>> @dataclass
            >>> class Address:
            ...     zip_code: str = field(metadata={'validator': length(5, 5)})
            >>>
            >>> @dataclass
            >>> class Person:
            ...     name: str
            ...     address: Address
            >>>
            >>> validate_dataclass(Person, {
            ...     'name': 'Alice',
            ...     'address': {'zip_code': '97201'}
            ... })

    Note:
        String-to-type coercion currently supports:
        - int: Decimal, hex (0x), octal (0o), binary (0b)
        - float: Scientific notation, infinity, NaN
        - bool: "true", "false", "yes", "no", "1", "0" (case-insensitive)

        After PR #196 merges, all types supported by from_type() will work automatically.

    """
    if not is_dataclass(cls):
        msg = f'{cls.__name__} must be a dataclass'
        return Maybe.failure(msg)

    # Resolve string annotations to actual types
    try:
        type_hints = get_type_hints(cls)
    except Exception:  # noqa: BLE001
        # If type hints resolution fails, try to resolve manually from __annotations__
        # This handles cases where types are defined locally (e.g., in test functions)
        type_hints = {}
        if hasattr(cls, '__annotations__'):
            import sys  # noqa: PLC0415

            module_ns = sys.modules[cls.__module__].__dict__ if hasattr(cls, '__module__') else {}
            for name, annotation in cls.__annotations__.items():
                if isinstance(annotation, str):
                    # Try to evaluate the string annotation
                    try:
                        type_hints[name] = eval(annotation, module_ns)  # noqa: S307
                    except Exception:  # noqa: BLE001, S112
                        # Keep as string if evaluation fails
                        continue
                else:
                    type_hints[name] = annotation

    # Collect errors and validated values
    errors: dict[str, str] = {}
    validated_values: dict[str, Any] = {}

    # Process each field
    for field_info in fields(cls):
        field_name = field_info.name
        # Use resolved type hint if available, otherwise use field type
        field_type = type_hints.get(field_name, field_info.type)
        has_default = field_info.default is not MISSING or field_info.default_factory is not MISSING

        # Get the raw value from data
        if field_name not in data:
            if has_default:
                # Use default value (will be handled by dataclass constructor)
                continue
            errors[field_name] = 'field is required'
            continue

        raw_value = data[field_name]

        # Handle None for Optional fields
        if raw_value is None:
            # Check if field is Optional (Union with None)
            # Handle string annotations from __future__ import annotations
            if isinstance(field_type, str):
                is_optional = field_type.startswith('Optional[') or 'None' in field_type
            else:
                args = get_args(field_type)
                is_optional = bool(args and type(None) in args)

            if is_optional:
                validated_values[field_name] = None
                continue
            errors[field_name] = 'cannot be None'
            continue

        # Type coercion: parse strings to target types
        parsed_result = _parse_value(raw_value, field_type)

        match parsed_result:
            case Success(parsed_value):
                # Apply field validator if present
                validator = field_info.metadata.get('validator') if field_info.metadata else None

                if validator is not None:
                    validation_result = validator(parsed_value)

                    match validation_result:
                        case Success(validated_value):
                            validated_values[field_name] = validated_value
                        case Failure(error):
                            errors[field_name] = error
                else:
                    # No validator, use parsed value
                    validated_values[field_name] = parsed_value

            case Failure(error):
                errors[field_name] = error

    # If any errors, return aggregated failure
    if errors:
        error_messages = [f'{field}: {error}' for field, error in errors.items()]
        return Maybe.failure('; '.join(error_messages))

    # All validations passed, construct the dataclass
    try:
        instance = cls(**validated_values)
        return Maybe.success(instance)
    except (TypeError, ValueError) as e:
        return Maybe.failure(f'Failed to construct {cls.__name__}: {e!s}')


def _parse_value(value: Any, target_type: type[Any]) -> Maybe[Any]:  # noqa: C901, PLR0912, ANN401
    """Parse a value to match the target type.

    Args:
        value: The value to parse (often a string)
        target_type: The target Python type

    Returns:
        Success with parsed value or Failure with error message

    """
    # Handle string type annotations (PEP 563 - from __future__ import annotations)
    if isinstance(target_type, str):
        # Resolve string annotation to actual type for primitives
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
        }

        if target_type in type_map:
            target_type = type_map[target_type]
        else:
            # Unknown string annotation - likely a forward reference or local class
            # For non-string values (like dicts), return as-is (might be nested dataclass)
            # For string values, we can't parse without knowing the actual type
            if not isinstance(value, str):
                return Maybe.success(value)
            # For strings, we don't know how to parse, return as-is
            return Maybe.success(value)

    # If value already matches target type, return it
    try:
        if isinstance(value, target_type):
            return Maybe.success(value)
    except TypeError:
        # target_type might not be a valid type for isinstance
        pass

    # Only parse strings to other types (unless it's a nested dataclass)
    if not isinstance(value, str):
        # Handle nested dataclasses
        if is_dataclass(target_type) and isinstance(value, dict):
            return validate_dataclass(target_type, value)
        # Return value as-is for non-string types
        return Maybe.success(value)

    # String-to-type coercion based on target type
    origin = get_origin(target_type)
    args = get_args(target_type)

    # Handle Optional[T] types
    if origin is type(None) or (args and type(None) in args):
        # Extract the non-None type
        actual_type = next((arg for arg in args if arg is not type(None)), target_type)
        return _parse_value(value, actual_type)

    # Parse strings using built-in parsers
    if target_type is int:
        return parse_int(value)
    if target_type is float:
        return parse_float(value)
    if target_type is bool:
        return parse_bool(value)
    if target_type is str:
        return Maybe.success(value)
    # For other types, return value as-is
    return Maybe.success(value)


__all__ = ['validate', 'validate_dataclass']
