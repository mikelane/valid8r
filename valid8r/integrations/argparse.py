"""argparse integration for valid8r parsers.

This module provides type_from_parser to convert valid8r parsers into argparse-compatible
type functions that can be used with ArgumentParser.add_argument().

argparse's type parameter expects a callable that takes a string and either returns
a converted value (on success) or raises TypeError or ValueError (on failure).

Examples:
    >>> import argparse
    >>> from valid8r.core import parsers, validators
    >>> from valid8r.integrations.argparse import type_from_parser
    >>>
    >>> # Basic usage with email parser
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument(
    ...     '--email',
    ...     type=type_from_parser(parsers.parse_email),
    ...     help='Email address'
    ... )
    >>>
    >>> # With chained validators for port validation
    >>> def port_parser(text):
    ...     return parsers.parse_int(text).bind(
    ...         validators.minimum(1) & validators.maximum(65535)
    ...     )
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument(
    ...     '--port',
    ...     type=type_from_parser(port_parser),
    ...     help='Port number (1-65535)'
    ... )

"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from valid8r.core.maybe import Maybe

from valid8r.core.maybe import (
    Failure,
    Success,
)

T = TypeVar('T')


def type_from_parser(parser: Callable[[str | None], Maybe[T]]) -> Callable[[str], T]:
    """Convert a valid8r parser into an argparse-compatible type function.

    Creates a callable that can be used as the 'type' parameter in
    ArgumentParser.add_argument(). The returned function takes a string,
    parses it using the provided valid8r parser, and either returns the
    successfully parsed value or raises ValueError with the error message.

    Args:
        parser: A valid8r parser function that takes a string and returns Maybe[T]

    Returns:
        A callable suitable for use with argparse's 'type' parameter

    Raises:
        ValueError: When the parser returns a Failure (invalid input)

    Examples:
        >>> from valid8r.core import parsers
        >>> from valid8r.integrations.argparse import type_from_parser
        >>>
        >>> # Create an argparse type for email validation
        >>> email_type = type_from_parser(parsers.parse_email)
        >>> email = email_type('alice@example.com')
        >>> email.local
        'alice'
        >>>
        >>> # Invalid input raises ValueError
        >>> try:
        ...     email_type('not-an-email')
        ... except ValueError as e:
        ...     print('Error:', e)
        Error: ...

    """

    def argparse_type(value: str) -> T:
        """Argparse type function that uses valid8r parser.

        Args:
            value: The string value to parse

        Returns:
            The successfully parsed and validated value

        Raises:
            ValueError: If validation fails

        """
        # Parse the value using the valid8r parser
        result = parser(value)

        # Handle the Maybe result
        match result:
            case Success(parsed_value):
                # Cast to T to satisfy mypy's return type checking
                return cast('T', parsed_value)
            case Failure(error_msg):
                # argparse expects TypeError or ValueError on failure
                # ValueError is more appropriate for validation failures
                raise ValueError(error_msg) from None

        # This should never be reached due to exhaustive pattern matching
        # but mypy doesn't know that
        msg = 'Unexpected Maybe state'  # pragma: no cover
        raise RuntimeError(msg)  # pragma: no cover

    return argparse_type


__all__ = ['type_from_parser']
