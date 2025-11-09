"""Typer integration for valid8r parsers.

This module provides TyperParser to use valid8r parsers as Typer parameter types.
Since Typer uses Click internally, TyperParser wraps the Click ParamTypeAdapter.

Examples:
    >>> import typer
    >>> from typing_extensions import Annotated
    >>> from valid8r.core import parsers
    >>> from valid8r.integrations.typer import TyperParser
    >>>
    >>> app = typer.Typer()
    >>>
    >>> # Basic usage with email parser
    >>> @app.command()
    ... def create_user(
    ...     email: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_email))]
    ... ) -> None:
    ...     print(f"Creating user: {email.local}@{email.domain}")
    >>>
    >>> # With chained validators for port validation
    >>> from valid8r.core import validators
    >>> def port_parser(text: str | None):
    ...     return parsers.parse_int(text).bind(
    ...         validators.minimum(1) & validators.maximum(65535)
    ...     )
    >>> @app.command()
    ... def start_server(
    ...     port: Annotated[int, typer.Option(parser=TyperParser(port_parser))]
    ... ) -> None:
    ...     print(f"Starting server on port {port}")

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import click

    from valid8r.core.maybe import Maybe

from valid8r.integrations.click import ParamTypeAdapter


class TyperParser(ParamTypeAdapter):
    """Typer parameter type adapter for valid8r parsers.

    This class wraps a valid8r parser function (returning Maybe[T]) into a Typer-compatible
    parameter type. Since Typer uses Click internally, this is a thin wrapper around
    ParamTypeAdapter that can be used with Typer's Option() and Argument().

    TyperParser can be used in two ways with Typer:
    1. As a Click ParamType: typer.Option(click_type=TyperParser(...))
    2. As a callable parser: typer.Option(parser=TyperParser(...))

    Args:
        parser: A function that takes a string and returns Maybe[T]
        name: Optional custom name for the type (defaults to parser.__name__)
        error_prefix: Optional prefix for error messages (e.g., "Email address")

    Examples:
        >>> from valid8r.core import parsers
        >>> from valid8r.integrations.typer import TyperParser
        >>>
        >>> # Simple email validation
        >>> email_type = TyperParser(parsers.parse_email)
        >>> email_type.name
        'parse_email'
        >>>
        >>> # With custom name
        >>> port_type = TyperParser(parsers.parse_int, name='port')
        >>> port_type.name
        'port'
        >>>
        >>> # With custom error prefix
        >>> email_type = TyperParser(
        ...     parsers.parse_email,
        ...     error_prefix='Email address'
        ... )

    """

    def __init__(
        self,
        parser: Callable[[str], Maybe[object]],
        name: str | None = None,
        error_prefix: str | None = None,
    ) -> None:
        """Initialize the TyperParser.

        Args:
            parser: A valid8r parser function
            name: Custom name for the type (defaults to parser.__name__)
            error_prefix: Custom prefix for error messages

        """
        # Initialize parent Click ParamTypeAdapter
        super().__init__(parser, name=name, error_prefix=error_prefix)

        # Add __name__ attribute for Typer's FuncParamType compatibility
        # When Typer uses parser=TyperParser(...), it wraps it in FuncParamType
        # which expects a __name__ attribute
        self.__name__ = self.name

    def __call__(self, value: str, _param: click.Parameter | None = None, _ctx: click.Context | None = None) -> object:
        """Make TyperParser callable for use with Typer's parser parameter.

        When used as parser=TyperParser(...), Typer wraps this in a FuncParamType
        and calls it directly. We delegate to the convert method which handles
        the Maybe conversion and error handling.

        Args:
            value: The input string to parse
            _param: Optional Click Parameter (unused)
            _ctx: Optional Click Context (unused)

        Returns:
            The successfully parsed and validated value

        Raises:
            click.exceptions.BadParameter: If validation fails

        """
        return self.convert(value, None, None)


__all__ = ['TyperParser']
