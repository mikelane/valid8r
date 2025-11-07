"""Click integration for valid8r parsers.

This module provides ParamTypeAdapter to use valid8r parsers as Click ParamTypes.

Examples:
    >>> import click
    >>> from valid8r.core import parsers, validators
    >>> from valid8r.integrations.click import ParamTypeAdapter
    >>>
    >>> # Basic usage with email parser
    >>> @click.command()
    ... @click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
    ... def create_user(email):
    ...     click.echo(f"Creating user: {email.local}@{email.domain}")
    >>>
    >>> # With chained validators for port validation
    >>> port_parser = parsers.parse_int_with_validation(
    ...     validators.minimum(1) & validators.maximum(65535)
    ... )
    >>> @click.command()
    ... @click.option('--port', type=ParamTypeAdapter(port_parser, name='port'))
    ... def start_server(port):
    ...     click.echo(f"Starting server on port {port}")

"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from valid8r.core.maybe import Maybe

import click

from valid8r.core.maybe import (
    Failure,
    Success,
)


class ParamTypeAdapter(click.ParamType):
    """Click ParamType adapter for valid8r parsers.

    This class wraps a valid8r parser function (returning Maybe[T]) into a Click ParamType,
    enabling seamless integration of valid8r's rich validation ecosystem with Click CLIs.

    Args:
        parser: A function that takes a string and returns Maybe[T]
        name: Optional custom name for the type (defaults to parser.__name__)
        error_prefix: Optional prefix for error messages (e.g., "Email address")

    Examples:
        >>> from valid8r.core import parsers
        >>> from valid8r.integrations.click import ParamTypeAdapter
        >>>
        >>> # Simple email validation
        >>> email_type = ParamTypeAdapter(parsers.parse_email)
        >>> email_type.name
        'parse_email'
        >>>
        >>> # With custom name
        >>> port_type = ParamTypeAdapter(parsers.parse_int, name='port')
        >>> port_type.name
        'port'
        >>>
        >>> # With custom error prefix
        >>> email_type = ParamTypeAdapter(
        ...     parsers.parse_email,
        ...     error_prefix='Email address'
        ... )

    """

    def __init__(
        self,
        parser: Callable[[str], Maybe[Any]],
        name: str | None = None,
        error_prefix: str | None = None,
    ) -> None:
        """Initialize the ParamTypeAdapter.

        Args:
            parser: A valid8r parser function
            name: Custom name for the type (defaults to parser.__name__)
            error_prefix: Custom prefix for error messages

        """
        self.parser = parser
        self.name = name or parser.__name__
        self.error_prefix = error_prefix

    def convert(
        self,
        value: Any,  # noqa: ANN401
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Any:  # noqa: ANN401
        """Convert and validate the input value using the parser.

        Args:
            value: The input value to convert
            param: The Click parameter being processed
            ctx: The Click context

        Returns:
            The successfully parsed and validated value

        Raises:
            click.exceptions.BadParameter: If validation fails

        """
        # If value is not a string, it's already been converted (e.g., from a callback)
        # In this case, just pass it through
        if not isinstance(value, str):
            return value

        # Parse the value using the valid8r parser
        result = self.parser(value)

        # Handle the Maybe result
        match result:
            case Success(val):
                return val
            case Failure(err):
                # Prepend error prefix if provided
                message = f'{self.error_prefix}: {err}' if self.error_prefix else err

                # Call Click's fail method to raise BadParameter
                self.fail(message, param, ctx)

        # This should never be reached due to exhaustive pattern matching
        # but mypy doesn't know that
        msg = 'Unexpected Maybe state'
        raise RuntimeError(msg)


__all__ = ['ParamTypeAdapter']
