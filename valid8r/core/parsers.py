"""String parsing functions with Maybe monad error handling."""

from __future__ import annotations

import re
from datetime import (
    date,
    datetime,
)
from decimal import (
    Decimal,
    InvalidOperation,
)
from enum import Enum
from functools import wraps
from typing import (
    TYPE_CHECKING,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)
from uuid import UUID

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

try:
    import uuid_utils as uuidu
except Exception:  # noqa: BLE001
    uuidu = None  # type: ignore[assignment]

try:
    from email_validator import (
        EmailNotValidError,
        validate_email,
    )

    HAS_EMAIL_VALIDATOR = True
except ImportError:
    HAS_EMAIL_VALIDATOR = False
    EmailNotValidError = None  # type: ignore[assignment,misc]
    validate_email = None  # type: ignore[assignment]

import base64
import binascii
import json
from dataclasses import dataclass
from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
    ip_address,
    ip_network,
)
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Iterable,
    )

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
P = ParamSpec('P')
E = TypeVar('E', bound=Enum)

ISO_DATE_LENGTH = 10

# Compiled regex patterns for phone parsing (cached for performance)
_PHONE_EXTENSION_PATTERN = re.compile(r'\s*[,;]\s*(\d+)$|\s+(?:x|ext\.?|extension)\s*(\d+)$', re.IGNORECASE)
_PHONE_VALID_CHARS_PATTERN = re.compile(r'^[\d\s()\-+.]+$', re.MULTILINE)
_PHONE_DIGIT_EXTRACTION_PATTERN = re.compile(r'\D')


