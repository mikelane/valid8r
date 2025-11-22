"""Examples of using from_type() for automatic parser generation.

This module demonstrates how to use Valid8r's type-based parser generation
to create parsers automatically from Python type annotations.
"""

from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
)

if TYPE_CHECKING:
    from collections.abc import Callable

from valid8r import validators
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.type_adapters import from_type

# =============================================================================
# Basic Type Parsing
# =============================================================================


def example_basic_types() -> None:
    """Demonstrate parsing basic Python types."""
    print('=== Basic Type Parsing ===\n')

    # Integer parsing
    int_parser: Callable[[str], Maybe[int]] = from_type(int)
    result = int_parser('42')
    match result:
        case Success(value):
            print(f'Parsed integer: {value} (type: {type(value).__name__})')
        case Failure(err):
            print(f'Error: {err}')

    # Float parsing
    float_parser: Callable[[str], Maybe[float]] = from_type(float)
    result = float_parser('3.14')  # type: ignore[assignment]
    match result:
        case Success(value):
            print(f'Parsed float: {value} (type: {type(value).__name__})')
        case Failure(err):
            print(f'Error: {err}')

    # Boolean parsing
    bool_parser: Callable[[str], Maybe[bool]] = from_type(bool)
    for test_input in ['true', 'false', '1', '0']:
        result = bool_parser(test_input)  # type: ignore[assignment]
        match result:
            case Success(value):
                print(f'Parsed boolean "{test_input}": {value}')
            case Failure(err):
                print(f'Error parsing "{test_input}": {err}')

    print()


# =============================================================================
# Optional Types
# =============================================================================


def example_optional_types() -> None:
    """Demonstrate parsing Optional types with None handling."""
    print('=== Optional Type Parsing ===\n')

    parser: Callable[[str], Maybe[int | None]] = from_type(int | None)

    # Valid integer
    result = parser('42')
    match result:
        case Success(value):
            print(f'Parsed optional int "42": {value}')

    # Empty string becomes None
    result = parser('')
    match result:
        case Success(value):
            print(f'Parsed empty string: {value} (None)')

    # "none" becomes None
    result = parser('none')
    match result:
        case Success(value):
            print(f'Parsed "none": {value} (None)')

    # Invalid input still fails
    result = parser('invalid')
    match result:
        case Failure(err):
            print(f'Invalid input rejected: {err}')

    print()


# =============================================================================
# Collection Types
# =============================================================================


def example_collections() -> None:
    """Demonstrate parsing collection types with element validation."""
    print('=== Collection Type Parsing ===\n')

    # List of integers
    list_parser: Callable[[str], Maybe[Any]] = from_type(list[int])
    result = list_parser('[1, 2, 3, 4, 5]')
    match result:
        case Success(value):
            print(f'Parsed list of ints: {value}')

    # List with invalid element
    result = list_parser('[1, "invalid", 3]')
    match result:
        case Failure(err):
            print(f'List with invalid element: {err}')

    # Dictionary with typed keys/values
    dict_parser: Callable[[str], Maybe[Any]] = from_type(dict[str, int])
    result = dict_parser('{"age": 30, "count": 5}')
    match result:
        case Success(value):
            print(f'Parsed dict: {value}')

    # Set (removes duplicates)
    set_parser: Callable[[str], Maybe[Any]] = from_type(set[str])
    result = set_parser('["a", "b", "c", "a"]')
    match result:
        case Success(value):
            print(f'Parsed set: {value} (duplicates removed)')

    # Nested structures
    nested_parser: Callable[[str], Maybe[Any]] = from_type(dict[str, list[int]])
    result = nested_parser('{"scores": [95, 87, 92]}')
    match result:
        case Success(value):
            print(f'Parsed nested structure: {value}')

    print()


# =============================================================================
# Union Types
# =============================================================================


