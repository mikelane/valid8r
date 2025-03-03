"""String parsing functions with Maybe monad error handling."""

from __future__ import annotations

from collections.abc import Callable
from datetime import (
    date,
    datetime,
)
from enum import Enum
from functools import wraps
from typing import (
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
P = ParamSpec('P')
E = TypeVar('E', bound=Enum)

ISO_DATE_LENGTH = 10


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
        return enum_class[value]  # type: ignore[no-any-return]
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
        error = f"Failed to parse key in pair {index + 1} '{pair}': {key_result.value_or('Parse error')}"
        return False, None, None, error_message or error

    # Parse the value
    value_result = value_parser(value_str.strip())
    if value_result.is_failure():
        error = f"Failed to parse value in pair {index + 1} '{pair}': {value_result.value_or('Parse error')}"
        return False, None, None, error_message or error

    return True, key_result.value_or(None), value_result.value_or(None), None


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
        Callable[[str], Maybe[K | None]], key_parser if key_parser is not None else _default_parser
    )

    actual_value_parser: Callable[[str], Maybe[V | None]] = cast(
        Callable[[str], Maybe[V | None]], value_parser if value_parser is not None else _default_parser
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
    return Maybe.success(set(result.value_or(set())))


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