def parse_int(input_value: str, error_message: str | None = None) -> Maybe[int]:
    """Parse a string to an integer."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    cleaned_input = input_value.strip()

    try:
        if '.' in cleaned_input:
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
        return Maybe.success(value=True)

    # False values
    if input_lower in ('false', 'f', 'no', 'n', '0'):
        return Maybe.success(value=False)

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
            dt = datetime.strptime(input_value, date_format)  # noqa: DTZ007
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


def parse_decimal(input_value: str, error_message: str | None = None) -> Maybe[Decimal]:
    """Parse a string to a Decimal.

    Args:
        input_value: String representation of a decimal number
        error_message: Optional custom error message

    Returns:
        Maybe[Decimal]: Success with Decimal value or Failure with an error message

    """
    if not input_value:
        return Maybe.failure('Input must not be empty')

    try:
        value = Decimal(input_value.strip())
        return Maybe.success(value)
    except (InvalidOperation, ValueError):
        return Maybe.failure(error_message or 'Input must be a valid number')


def _check_enum_has_empty_value(enum_class: type[Enum]) -> bool:
    """Check if an enum has an empty string as a value."""
    return any(member.value == '' for member in enum_class.__members__.values())


def _find_enum_by_value(enum_class: type[Enum], value: str) -> Enum | None:
    """Find an enum member by its value."""
    for member in enum_class.__members__.values():
        if member.value == value:
            return member
    return None


def _find_enum_by_name(enum_class: type[E], value: str) -> E | None:
    """Find an enum member by its name."""
    try:
        return enum_class[value]
    except KeyError:
        return None


def parse_enum(input_value: str, enum_class: type[E], error_message: str | None = None) -> Maybe[object]:
    """Parse a string to an enum value."""
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

    member = _find_enum_by_name(enum_class, input_value)
    if member is not None:
        return Maybe.success(member)

    input_stripped = input_value.strip()
    if input_stripped != input_value:
        member = _find_enum_by_value(enum_class, input_stripped)
        if member is not None:
            return Maybe.success(member)

    for name in enum_class.__members__:
        if name.lower() == input_value.lower():
            return Maybe.success(enum_class[name])

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

    def default_parser(s: str) -> Maybe[T]:
        return Maybe.success(s.strip())  # type: ignore[arg-type]

    parser = element_parser if element_parser is not None else default_parser

    elements = input_value.split(separator)

    parsed_elements: list[T] = []
    for i, element in enumerate(elements, start=1):
        match parser(element.strip()):
            case Success(value) if value is not None:
                parsed_elements.append(value)
            case Failure() if error_message:
                return Maybe.failure(error_message)
            case Failure(result):
                return Maybe.failure(f"Failed to parse element {i} '{element}': {result}")

    return Maybe.success(parsed_elements)


def _parse_key_value_pair(  # noqa: PLR0913
    pair: str,
    index: int,
    key_parser: Callable[[str], Maybe[K]],  # K can be None
    value_parser: Callable[[str], Maybe[V]],  # V can be None
    key_value_separator: str,
    error_message: str | None = None,
) -> tuple[bool, K | None, V | None, str | None]:
    """Parse a single key-value pair.

    Returns:
        A tuple of (success, key, value, error_message)

    """
    if key_value_separator not in pair:
        error = f"Invalid key-value pair '{pair}': missing separator '{key_value_separator}'"
        return False, None, None, error_message or error

    key_str, value_str = pair.split(key_value_separator, 1)

    # Parse the key
    key_result = key_parser(key_str.strip())
    if key_result.is_failure():
        error = f"Failed to parse key in pair {index + 1} '{pair}': {key_result.error_or('Parse error')}"
        return False, None, None, error_message or error

    # Parse the value
    value_result = value_parser(value_str.strip())
    if value_result.is_failure():
        error = f"Failed to parse value in pair {index + 1} '{pair}': {value_result.error_or('Parse error')}"
        return False, None, None, error_message or error

    # At this point both results are Success; extract concrete values by pattern matching
    match key_result:
        case Success(key_val):
            key: K | None = key_val
        case _:
            key = None

    match value_result:
        case Success(value_val):
            value: V | None = value_val
        case _:
            value = None

    return True, key, value, None


def parse_dict(  # noqa: PLR0913
    input_value: str,
    key_parser: Callable[[str], Maybe[K]] | None = None,
    value_parser: Callable[[str], Maybe[V]] | None = None,
    pair_separator: str = ',',
    key_value_separator: str = ':',
    error_message: str | None = None,
) -> Maybe[dict[K, V]]:
    """Parse a string to a dictionary using the specified parsers and separators."""
    if not input_value:
        return Maybe.failure('Input must not be empty')

    def _default_parser(s: str) -> Maybe[str | None]:
        """Parse a string by stripping whitespace."""
        return Maybe.success(s.strip())

    actual_key_parser: Callable[[str], Maybe[K | None]] = cast(
        'Callable[[str], Maybe[K | None]]', key_parser if key_parser is not None else _default_parser
    )

    actual_value_parser: Callable[[str], Maybe[V | None]] = cast(
        'Callable[[str], Maybe[V | None]]', value_parser if value_parser is not None else _default_parser
    )

    # Split the input string by the pair separator
    pairs = input_value.split(pair_separator)

    # Parse each key-value pair
    parsed_dict: dict[K, V] = {}

    for i, pair in enumerate(pairs):
        success, key, value, err = _parse_key_value_pair(
            pair, i, actual_key_parser, actual_value_parser, key_value_separator, error_message
        )

        if not success:
            return Maybe.failure(err or 'Failed to parse key-value pair')

        if key is not None and value is not None:
            parsed_dict[key] = value

    return Maybe.success(parsed_dict)


def parse_set(
    input_value: str,
    element_parser: Callable[[str], Maybe[T]] | None = None,
    separator: str | None = None,
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
    if separator is None:
        separator = ','
    # Use the list parser and convert to set
    result = parse_list(input_value, element_parser, separator, error_message)
    if result.is_failure():
        return Maybe.failure('Parse error')

    # Convert to set (removes duplicates)
    parsed_list = result.value_or([])
    return Maybe.success(set(parsed_list))


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


def parse_list_with_validation(  # noqa: PLR0913
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


def parse_dict_with_validation(  # noqa: PLR0913
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


def create_parser(convert_func: Callable[[str], T], error_message: str | None = None) -> Callable[[str], Maybe[T]]:
    """Create a parser function from a conversion function.

    This factory takes a function that converts strings to values and wraps it
    in error handling logic to return Maybe instances.

    Args:
        convert_func: A function that converts strings to values of type T
        error_message: Optional custom error message for failures

    Returns:
        A parser function that returns Maybe[T]

    Example:
        >>> from decimal import Decimal
        >>> parse_decimal = create_parser(Decimal, "Invalid decimal format")
        >>> result = parse_decimal("3.14")
        >>> result.is_success()
        True

    """

    def parser(input_value: str) -> Maybe[T]:
        if not input_value:
            return Failure('Input must not be empty')

        try:
            return Success(convert_func(input_value.strip()))
        except Exception as e:  # noqa: BLE001
            return Failure(error_message or f'Invalid {convert_func.__name__} format: {e}')

    return parser


@overload
def make_parser(func: Callable[[str], T]) -> Callable[[str], Maybe[T]]: ...


@overload
def make_parser() -> Callable[[Callable[[str], T]], Callable[[str], Maybe[T]]]: ...


def make_parser(
    func: Callable[[str], T] | None = None,
) -> Callable[[str], Maybe[T]] | Callable[[Callable[[str], T]], Callable[[str], Maybe[T]]]:
    """Create a parser function from a conversion function with a decorator.

    Example:
        @make_parser
        def parse_decimal(s: str) -> Decimal:
            return Decimal(s)

        # Or with parentheses
        @make_parser()
        def parse_decimal(s: str) -> Decimal:
            return Decimal(s)

        result = parse_decimal("123.45")  # Returns Maybe[Decimal]

    """

    def decorator(f: Callable[[str], T]) -> Callable[[str], Maybe[T]]:
        @wraps(f)
        def wrapper(input_value: str) -> Maybe[T]:
            if not input_value:
                return Maybe.failure('Input must not be empty')
            try:
                return Maybe.success(f(input_value.strip()))
            except Exception as e:  # noqa: BLE001
                return Maybe.failure(f'Invalid format for {f.__name__}, error: {e}')

        return wrapper

    # Handle both @create_parser and @create_parser() syntax
    if func is None:
        return decorator
    return decorator(func)


def validated_parser(
    convert_func: Callable[[str], T], validator: Callable[[T], Maybe[T]], error_message: str | None = None
) -> Callable[[str], Maybe[T]]:
    """Create a parser with a built-in validator.

    This combines parsing and validation in a single function.

    Args:
        convert_func: A function that converts strings to values of type T
        validator: A validator function that validates the parsed value
        error_message: Optional custom error message for parsing failures

    Returns:
        A parser function that returns Maybe[T]

    Example:
        >>> from decimal import Decimal
        >>> from valid8r.core.validators import minimum, maximum
        >>> # Create a parser for positive decimals
        >>> valid_range = lambda x: minimum(0)(x).bind(lambda y: maximum(100)(y))
        >>> parse_percent = validated_parser(Decimal, valid_range)
        >>> result = parse_percent("42.5")
        >>> result.is_success()
        True

    """
    parse = create_parser(convert_func, error_message)

    def parser(input_value: str) -> Maybe[T]:
        # First parse the input
        result = parse(input_value)

        # If parsing succeeded, validate the result
        return result.bind(validator)

    return parser


def parse_uuid(text: str, version: int | None = None, strict: bool = True) -> Maybe[UUID]:
    """Parse a string to a UUID.

    Uses uuid-utils to parse and validate UUIDs across versions 1, 3, 4, 5, 6, 7, and 8 when available.
    When ``version`` is provided, validates the parsed UUID version. In ``strict`` mode (default),
    a mismatch yields a Failure; otherwise, the mismatch is ignored and the UUID is returned.

    Args:
        text: The input string to parse as UUID.
        version: Optional expected UUID version to validate against.
        strict: Whether to enforce the expected version when provided.

    Returns:
        Maybe[UUID]: Success with a UUID object or Failure with an error message.

    """
    if not text:
        return Maybe.failure('Input must not be empty')

    s = text.strip()

    try:
        # Prefer uuid-utils if available; fall back to stdlib
        if uuidu is not None:
            parsed_any = uuidu.UUID(s)
            parsed_version = getattr(parsed_any, 'version', None)
        else:
            parsed_std = UUID(s)
            parsed_version = getattr(parsed_std, 'version', None)
    except Exception:  # noqa: BLE001
        return Maybe.failure('Input must be a valid UUID')

    if version is not None:
        supported_versions = {1, 3, 4, 5, 6, 7, 8}
        if version not in supported_versions:
            return Maybe.failure(f'Unsupported UUID version: v{version}')
        if strict and version != parsed_version:
            return Maybe.failure(f'UUID version mismatch: expected v{version}, got v{parsed_version}')

    # Return a standard library UUID object for compatibility
    try:
        return Maybe.success(UUID(s))
    except Exception:  # noqa: BLE001
        # This should not happen if initial parsing succeeded, but guard anyway
        return Maybe.failure('Input must be a valid UUID')


def parse_ipv4(text: str) -> Maybe[IPv4Address]:
    """Parse an IPv4 address string.

    Trims surrounding whitespace only. Returns Success with a concrete
    IPv4Address on success, or Failure with a deterministic error message.

    Error messages:
    - value must be a string
    - value is empty
    - not a valid IPv4 address
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    try:
        addr = ip_address(s)
    except ValueError:
        return Maybe.failure('not a valid IPv4 address')

    if isinstance(addr, IPv4Address):
        return Maybe.success(addr)

    return Maybe.failure('not a valid IPv4 address')