def example_union_types() -> None:
    """Demonstrate parsing Union types that try alternatives."""
    print('=== Union Type Parsing ===\n')

    parser: Callable[[str], Maybe[Any]] = from_type(int | float | str)

    # Try different inputs
    test_inputs = ['42', '3.14', 'hello', 'true']

    for test_input in test_inputs:
        result = parser(test_input)
        match result:
            case Success(value):
                print(f'Parsed "{test_input}" as {type(value).__name__}: {value}')

    print()


# =============================================================================
# Literal Types
# =============================================================================


def example_literal_types() -> None:
    """Demonstrate parsing Literal types with restricted values."""
    print('=== Literal Type Parsing ===\n')

    # String literals
    color_parser: Callable[[str], Maybe[Any]] = from_type(Literal['red', 'green', 'blue'])

    for color in ['red', 'yellow', 'green']:
        result = color_parser(color)
        match result:
            case Success(value):
                print(f'Valid color: {value}')
            case Failure(err):
                print(f'Invalid color "{color}": {err}')

    # Mixed type literals
    mixed_parser: Callable[[str], Maybe[Any]] = from_type(Literal[1, 'one', True])
    for test_input in ['1', 'one', 'true', 'invalid']:
        result = mixed_parser(test_input)
        match result:
            case Success(value):
                print(f'Parsed literal "{test_input}": {value} (type: {type(value).__name__})')
            case Failure(err):
                print(f'Invalid literal "{test_input}": {err}')

    print()


# =============================================================================
# Enum Types
# =============================================================================


class Status(Enum):
    """Example enum for status values."""

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'


