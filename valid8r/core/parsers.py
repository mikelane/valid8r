"""String parsing functions with Maybe monad error handling."""

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