def parse_ipv6(text: str) -> Maybe[IPv6Address]:
    """Parse an IPv6 address string.

    Trims surrounding whitespace only. Returns Success with a concrete
    IPv6Address on success, or Failure with a deterministic error message.

    Error messages:
    - value must be a string
    - value is empty
    - not a valid IPv6 address
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    # Explicitly reject scope IDs like %eth0
    if '%' in s:
        return Maybe.failure('not a valid IPv6 address')

    try:
        addr = ip_address(s)
    except ValueError:
        return Maybe.failure('not a valid IPv6 address')

    if isinstance(addr, IPv6Address):
        return Maybe.success(addr)

    return Maybe.failure('not a valid IPv6 address')


def parse_ip(text: str) -> Maybe[IPv4Address | IPv6Address]:
    """Parse a string as either an IPv4 or IPv6 address.

    Trims surrounding whitespace only.

    Error messages:
    - value must be a string
    - value is empty
    - not a valid IP address
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    # Reject non-address forms such as IPv6 scope IDs or URLs
    if '%' in s or '://' in s:
        return Maybe.failure('not a valid IP address')

    try:
        addr = ip_address(s)
    except ValueError:
        return Maybe.failure('not a valid IP address')

    if isinstance(addr, (IPv4Address, IPv6Address)):
        return Maybe.success(addr)

    return Maybe.failure('not a valid IP address')