class Priority(Enum):
    """Example enum with integer values."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


def example_enum_types() -> None:
    """Demonstrate parsing Enum types with case-insensitive matching."""
    print('=== Enum Type Parsing ===\n')

    status_parser: Callable[[str], Maybe[Any]] = from_type(Status)

    # Case-insensitive matching
    for test_input in ['ACTIVE', 'active', 'AcTiVe', 'invalid']:
        result = status_parser(test_input)
        match result:
            case Success(value):
                print(f'Parsed status "{test_input}": {value} ({value.value})')
            case Failure(err):
                print(f'Invalid status "{test_input}": {err}')

    print()


# =============================================================================
# Annotated Types with Validators
# =============================================================================


def example_annotated_types() -> None:
    """Demonstrate combining type parsing with validation using Annotated."""
    print('=== Annotated Type Parsing ===\n')

    # Integer with range validation
    age_parser: Callable[[str], Maybe[Any]] = from_type(Annotated[int, validators.minimum(0), validators.maximum(120)])  # type: ignore[type-var]

    for test_input in ['25', '150', '-5', 'abc']:
        result = age_parser(test_input)
        match result:
            case Success(value):
                print(f'Valid age: {value}')
            case Failure(err):
                print(f'Invalid age "{test_input}": {err}')

    # String with length validation
    username_parser: Callable[[str], Maybe[Any]] = from_type(Annotated[str, validators.length(3, 20)])

    for test_input in ['alice', 'ab', 'this_username_is_way_too_long']:
        result = username_parser(test_input)
        match result:
            case Success(value):
                print(f'Valid username: {value}')
            case Failure(err):
                print(f'Invalid username "{test_input}": {err}')

    print()


# =============================================================================
# Complex Nested Types
# =============================================================================


def example_complex_types() -> None:
    """Demonstrate parsing complex nested type structures."""
    print('=== Complex Nested Type Parsing ===\n')

    # List of optional integers with validation
    parser: Callable[[str], Maybe[Any]] = from_type(list[Annotated[int, validators.minimum(0)] | None])

    test_input = '[1, null, 5, 10]'
    result = parser(test_input)
    match result:
        case Success(value):
            print(f'Parsed list with optionals: {value}')

    # Dict with validated values
    validated_dict_parser: Callable[[str], Maybe[Any]] = from_type(
        dict[str, Annotated[int, validators.minimum(0), validators.maximum(100)]]
    )

    test_input = '{"math": 95, "english": 87, "science": 92}'
    result = validated_dict_parser(test_input)
    match result:
        case Success(value):
            print(f'Parsed validated dict: {value}')

    # Nested lists
    nested_list_parser: Callable[[str], Maybe[Any]] = from_type(list[list[int]])

    test_input = '[[1, 2, 3], [4, 5, 6], [7, 8, 9]]'
    result = nested_list_parser(test_input)
    match result:
        case Success(value):
            print(f'Parsed nested lists: {value}')

    print()


# =============================================================================
# Real-World Example: Configuration Parser
# =============================================================================


class LogLevel(Enum):
    """Log level configuration."""

    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


def example_config_parser() -> None:
    """Demonstrate a real-world configuration parser."""
    print('=== Real-World Configuration Parser ===\n')

    # Define configuration schema using type annotations
    port_type = Annotated[int, validators.minimum(1), validators.maximum(65535)]
    timeout_type = Annotated[int, validators.minimum(0)]
    host_list_type = list[str]

    # Create parsers
    port_parser: Callable[[str], Maybe[Any]] = from_type(port_type)
    timeout_parser: Callable[[str], Maybe[Any]] = from_type(timeout_type)
    log_level_parser: Callable[[str], Maybe[Any]] = from_type(LogLevel)
    hosts_parser: Callable[[str], Maybe[Any]] = from_type(host_list_type)
    debug_parser: Callable[[str], Maybe[Any]] = from_type(bool)

    # Example configuration
    config_data = {
        'port': '8080',
        'timeout': '30',
        'log_level': 'INFO',
        'hosts': '["app1.example.com", "app2.example.com"]',
        'debug': 'false',
    }

    print('Parsing configuration:')
    config_result: dict[str, Maybe] = {}

    # Parse each field
    config_result['port'] = port_parser(config_data['port'])
    config_result['timeout'] = timeout_parser(config_data['timeout'])
    config_result['log_level'] = log_level_parser(config_data['log_level'])
    config_result['hosts'] = hosts_parser(config_data['hosts'])
    config_result['debug'] = debug_parser(config_data['debug'])

    # Display results
    for key, result in config_result.items():
        match result:
            case Success(value):
                print(f'  {key}: {value}')
            case Failure(err):
                print(f'  {key}: ERROR - {err}')

    # Check if all valid
    all_valid = all(r.is_success() for r in config_result.values())
    print(f'\nConfiguration valid: {all_valid}')

    print()


# =============================================================================
# Security: DoS Protection Example
# =============================================================================


def example_dos_protection() -> None:
    """Demonstrate built-in DoS protection for large inputs."""
    print('=== DoS Protection ===\n')

    parser: Callable[[str], Maybe[Any]] = from_type(list[int])

    # Normal sized input works fine
    normal_input = '[' + ','.join(str(i) for i in range(100)) + ']'
    result = parser(normal_input)
    match result:
        case Success(value):
            print(f'Normal input (100 elements): Success ({len(value)} items)')

    # Malicious large input is rejected quickly
    import time

    malicious_input = '[' + '1,' * 100_000 + '1]'  # ~600KB
    print(f'\nTrying malicious input ({len(malicious_input):,} chars)...')

    start = time.perf_counter()
    result = parser(malicious_input)
    elapsed_ms = (time.perf_counter() - start) * 1000

    match result:
        case Failure(err):
            print(f'Rejected in {elapsed_ms:.2f}ms (< 10ms required)')
            print(f'Error: {err}')

    print()


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """Run all examples."""
    example_basic_types()
    example_optional_types()
    example_collections()
    example_union_types()
    example_literal_types()
    example_enum_types()
    example_annotated_types()
    example_complex_types()
    example_config_parser()
    example_dos_protection()


if __name__ == '__main__':
    main()
