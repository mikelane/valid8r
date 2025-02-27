"""String parsing functions with Maybe monad error handling.

This module provides functions to parse strings into various Python types.
All parsing functions return Maybe objects, allowing for clean error handling.
"""

from __future__ import annotations

from datetime import (
    date,
    datetime,
)
from typing import TypeVar

from valid8r.core.maybe import Maybe

T = TypeVar('T')

ISO_DATE_LENGTH = 10


def parse_int(input_value: str, error_message: str | None = None) -> Maybe[int]:
    """Parse a string to an integer.

    Args:
        input_value: String input to parse
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed integer or an error

    Examples:
        >>> parse_int("42")
        Just(42)
        >>> parse_int("abc")
        Nothing(Input must be a valid integer)

    """
    if not input_value:
        return Maybe.nothing('Input must not be empty')

    # Remove any whitespace
    cleaned_input = input_value.strip()

    try:
        # Check if the string represents a float
        if '.' in cleaned_input:
            # Convert to float first to check if it's an integer value
            float_val = float(cleaned_input)
            if float_val.is_integer():
                # It's a whole number like 42.0
                return Maybe.just(int(float_val))
            # It has a fractional part like 42.5
            return Maybe.nothing(error_message or 'Input must be a valid integer')

        value = int(cleaned_input)
        return Maybe.just(value)
    except ValueError:
        return Maybe.nothing(error_message or 'Input must be a valid integer')
    except OverflowError:
        return Maybe.nothing(error_message or 'Value is too large')


def parse_float(input_value: str, error_message: str | None = None) -> Maybe[float]:
    """Parse a string to a float.

    Args:
        input_value: String input to parse
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed float or an error

    """
    if not input_value:
        return Maybe.nothing('Input must not be empty')

    try:
        value = float(input_value.strip())
        return Maybe.just(value)
    except ValueError:
        return Maybe.nothing(error_message or 'Input must be a valid number')


def parse_bool(input_value: str, error_message: str | None = None) -> Maybe[bool]:
    """Parse a string to a boolean.

    Args:
        input_value: String input to parse
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed boolean or an error

    """
    if not input_value:
        return Maybe.nothing('Input must not be empty')

    # Normalize input
    input_lower = input_value.strip().lower()

    # True values
    if input_lower in ('true', 't', 'yes', 'y', '1'):
        return Maybe.just(value=True)

    # False values
    if input_lower in ('false', 'f', 'no', 'n', '0'):
        return Maybe.just(value=False)

    return Maybe.nothing(error_message or 'Input must be a valid boolean')


def parse_date(input_value: str, date_format: str | None = None, error_message: str | None = None) -> Maybe[date]:
    """Parse a string to a date.

    Args:
        input_value: String input to parse
        date_format: Optional format string (strftime format)
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed date or an error

    """
    if not input_value:
        return Maybe.nothing('Input must not be empty')

    try:
        # Clean input
        input_value = input_value.strip()

        if date_format:
            # Parse with the provided format
            dt = datetime.strptime(input_value, date_format)  # noqa: DTZ007
            return Maybe.just(dt.date())

        # Try ISO format by default, but be more strict
        # Standard ISO format should have dashes: YYYY-MM-DD
        if len(input_value) == ISO_DATE_LENGTH and input_value[4] == '-' and input_value[7] == '-':
            return Maybe.just(date.fromisoformat(input_value))
        # Non-standard formats should be explicitly specified
        return Maybe.nothing(error_message or 'Input must be a valid date')
    except ValueError:
        return Maybe.nothing(error_message or 'Input must be a valid date')


def parse_complex(input_value: str, error_message: str | None = None) -> Maybe[complex]:
    """Parse a string to a complex number.

    Args:
        input_value: String input to parse
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed complex number or an error

    Examples:
        >>> parse_complex("3+4j")
        Just((3+4j))
        >>> parse_complex("3+4i")  # Also supports mathematical 'i' notation
        Just((3+4j))
        >>> parse_complex("not a complex")
        Nothing(Input must be a valid complex number)

    """
    if not input_value:
        return Maybe.nothing('Input must not be empty')

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
        # This is tricky because we need to preserve the signs
        if ' ' in input_str:
            # Remove spaces while preserving operators
            input_str = input_str.replace(' + ', '+').replace(' - ', '-')
            input_str = input_str.replace('+ ', '+').replace('- ', '-')
            input_str = input_str.replace(' +', '+').replace(' -', '-')

        value = complex(input_str)
        return Maybe.just(value)
    except ValueError:
        return Maybe.nothing(error_message or 'Input must be a valid complex number')


def _check_enum_has_empty_value(enum_class: type) -> bool:
    """Check if an enum has an empty string as a value."""
    try:
        return any(member.value == '' for member in enum_class)
    except Exception:  # noqa: BLE001
        # Handle any issues with iterating through the enum
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
    """Parse a string to an enum value.

    Args:
        input_value: String input to parse
        enum_class: The enum class to use for parsing
        error_message: Optional custom error message

    Returns:
        A Maybe containing either the parsed enum value or an error

    Examples:
        >>> from enum import Enum
        >>> class Color(Enum):
        ...     RED = "RED"
        ...     GREEN = "GREEN"
        ...     BLUE = "BLUE"
        >>> parse_enum("RED", Color)
        Just(Color.RED)
        >>> parse_enum("YELLOW", Color)
        Nothing(Input must be a valid enumeration value)

    """
    # First, check if enum_class is actually an Enum
    from enum import Enum

    if not isinstance(enum_class, type) or not issubclass(enum_class, Enum):
        return Maybe.nothing(error_message or 'Invalid enum class provided')

    # Check if empty is valid for this enum
    has_empty_value = _check_enum_has_empty_value(enum_class)

    if input_value == '' and not has_empty_value:
        return Maybe.nothing('Input must not be empty')

    # Try direct match with enum values
    member = _find_enum_by_value(enum_class, input_value)
    if member is not None:
        return Maybe.just(member)

    # Try enum name lookup
    member = _find_enum_by_name(enum_class, input_value)
    if member is not None:
        return Maybe.just(member)

    # Try with stripped value if different
    input_stripped = input_value.strip()
    if input_stripped != input_value:
        member = _find_enum_by_value(enum_class, input_stripped)
        if member is not None:
            return Maybe.just(member)

        member = _find_enum_by_name(enum_class, input_stripped)
        if member is not None:
            return Maybe.just(member)

    return Maybe.nothing(error_message or 'Input must be a valid enumeration value')