def parse_cidr(text: str, *, strict: bool = True) -> Maybe[IPv4Network | IPv6Network]:
    """Parse a CIDR network string (IPv4 or IPv6).

    Uses ipaddress.ip_network under the hood. By default ``strict=True``
    so host bits set will fail. With ``strict=False``, host bits are masked.

    Error messages:
    - value must be a string
    - value is empty
    - has host bits set (when strict and host bits are present)
    - not a valid network (all other parsing failures)
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    try:
        net = ip_network(s, strict=strict)
    except ValueError as exc:
        msg = str(exc)
        if 'has host bits set' in msg:
            return Maybe.failure('has host bits set')
        return Maybe.failure('not a valid network')

    if isinstance(net, (IPv4Network, IPv6Network)):
        return Maybe.success(net)

    return Maybe.failure('not a valid network')


# ---------------------------
# URL and Email parsing
# ---------------------------


@dataclass(frozen=True)
class UrlParts:
    """Structured URL components.

    Attributes:
        scheme: Lowercased scheme (e.g. "http").
        username: Username from userinfo, if present.
        password: Password from userinfo, if present.
        host: Lowercased host or IPv6 literal without brackets, or None when not provided and not required.
        port: Explicit port if present, otherwise None.
        path: Path component as-is (no normalization).
        query: Query string without leading '?'.
        fragment: Fragment without leading '#'.

    Examples:
        >>> from valid8r.core.maybe import Success
        >>> match parse_url('https://alice:pw@example.com:8443/x?q=1#top'):
        ...     case Success(u):
        ...         (u.scheme, u.username, u.password, u.host, u.port, u.path, u.query, u.fragment)
        ...     case _:
        ...         ()
        ('https', 'alice', 'pw', 'example.com', 8443, '/x', 'q=1', 'top')

    """

    scheme: str
    username: str | None
    password: str | None
    host: str | None
    port: int | None
    path: str
    query: str
    fragment: str


@dataclass(frozen=True)
class EmailAddress:
    """Structured email address.

    Attributes:
        local: Local part (preserves original case).
        domain: Domain part lowercased.

    Examples:
        >>> from valid8r.core.maybe import Success
        >>> match parse_email('First.Last+tag@Example.COM'):
        ...     case Success(addr):
        ...         (addr.local, addr.domain)
        ...     case _:
        ...         ()
        ('First.Last+tag', 'example.com')

    """

    local: str
    domain: str


@dataclass(frozen=True)
class PhoneNumber:
    """Structured North American phone number (NANP).

    Represents a parsed and validated phone number in the North American Numbering Plan
    (United States, Canada, and other NANP territories).

    Attributes:
        area_code: Three-digit area code (NPA).
        exchange: Three-digit exchange code (NXX).
        subscriber: Four-digit subscriber number.
        country_code: Country code (always '1' for NANP).
        region: Two-letter region code ('US', 'CA', etc.).
        extension: Optional extension number.

    Examples:
        >>> from valid8r.core.maybe import Success
        >>> match parse_phone('(415) 555-2671'):
        ...     case Success(phone):
        ...         (phone.area_code, phone.exchange, phone.subscriber)
        ...     case _:
        ...         ()
        ('415', '555', '2671')

    """

    area_code: str
    exchange: str
    subscriber: str
    country_code: str
    region: str
    extension: str | None

    @property
    def e164(self) -> str:
        """E.164 international format (+14155552671).

        The E.164 format is the international standard for phone numbers.
        It includes the country code prefix and no formatting separators.

        Returns:
            Phone number in E.164 format, with extension if present.
        """
        base = f'+{self.country_code}{self.area_code}{self.exchange}{self.subscriber}'
        if self.extension:
            return f'{base} x{self.extension}'
        return base

    @property
    def national(self) -> str:
        """National format ((415) 555-2671).

        The national format is the standard format for displaying phone numbers
        within a country, without the country code.

        Returns:
            Phone number in national format, with extension if present.
        """
        base = f'({self.area_code}) {self.exchange}-{self.subscriber}'
        if self.extension:
            return f'{base} ext. {self.extension}'
        return base

    @property
    def international(self) -> str:
        """International format (+1 415-555-2671).

        The international format includes the country code and uses dashes
        as separators.

        Returns:
            Phone number in international format, with extension if present.
        """
        base = f'+{self.country_code} {self.area_code}-{self.exchange}-{self.subscriber}'
        if self.extension:
            return f'{base} ext. {self.extension}'
        return base

    @property
    def raw_digits(self) -> str:
        """Raw digits with country code (14155552671).

        Returns all digits including the country code, with no formatting.
        Does not include the extension.

        Returns:
            All digits as a string without any formatting.
        """
        return f'{self.country_code}{self.area_code}{self.exchange}{self.subscriber}'


def _is_valid_hostname_label(label: str) -> bool:
    if not (1 <= len(label) <= 63):
        return False
    # Alnum or hyphen; cannot start or end with hyphen
    if label.startswith('-') or label.endswith('-'):
        return False
    for ch in label:
        if ch.isalnum() or ch == '-':
            continue
        return False
    return True


def _is_valid_hostname(host: str) -> bool:
    # Allow localhost explicitly
    if host.lower() == 'localhost':
        return True

    if len(host) == 0 or len(host) > 253:
        return False

    # Reject underscores and empty labels
    labels = host.split('.')
    return all(not (part == '' or not _is_valid_hostname_label(part)) for part in labels)


def _parse_userinfo_and_hostport(netloc: str) -> tuple[str | None, str | None, str]:
    """Split userinfo and hostport from a netloc string."""
    if '@' in netloc:
        userinfo, hostport = netloc.rsplit('@', 1)
        if ':' in userinfo:
            user, pwd = userinfo.split(':', 1)
        else:
            user, pwd = userinfo, None
        return (user or None), (pwd or None), hostport
    return None, None, netloc


def _parse_host_and_port(hostport: str) -> tuple[str | None, int | None]:
    """Parse host and optional port from hostport.

    Supports IPv6 literals in brackets.
    Returns (host, port). Host is None when missing.
    """
    if not hostport:
        return None, None

    host = None
    port: int | None = None

    if hostport.startswith('['):
        # IPv6 literal [::1] or [::1]:443
        if ']' not in hostport:
            return None, None
        end = hostport.find(']')
        host = hostport[1:end]
        rest = hostport[end + 1 :]
        if rest.startswith(':'):
            try:
                port_val = int(rest[1:])
            except ValueError:
                return None, None
            if not (0 <= port_val <= 65535):
                return None, None
            port = port_val
        elif rest != '':
            # Garbage after bracket
            return None, None
        return host, port

    # Not bracketed: split on last ':' to allow IPv6 bracket requirement
    if ':' in hostport:
        host_candidate, port_str = hostport.rsplit(':', 1)
        if host_candidate == '':
            return None, None
        try:
            port_val = int(port_str)
        except ValueError:
            # Could be part of IPv6 without brackets (not supported by URL syntax)
            return hostport, None
        if not (0 <= port_val <= 65535):
            return None, None
        return host_candidate, port_val

    return hostport, None


def _validate_url_host(host: str | None, original_netloc: str) -> bool:
    if host is None:
        return False

    # If original contained brackets or host contains ':' treat as IPv6
    if original_netloc.startswith('[') or ':' in host:
        try:
            _ = ip_address(host)
            return isinstance(_, (IPv6Address, IPv4Address))
        except ValueError:
            return False

    # Try IPv4
    try:
        _ = ip_address(host)
        if isinstance(_, IPv4Address):
            return True
    except ValueError:
        pass

    # Hostname
    return _is_valid_hostname(host)


def parse_url(
    text: str,
    *,
    allowed_schemes: Iterable[str] = ('http', 'https'),
    require_host: bool = True,
) -> Maybe[UrlParts]:
    """Parse a URL with light validation.

    Rules:
    - Trim surrounding whitespace only
    - Require scheme in allowed_schemes (defaults to http/https)
    - If require_host, netloc must include a valid host (hostname, IPv4, or bracketed IPv6)
    - Lowercase scheme and host; do not modify path/query/fragment

    Failure messages (exact substrings):
    - Input must be a string
    - Input must not be empty
    - Unsupported URL scheme
    - URL requires host
    - Invalid host

    Args:
        text: The URL string to parse
        allowed_schemes: Iterable of allowed scheme names (default: ('http', 'https'))
        require_host: Whether to require a host in the URL (default: True)

    Returns:
        Maybe[UrlParts]: Success with UrlParts containing parsed components, or Failure with error message

    Examples:
        >>> from valid8r.core.parsers import parse_url
        >>> from valid8r.core.maybe import Success
        >>>
        >>> # Parse a complete URL
        >>> result = parse_url('https://user:pass@api.example.com:8080/v1/users?active=true#section')
        >>> isinstance(result, Success)
        True
        >>> url = result.value
        >>> url.scheme
        'https'
        >>> url.host
        'api.example.com'
        >>> url.port
        8080
        >>> url.path
        '/v1/users'
        >>> url.query
        'active=true'
        >>> url.fragment
        'section'
        >>>
        >>> # Access credentials
        >>> url.username
        'user'
        >>> url.password
        'pass'
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    parts = urlsplit(s)

    scheme_lower = parts.scheme.lower()
    if scheme_lower == '' or scheme_lower not in {sch.lower() for sch in allowed_schemes}:
        return Maybe.failure('Unsupported URL scheme')

    username: str | None
    password: str | None
    host: str | None
    port: int | None

    username = None
    password = None
    host = None
    port = None

    netloc = parts.netloc

    if netloc:
        username, password, hostport = _parse_userinfo_and_hostport(netloc)
        host, port = _parse_host_and_port(hostport)

        if host is not None:
            host = host.lower()

        # Validate host when present
        if host is not None and not _validate_url_host(host, netloc):
            return Maybe.failure('Invalid host')
    elif require_host:
        return Maybe.failure('URL requires host')

    # When require_host is True we must have a host
    if require_host and (host is None or host == ''):
        return Maybe.failure('URL requires host')

    result = UrlParts(
        scheme=scheme_lower,
        username=username,
        password=password,
        host=host,
        port=port,
        path=parts.path,
        query=parts.query,
        fragment=parts.fragment,
    )

    return Maybe.success(result)


