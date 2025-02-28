"""String parsing functions with Maybe monad error handling."""

from __future__ import annotations

from collections.abc import Callable
from datetime import (
    date,
    datetime,
)
from typing import (
    Any,
    TypeVar,
)

from valid8r.core.maybe import Maybe

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

ISO_DATE_LENGTH = 10


def parse_int(input_value: str, error_message: str | None = None) -> Maybe[int]:
    """Parse a string to an integer."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    # Remove any whitespace
    cleaned_input = input_value.strip()

    try:
        # Check if the string represents a float
        if '.' in cleaned_input:
            # Convert to float first to check if it's an integer value
            float_val = float(cleaned_input)
            if float_val.is_integer():
                # It's a whole number like 42.0
                return Maybe.success(int(float_val))
            # It has a fractional part like 42.5
            return Maybe.failure(error_message or 'Input must be a valid integer')

        value = int(cleaned_input)
        return Maybe.success(value)
    except ValueError:
        return Maybe.failure(error_message or 'Input must be a valid integer')


def parse_float(input_value: str, error_message: str | None = None) -> Maybe[float]:
    """Parse a string to a float."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    try:
        value = float(input_value.strip())
        return Maybe.success(value)
    except ValueError:
        return Maybe.failure(error_message or 'Input must be a valid number')


def parse_bool(input_value: str, error_message: str | None = None) -> Maybe[bool]:
    """Parse a string to a boolean."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    # Normalize input
    input_lower = input_value.strip().lower()

    # True values
    if input_lower in ('true', 't', 'yes', 'y', '1'):
        return Maybe.success(True)

    # False values
    if input_lower in ('false', 'f', 'no', 'n', '0'):
        return Maybe.success(False)

    return Maybe.failure(error_message or 'Input must be a valid boolean')


def parse_date(input_value: str, date_format: str | None = None, error_message: str | None = None) -> Maybe[date]:
    """Parse a string to a date."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    try:
        # Clean input
        input_value = input_value.strip()

        if date_format:
            # Parse with the provided format
            dt = datetime.strptime(input_value, date_format)
            return Maybe.success(dt.date())

        # Try ISO format by default, but be more strict
        # Standard ISO format should have dashes: YYYY-MM-DD
        if len(input_value) == ISO_DATE_LENGTH and input_value[4] == '-' and input_value[7] == '-':
            return Maybe.success(date.fromisoformat(input_value))
        # Non-standard formats should be explicitly specified
        return Maybe.failure(error_message or 'Input must be a valid date')
    except ValueError:
        return Maybe.failure(error_message or 'Input must be a valid date')