def parse_email(text: str) -> Maybe[EmailAddress]:
    """Parse a bare email address of the form ``local@domain``.

    Uses the email-validator library for RFC 5322 compliant validation.
    Domain names are normalized to lowercase, local parts preserve their case.

    Requires the email-validator library to be installed. If not available,
    returns a Failure indicating the library is required.

    Rules:
    - Trim surrounding whitespace
    - Full RFC 5322 email validation
    - Supports internationalized domains (IDNA)
    - Domain is lowercased in the result; local part preserves case

    Failure messages:
    - Input must be a string
    - Input must not be empty
    - email-validator library is required but not installed
    - Various RFC-compliant validation error messages from email-validator

    Args:
        text: The email address string to parse

    Returns:
        Maybe[EmailAddress]: Success with EmailAddress or Failure with error message

    Examples:
        >>> from valid8r.core.parsers import parse_email
        >>> from valid8r.core.maybe import Success
        >>>
        >>> # Parse an email with case normalization
        >>> result = parse_email('User.Name+tag@Example.COM')
        >>> isinstance(result, Success)
        True
        >>> email = result.value
        >>> # Local part preserves original case
        >>> email.local
        'User.Name+tag'
        >>> # Domain is normalized to lowercase
        >>> email.domain
        'example.com'
    """
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    if not HAS_EMAIL_VALIDATOR:
        return Maybe.failure('email-validator library is required but not installed')

    try:
        # Validate without DNS lookups
        result = validate_email(s, check_deliverability=False)

        # Return normalized components
        return Maybe.success(EmailAddress(local=result.local_part, domain=result.domain))
    except EmailNotValidError as e:
        return Maybe.failure(str(e))
    except Exception as e:  # noqa: BLE001
        return Maybe.failure(f'email validation error: {e}')


def parse_phone(text: str | None, *, region: str = 'US', strict: bool = False) -> Maybe[PhoneNumber]:  # noqa: PLR0912
    """Parse a North American phone number (NANP format).

    Parses phone numbers in the North American Numbering Plan format (US, Canada, etc.).
    Supports various formatting styles and validates area codes and exchanges.

    Rules:
    - Accepts 10-digit or 11-digit (with country code 1) phone numbers
    - Strips all non-digit characters except extension markers
    - Validates area code (NPA): cannot start with 0 or 1, cannot be 555
    - Validates exchange (NXX): cannot start with 0 or 1, cannot be 555 or 911
    - Supports extensions with markers: x, ext, extension, comma
    - In strict mode, requires formatting characters (not just digits)
    - Defaults to US region unless specified

    Failure messages:
    - Phone number cannot be empty
    - Phone number must have exactly 10 digits (after country code)
    - Invalid area code (starts with 0/1 or reserved)
    - Invalid exchange (starts with 0/1, reserved, or emergency)
    - Only North American phone numbers are supported
    - Invalid format (contains non-digit/non-separator characters)
    - Strict mode requires formatting characters
    - Invalid extension (non-numeric or too long)

    Args:
        text: The phone number string to parse
        region: Two-letter region code (default: 'US')
        strict: If True, requires formatting characters (default: False)

    Returns:
        Maybe[PhoneNumber]: Success with PhoneNumber or Failure with error message

    Examples:
        >>> match parse_phone('(415) 555-2671'):
        ...     case Success(phone):
        ...         phone.area_code
        ...     case _:
        ...         None
        '415'

        >>> match parse_phone('415-555-2671 x123'):
        ...     case Success(phone):
        ...         phone.extension
        ...     case _:
        ...         None
        '123'

        >>> match parse_phone('+1 604 555 1234', region='CA'):
        ...     case Success(phone):
        ...         phone.region
        ...     case _:
        ...         None
        'CA'
    """
    # Handle None or empty input
    if text is None or not isinstance(text, str):
        return Maybe.failure('Phone number cannot be empty')

    s = text.strip()
    if s == '':
        return Maybe.failure('Phone number cannot be empty')

    # Extract extension if present
    extension = None
    extension_match = _PHONE_EXTENSION_PATTERN.search(s)
    if extension_match:
        # Get the captured group (either group 1 or 2)
        extension = extension_match.group(1) or extension_match.group(2)
        # Validate extension length
        if len(extension) > 8:
            return Maybe.failure('Extension is too long (maximum 8 digits)')
        # Remove extension from phone number for parsing
        s = s[: extension_match.start()]

    # Check for invalid characters before extracting digits
    # Allow only: digits, whitespace (including tabs/newlines), ()-.+ and common separators
    if not _PHONE_VALID_CHARS_PATTERN.match(s):
        return Maybe.failure('Invalid format: phone number contains invalid characters')

    # Extract only digits
    digits = _PHONE_DIGIT_EXTRACTION_PATTERN.sub('', s)

    # Check for strict mode - original must have formatting
    if strict and text.strip() == digits:
        return Maybe.failure('Strict mode requires formatting characters (e.g., dashes, parentheses, spaces)')

    # Validate digit count
    if len(digits) == 0:
        return Maybe.failure('Phone number cannot be empty')

    # Handle country code
    country_code = '1'
    if len(digits) == 11:
        if digits[0] != '1':
            return Maybe.failure('Only North American phone numbers (country code 1) are supported')
        digits = digits[1:]  # Strip country code
    elif len(digits) > 11:
        # Check if it starts with a non-1 digit (likely international)
        if digits[0] != '1':
            return Maybe.failure('Only North American phone numbers (country code 1) are supported')
        return Maybe.failure(f'Phone number must have 10 digits, got {len(digits)}')
    elif len(digits) != 10:
        return Maybe.failure(f'Phone number must have 10 digits, got {len(digits)}')

    # Check for extremely long input (security)
    if len(text) > 100:
        return Maybe.failure('Invalid format: phone number is too long')

    # Extract components
    area_code = digits[0:3]
    exchange = digits[3:6]
    subscriber = digits[6:10]

    # Validate area code (NPA)
    if area_code[0] in ('0', '1'):
        return Maybe.failure(f'Invalid area code: {area_code} (cannot start with 0 or 1)')
    if area_code == '555':
        return Maybe.failure(f'Invalid area code: {area_code} (reserved for fiction)')

    # Validate exchange (NXX)
    if exchange[0] in ('0', '1'):
        return Maybe.failure(f'Invalid exchange: {exchange} (cannot start with 0 or 1)')
    if exchange == '911':
        return Maybe.failure(f'Invalid exchange: {exchange} (emergency number)')
    # 555 exchange with 555x subscriber numbers (555-0000 to 555-9999) are fictional
    if exchange == '555' and subscriber.startswith('555'):
        return Maybe.failure(f'Invalid exchange: {exchange} with subscriber {subscriber} (reserved for fiction)')

    return Maybe.success(
        PhoneNumber(
            area_code=area_code,
            exchange=exchange,
            subscriber=subscriber,
            country_code=country_code,
            region=region,
            extension=extension,
        )
    )