def parse_complex(input_value: str, error_message: str | None = None) -> Maybe[complex]:
    """Parse a string to a complex number."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    try:
        # Strip whitespace from the outside but not inside
        input_str = input_value.strip()

        # Handle parentheses if present
        if input_str.startswith('(') and input_str.endswith(')'):
            input_str = input_str[1:-1]

        # Handle 'i' notation by converting to 'j' notation
        if 'i' in input_str and 'j' not in input_str:
            input_str = input_str.replace('i', 'j')

        # Handle spaces in complex notation (e.g., "3 + 4j")
        if ' ' in input_str:
            # Remove spaces while preserving operators
            input_str = input_str.replace(' + ', '+').replace(' - ', '-')
            input_str = input_str.replace('+ ', '+').replace('- ', '-')
            input_str = input_str.replace(' +', '+').replace(' -', '-')

        value = complex(input_str)
        return Maybe.success(value)
    except ValueError:
        return Maybe.failure(error_message or 'Input must be a valid complex number')


def _check_enum_has_empty_value(enum_class: type) -> bool:
    """Check if an enum has an empty string as a value."""
    try:
        return any(member.value == '' for member in enum_class)
    except Exception:
        return False


def _find_enum_by_value(enum_class: type, value: str) -> T | None:
    """Find an enum member by its value."""
    for member in enum_class:
        if member.value == value:
            return member
    return None


def _find_enum_by_name(enum_class: type, value: str) -> T | None:
    """Find an enum member by its name."""
    try:
        return enum_class[value]
    except KeyError:
        return None


def parse_enum(input_value: str, enum_class: type, error_message: str | None = None) -> Maybe[object]:
    """Parse a string to an enum value."""
    from enum import Enum

    if not isinstance(enum_class, type) or not issubclass(enum_class, Enum):
        return Maybe.failure(error_message or 'Invalid enum class provided')

    # Check if empty is valid for this enum
    has_empty_value = _check_enum_has_empty_value(enum_class)

    if input_value == '' and not has_empty_value:
        return Maybe.failure('Input must not be empty')

    # Try direct match with enum values
    member = _find_enum_by_value(enum_class, input_value)
    if member is not None:
        return Maybe.success(member)

    # Try enum name lookup
    member = _find_enum_by_name(enum_class, input_value)
    if member is not None:
        return Maybe.success(member)

    # Try with stripped value if different
    input_stripped = input_value.strip()
    if input_stripped != input_value:
        member = _find_enum_by_value(enum_class, input_stripped)
        if member is not None:
            return Maybe.success(member)

        member = _find_enum_by_name(enum_class, input_stripped)
        if member is not None:
            return Maybe.success(member)

    return Maybe.failure(error_message or 'Input must be a valid enumeration value')


def parse_list(
    input_value: str,
    element_parser: Callable[[str], Maybe[T]] | None = None,
    separator: str = ',',
    error_message: str | None = None,
) -> Maybe[list[T]]:
    """Parse a string to a list using the specified element parser and separator.

    Args:
        input_value: The string to parse
        element_parser: A function that parses individual elements
        separator: The string that separates elements
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed list or an error message

    """
    if not input_value:
        return Maybe.failure('Input must not be empty')

    # Use default parser if none provided
    if element_parser is None:
        element_parser = lambda s: Maybe.success(s.strip())

    # Split the input string by the separator
    elements = input_value.split(separator)

    # Parse each element
    parsed_elements = []
    for i, element in enumerate(elements):
        result = element_parser(element.strip())
        if result.is_failure():
            if error_message:
                return Maybe.failure(error_message)
            return Maybe.failure(f"Failed to parse element {i + 1} '{element}': {result.value_or('Parse error')}")
        parsed_elements.append(result.value_or(None))

    return Maybe.success(parsed_elements)


def parse_dict(
    input_value: str,
    key_parser: Callable[[str], Maybe[K]] | None = None,
    value_parser: Callable[[str], Maybe[V]] | None = None,
    pair_separator: str = ',',
    key_value_separator: str = ':',
    error_message: str | None = None,
) -> Maybe[dict[K, V]]:
    """Parse a string to a dictionary using the specified parsers and separators.

    Args:
        input_value: The string to parse
        key_parser: A function that parses keys
        value_parser: A function that parses values
        pair_separator: The string that separates key-value pairs
        key_value_separator: The string that separates keys from values
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed dictionary or an error message

    """
    if not input_value:
        return Maybe.failure('Input must not be empty')

    # Use default parsers if none provided
    if key_parser is None:
        key_parser = lambda s: Maybe.success(s.strip())
    if value_parser is None:
        value_parser = lambda s: Maybe.success(s.strip())

    # Split the input string by the pair separator
    pairs = input_value.split(pair_separator)

    # Parse each key-value pair
    parsed_dict = {}
    for i, pair in enumerate(pairs):
        if key_value_separator not in pair:
            if error_message:
                return Maybe.failure(error_message)
            return Maybe.failure(f"Invalid key-value pair '{pair}': missing separator '{key_value_separator}'")

        key_str, value_str = pair.split(key_value_separator, 1)

        # Parse the key
        key_result = key_parser(key_str.strip())
        if key_result.is_failure():
            if error_message:
                return Maybe.failure(error_message)
            return Maybe.failure(f"Failed to parse key in pair {i + 1} '{pair}': {key_result.value_or('Parse error')}")

        # Parse the value
        value_result = value_parser(value_str.strip())
        if value_result.is_failure():
            if error_message:
                return Maybe.failure(error_message)
            return Maybe.failure(
                f"Failed to parse value in pair {i + 1} '{pair}': {value_result.value_or('Parse error')}"
            )

        parsed_dict[key_result.value_or(None)] = value_result.value_or(None)

    return Maybe.success(parsed_dict)


def parse_set(
    input_value: str,
    element_parser: Callable[[str], Maybe[T]] | None = None,
    separator: str = ',',
    error_message: str | None = None,
) -> Maybe[set[T]]:
    """Parse a string to a set using the specified element parser and separator.

    Args:
        input_value: The string to parse
        element_parser: A function that parses individual elements
        separator: The string that separates elements
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed set or an error message

    """
    # Use the list parser and convert to set
    result = parse_list(input_value, element_parser, separator, error_message)
    if result.is_failure():
        return result

    # Convert to set (removes duplicates)
    return Maybe.success(set(result.value_or([])))


# Type-specific validation parsers


def parse_int_with_validation(
    input_value: str,
    min_value: int | None = None,
    max_value: int | None = None,
    error_message: str | None = None,
) -> Maybe[int]:
    """Parse a string to an integer with validation.

    Args:
        input_value: The string to parse
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed integer or an error message

    """
    result = parse_int(input_value, error_message)
    if result.is_failure():
        return result

    # Validate the parsed value
    value = result.value_or(0)

    if min_value is not None and value < min_value:
        return Maybe.failure(error_message or f'Value must be at least {min_value}')

    if max_value is not None and value > max_value:
        return Maybe.failure(error_message or f'Value must be at most {max_value}')

    return Maybe.success(value)


def parse_list_with_validation(
    input_value: str,
    element_parser: Callable[[str], Maybe[T]] | None = None,
    separator: str = ',',
    min_length: int | None = None,
    max_length: int | None = None,
    error_message: str | None = None,
) -> Maybe[list[T]]:
    """Parse a string to a list with validation.

    Args:
        input_value: The string to parse
        element_parser: A function that parses individual elements
        separator: The string that separates elements
        min_length: Minimum allowed list length
        max_length: Maximum allowed list length
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed list or an error message

    """
    result = parse_list(input_value, element_parser, separator, error_message)
    if result.is_failure():
        return result

    # Validate the parsed list
    parsed_list = result.value_or([])

    if min_length is not None and len(parsed_list) < min_length:
        return Maybe.failure(error_message or f'List must have at least {min_length} elements')

    if max_length is not None and len(parsed_list) > max_length:
        return Maybe.failure(error_message or f'List must have at most {max_length} elements')

    return Maybe.success(parsed_list)


def parse_dict_with_validation(
    input_value: str,
    key_parser: Callable[[str], Maybe[K]] | None = None,
    value_parser: Callable[[str], Maybe[V]] | None = None,
    pair_separator: str = ',',
    key_value_separator: str = ':',
    required_keys: list[str] | None = None,
    error_message: str | None = None,
) -> Maybe[dict[K, V]]:
    """Parse a string to a dictionary with validation.

    Args:
        input_value: The string to parse
        key_parser: A function that parses keys
        value_parser: A function that parses values
        pair_separator: The string that separates key-value pairs
        key_value_separator: The string that separates keys from values
        required_keys: List of keys that must be present
        error_message: Custom error message for parsing failures

    Returns:
        A Maybe containing the parsed dictionary or an error message

    """
    result = parse_dict(input_value, key_parser, value_parser, pair_separator, key_value_separator, error_message)
    if result.is_failure():
        return result

    # Validate the parsed dictionary
    parsed_dict = result.value_or({})

    if required_keys:
        missing_keys = [key for key in required_keys if key not in parsed_dict]
        if missing_keys:
            return Maybe.failure(error_message or f'Missing required keys: {", ".join(missing_keys)}')

    return Maybe.success(parsed_dict)


# Parser Registry for custom parser registration


class ParserRegistry:
    """Registry for parser functions.

    This class provides a way to register custom parsers for specific types
    and retrieve them later. It also provides a convenient way to parse strings
    to specific types using registered parsers.

    Examples:
        >>> # Register a custom parser for IP addresses
        >>> def parse_ip_address(input_value: str) -> Maybe[ipaddress.IPv4Address]:
        ...     try:
        ...         return Maybe.success(ipaddress.IPv4Address(input_value))
        ...     except ValueError:
        ...         return Maybe.failure("Invalid IP address")
        ...
        >>> ParserRegistry.register(ipaddress.IPv4Address, parse_ip_address)
        ...
        >>> # Parse a string to an IP address
        >>> result = ParserRegistry.parse("192.168.1.1", ipaddress.IPv4Address)
        >>> result.is_success()
        True
        >>> str(result.value_or(None))
        '192.168.1.1'

    """

    _parsers: dict[type, Callable] = {}

    @classmethod
    def register(cls, type_: type, parser: Callable) -> None:
        """Register a parser for a specific type.

        Args:
            type_: The type to register the parser for
            parser: The parser function

        """
        cls._parsers[type_] = parser

    @classmethod
    def get_parser(cls, type_: type) -> Callable | None:
        """Get a parser for a specific type.

        This method first looks for a direct match with the specified type.
        If no direct match is found, it looks for a match with a parent class.

        Args:
            type_: The type to get a parser for

        Returns:
            The parser function or None if not found

        """
        # Check for direct match
        if type_ in cls._parsers:
            return cls._parsers[type_]

        # Check for parent class match (inheritance)
        for registered_type, parser in cls._parsers.items():
            if isinstance(registered_type, type) and issubclass(type_, registered_type):
                return parser

        return None

    @classmethod
    def parse(cls, input_value: str, type_: type, error_message: str | None = None, **kwargs) -> Maybe[Any]:
        """Parse a string to a specific type using the registered parser.

        Args:
            input_value: The string to parse
            type_: The target type
            error_message: Custom error message for parsing failures
            **kwargs: Additional arguments to pass to the parser

        Returns:
            A Maybe containing the parsed value or an error message

        """
        parser = cls.get_parser(type_)
        if parser is None:
            return Maybe.failure(error_message or f'No parser found for type {type_.__name__}')

        return parser(input_value, **kwargs)

    @classmethod
    def register_defaults(cls) -> None:
        """Register default parsers for built-in types."""
        # Register parsers for basic types
        cls.register(int, parse_int)
        cls.register(float, parse_float)
        cls.register(bool, parse_bool)
        cls.register(complex, parse_complex)
        cls.register(date, parse_date)
        cls.register(str, lambda s: Maybe.success(s))

        # Register parsers for collection types
        cls.register(list, parse_list)
        cls.register(dict, parse_dict)
        cls.register(set, parse_set)