def parse_slug(
    text: str,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
) -> Maybe[str]:
    """Parse a URL-safe slug (lowercase letters, numbers, hyphens only).

    A valid slug contains only lowercase letters, numbers, and hyphens.
    Cannot start/end with hyphen or have consecutive hyphens.

    Args:
        text: String to validate as slug
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)

    Returns:
        Maybe[str]: Success with slug or Failure with error

    Examples:
        >>> from valid8r.core.parsers import parse_slug
        >>>
        >>> # Valid slugs
        >>> parse_slug('hello-world').value_or(None)
        'hello-world'
        >>> parse_slug('blog-post-123').value_or(None)
        'blog-post-123'
        >>> parse_slug('a').value_or(None)
        'a'
        >>>
        >>> # With length constraints
        >>> parse_slug('hello', min_length=5).value_or(None)
        'hello'
        >>> parse_slug('hello', max_length=10).value_or(None)
        'hello'
        >>>
        >>> # Invalid slugs
        >>> parse_slug('').is_failure()
        True
        >>> parse_slug('Hello-World').is_failure()
        True
        >>> parse_slug('hello_world').is_failure()
        True
        >>> parse_slug('-hello').is_failure()
        True
        >>> parse_slug('hello-').is_failure()
        True
        >>> parse_slug('hello--world').is_failure()
        True
        >>>
        >>> # Length constraint failures
        >>> parse_slug('hi', min_length=5).is_failure()
        True
        >>> parse_slug('very-long-slug', max_length=5).is_failure()
        True
    """
    if not text:
        return Maybe.failure('Slug cannot be empty')

    # Check length constraints
    if min_length is not None and len(text) < min_length:
        return Maybe.failure(f'Slug is too short (minimum {min_length} characters)')

    if max_length is not None and len(text) > max_length:
        return Maybe.failure(f'Slug is too long (maximum {max_length} characters)')

    # Check for leading hyphen
    if text.startswith('-'):
        return Maybe.failure('Slug cannot start with a hyphen')

    # Check for trailing hyphen
    if text.endswith('-'):
        return Maybe.failure('Slug cannot end with a hyphen')

    # Check for consecutive hyphens
    if '--' in text:
        return Maybe.failure('Slug cannot contain consecutive hyphens')

    # Check for invalid characters (not lowercase, digit, or hyphen)
    if not re.match(r'^[a-z0-9-]+$', text):
        # Check specifically for uppercase
        if any(c.isupper() for c in text):
            return Maybe.failure('Slug must contain only lowercase letters, numbers, and hyphens')
        return Maybe.failure('Slug contains invalid characters')

    return Maybe.success(text)


def parse_json(text: str) -> Maybe[object]:
    """Parse a JSON string into a Python object.

    Supports all JSON types: objects, arrays, strings, numbers, booleans, null.

    Args:
        text: JSON-formatted string

    Returns:
        Maybe[object]: Success with parsed object or Failure with error

    Examples:
        >>> from valid8r.core.parsers import parse_json
        >>>
        >>> # JSON objects
        >>> parse_json('{"name": "Alice", "age": 30}').value_or(None)
        {'name': 'Alice', 'age': 30}
        >>>
        >>> # JSON arrays
        >>> parse_json('[1, 2, 3, 4, 5]').value_or(None)
        [1, 2, 3, 4, 5]
        >>>
        >>> # JSON primitives
        >>> parse_json('"hello world"').value_or(None)
        'hello world'
        >>> parse_json('42').value_or(None)
        42
        >>> parse_json('true').value_or(None)
        True
        >>> parse_json('false').value_or(None)
        False
        >>> parse_json('null').value_or(None)
        >>>
        >>> # Invalid JSON
        >>> parse_json('').is_failure()
        True
        >>> parse_json('{invalid}').is_failure()
        True
        >>> parse_json('{"name": "Alice"').is_failure()
        True
    """
    if not text:
        return Maybe.failure('JSON input cannot be empty')

    try:
        result = json.loads(text)
        return Maybe.success(result)
    except json.JSONDecodeError as e:
        return Maybe.failure(f'Invalid JSON: {e.msg}')


def parse_base64(text: str) -> Maybe[bytes]:
    r"""Parse and decode a base64-encoded string.

    Accepts both standard and URL-safe base64, with or without padding.
    Handles whitespace and newlines within the base64 string.

    Args:
        text: Base64-encoded string

    Returns:
        Maybe[bytes]: Success with decoded bytes or Failure with error

    Examples:
        >>> from valid8r.core.parsers import parse_base64
        >>>
        >>> # Standard base64 with padding
        >>> parse_base64('SGVsbG8gV29ybGQ=').value_or(None)
        b'Hello World'
        >>>
        >>> # Standard base64 without padding
        >>> parse_base64('SGVsbG8gV29ybGQ').value_or(None)
        b'Hello World'
        >>>
        >>> # URL-safe base64 (hyphens and underscores)
        >>> parse_base64('A-A=').is_success()
        True
        >>> parse_base64('Pz8_').is_success()
        True
        >>>
        >>> # Base64 with whitespace (automatically stripped)
        >>> parse_base64(' SGVsbG8gV29ybGQ= ').value_or(None)
        b'Hello World'
        >>>
        >>> # Invalid base64
        >>> parse_base64('').is_failure()
        True
        >>> parse_base64('Not@Valid!').is_failure()
        True
        >>> parse_base64('====').is_failure()
        True
    """
    # Strip all whitespace (including internal newlines)
    text = ''.join(text.split())

    if not text:
        return Maybe.failure('Base64 input cannot be empty')

    try:
        # Replace URL-safe characters with standard base64
        text = text.replace('-', '+').replace('_', '/')

        # Add padding if missing
        missing_padding = len(text) % 4
        if missing_padding:
            text += '=' * (4 - missing_padding)

        decoded = base64.b64decode(text, validate=True)
        return Maybe.success(decoded)
    except (ValueError, binascii.Error):
        return Maybe.failure('Base64 contains invalid characters')


def parse_jwt(text: str) -> Maybe[str]:
    """Parse and validate a JWT (JSON Web Token) structure.

    Validates that the JWT has exactly three parts (header.payload.signature)
    separated by dots, and that each part is valid base64url.
    Also validates that header and payload are valid JSON.

    Note: This function validates JWT structure only. It does NOT verify
    the cryptographic signature. Use a dedicated JWT library (e.g., PyJWT)
    for signature verification and claims validation.

    Args:
        text: JWT string to validate

    Returns:
        Maybe[str]: Success with original JWT or Failure with error

    Examples:
        >>> from valid8r.core.parsers import parse_jwt
        >>>
        >>> # Valid JWT (structure only - signature not verified)
        >>> jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig'
        >>> parse_jwt(jwt).is_success()
        True
        >>>
        >>> # JWT with whitespace (automatically stripped)
        >>> parse_jwt(' ' + jwt + ' ').is_success()
        True
        >>>
        >>> # Invalid: empty string
        >>> parse_jwt('').is_failure()
        True
        >>>
        >>> # Invalid: wrong number of parts
        >>> parse_jwt('header.payload').is_failure()
        True
        >>> parse_jwt('a.b.c.d').is_failure()
        True
        >>>
        >>> # Invalid: non-base64url encoding
        >>> parse_jwt('not-base64!.eyJzdWIiOiIxMjM0In0.sig').is_failure()
        True
        >>>
        >>> # Invalid: non-JSON header/payload
        >>> parse_jwt('bm90anNvbg==.eyJzdWIiOiIxMjM0In0.sig').is_failure()
        True
    """
    # Strip whitespace
    text = text.strip()

    if not text:
        return Maybe.failure('JWT cannot be empty')

    parts = text.split('.')
    if len(parts) != 3:
        return Maybe.failure('JWT must have exactly three parts separated by dots')

    # Helper to convert base64url to base64 with padding
    def decode_base64url(part: str) -> bytes:
        base64_part = part.replace('-', '+').replace('_', '/')
        missing_padding = len(base64_part) % 4
        if missing_padding:
            base64_part += '=' * (4 - missing_padding)
        return base64.b64decode(base64_part, validate=True)

    # Validate header (part 0)
    if not parts[0]:
        return Maybe.failure('JWT header cannot be empty')

    try:
        header_bytes = decode_base64url(parts[0])
        json.loads(header_bytes)
    except (ValueError, binascii.Error):
        return Maybe.failure('JWT header is not valid base64')
    except json.JSONDecodeError:
        return Maybe.failure('JWT header is not valid JSON')

    # Validate payload (part 1)
    if not parts[1]:
        return Maybe.failure('JWT payload cannot be empty')

    try:
        payload_bytes = decode_base64url(parts[1])
        json.loads(payload_bytes)
    except (ValueError, binascii.Error):
        return Maybe.failure('JWT payload is not valid base64')
    except json.JSONDecodeError:
        return Maybe.failure('JWT payload is not valid JSON')

    # Validate signature (part 2)
    if not parts[2]:
        return Maybe.failure('JWT signature cannot be empty')

    try:
        decode_base64url(parts[2])
    except (ValueError, binascii.Error):
        return Maybe.failure('JWT signature is not valid base64')

    return Maybe.success(text)


# Public API exports
__all__ = [
    'EmailAddress',
    'PhoneNumber',
    'UrlParts',
    'create_parser',
    'make_parser',
    'parse_base64',
    'parse_bool',
    'parse_cidr',
    'parse_complex',
    'parse_date',
    'parse_decimal',
    'parse_dict',
    'parse_dict_with_validation',
    'parse_email',
    'parse_enum',
    'parse_float',
    'parse_int',
    'parse_int_with_validation',
    'parse_ip',
    'parse_ipv4',
    'parse_ipv6',
    'parse_json',
    'parse_jwt',
    'parse_list',
    'parse_list_with_validation',
    'parse_phone',
    'parse_set',
    'parse_slug',
    'parse_url',
    'parse_uuid',
    'validated_parser',
]
