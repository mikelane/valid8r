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

import functools
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
)

import typer

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.integrations.click import ParamTypeAdapter

if TYPE_CHECKING:
    from collections.abc import Callable

    import click


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

    def __call__(self, value: str, param: click.Parameter | None = None, ctx: click.Context | None = None) -> object:
        """Make TyperParser callable for use with Typer's parser parameter.

        When used as parser=TyperParser(...), Typer wraps this in a FuncParamType
        and calls it directly. We delegate to the convert method which handles
        the Maybe conversion and error handling.

        Args:
            value: The input string to parse
            param: Optional Click Parameter (can be named param or _param)
            ctx: Optional Click Context (can be named ctx or _ctx)

        Returns:
            The successfully parsed and validated value

        Raises:
            click.exceptions.BadParameter: If validation fails

        """
        return self.convert(value, param, ctx)


def validator_callback(
    parser: Callable[[str | None], Maybe[object]],
    *validators: Callable[[object], Maybe[object]],
    error_prefix: str | None = None,
) -> Callable[[str], object]:
    """Create a Typer callback function from a valid8r parser and optional validators.

    This factory function creates a callback that can be used with Typer's Option() or
    Argument() callback parameter. The callback will parse and validate the input,
    returning the validated value or raising typer.BadParameter on failure.

    Args:
        parser: A valid8r parser function that returns Maybe[T]
        *validators: Optional validator functions to chain after parsing
        error_prefix: Optional prefix for error messages (e.g., "Port number")

    Returns:
        A callback function compatible with Typer's callback parameter

    Examples:
        >>> from valid8r.core import parsers, validators
        >>> from valid8r.integrations.typer import validator_callback
        >>> import typer
        >>>
        >>> # Simple email validation
        >>> email_callback = validator_callback(parsers.parse_email)
        >>>
        >>> # Port validation with range checking
        >>> def port_parser(text: str | None):
        ...     return parsers.parse_int(text).bind(
        ...         validators.minimum(1) & validators.maximum(65535)
        ...     )
        >>> port_callback = validator_callback(port_parser)
        >>>
        >>> # Use in Typer command
        >>> app = typer.Typer()
        >>> @app.command()
        ... def serve(
        ...     port: int = typer.Option(8000, callback=port_callback)
        ... ) -> None:
        ...     print(f"Serving on port {port}")

    """

    def callback(value: str) -> object:
        """Validate using valid8r parser and return result or raise BadParameter."""
        # Parse the input
        result = parser(value)

        # Apply any additional validators
        for validator in validators:
            result = result.bind(validator)

        # Convert Maybe result to Typer exception or return value
        match result:
            case Success(val):
                return val
            case Failure(err):
                # Prepend error prefix if provided
                error_msg = f'{error_prefix}: {err}' if error_prefix else err
                raise typer.BadParameter(error_msg)

        # Unreachable but satisfies type checker
        msg = 'Unexpected Maybe variant'
        raise RuntimeError(msg)

    return callback


def validate_with(
    param_name: str,
    parser: Callable[[str | None], Maybe[object]],
    *validators: Callable[[object], Maybe[object]],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Add validation to a Typer command parameter.

    This decorator modifies a Typer command to use a validator callback for
    a specific parameter. The validated/converted value replaces the original
    string parameter before the command executes.

    Note: This decorator should be applied BEFORE @app.command() so that
    Typer sees the modified default values with callbacks attached.

    Args:
        param_name: Name of the parameter to validate
        parser: A valid8r parser function that returns Maybe[T]
        *validators: Optional validator functions to chain after parsing

    Returns:
        A decorator function that modifies the Typer command

    Examples:
        >>> from valid8r.core import parsers, validators
        >>> from valid8r.integrations.typer import validate_with
        >>> import typer
        >>>
        >>> app = typer.Typer()
        >>>
        >>> @app.command()
        ... @validate_with('email', parsers.parse_email)
        ... def send(email: str = typer.Option(...)) -> None:
        ...     # email is now an EmailAddress object
        ...     print(f"Sending to {email.local}@{email.domain}")
        >>>
        >>> @app.command()
        ... @validate_with('email', parsers.parse_email)
        ... @validate_with('age', parsers.parse_int, validators.minimum(0))
        ... def register(
        ...     email: str = typer.Option(...),
        ...     age: str = typer.Option(...)
        ... ) -> None:
        ...     # Both parameters are validated
        ...     print(f"Registered {email.local}, age {age}")

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Modify the function to add parameter validation via callback."""
        # Create a validator callback for this parameter
        callback = validator_callback(parser, *validators)

        # Get the function's signature
        sig = inspect.signature(func)

        # Find the parameter
        if param_name not in sig.parameters:
            # Parameter doesn't exist, just return the function
            return func

        param = sig.parameters[param_name]

        # Check if parameter has a default that's a typer.Option or typer.Argument
        if param.default is inspect.Parameter.empty:
            # No default, can't add callback
            return func

        # Modify the default to add our callback
        if hasattr(param.default, 'callback'):
            # It's a typer.Option or typer.Argument, add our callback
            old_callback = param.default.callback

            # Chain callbacks if one already exists
            if old_callback is not None:

                def chained_callback(value: str) -> object:
                    """Chain our validator with existing callback."""
                    result = callback(value)
                    return old_callback(result)

                param.default.callback = chained_callback
            else:
                param.default.callback = callback

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            """Preserve function signature and forward call."""
            return func(*args, **kwargs)

        return wrapper

    return decorator


class ValidatedType:
    """Create a custom Typer type with valid8r validation.

    This class wraps a valid8r parser into a Click ParamType that can be used
    with Typer's type annotations. It provides a cleaner alternative to using
    TyperParser directly in type hints.

    Args:
        parser: A valid8r parser function that returns Maybe[T]
        name: Optional custom name for the type
        help_text: Optional help text describing validation constraints (reserved for future use)

    Examples:
        >>> from valid8r.core import parsers
        >>> from valid8r.integrations.typer import ValidatedType
        >>> import typer
        >>>
        >>> # Create custom types
        >>> Email = ValidatedType(parsers.parse_email)
        >>> Phone = ValidatedType(parsers.parse_phone)
        >>>
        >>> app = typer.Typer()
        >>>
        >>> @app.command()
        ... def contact(
        ...     email: Email = typer.Option(...),  # type: ignore[valid-type]
        ...     phone: Phone = typer.Option(None)   # type: ignore[valid-type]
        ... ) -> None:
        ...     # email is EmailAddress, phone is Optional[PhoneNumber]
        ...     print(f"Contact: {email.local}@{email.domain}")

    """

    def __new__(  # type: ignore[misc]
        cls,
        parser: Callable[[str | None], Maybe[object]],
        name: str | None = None,
        help_text: str | None = None,  # noqa: ARG004
    ) -> TyperParser:
        """Create a new ValidatedType instance as a TyperParser.

        This uses __new__ to return a TyperParser instance directly,
        making ValidatedType a factory for TyperParser with different semantics.

        Args:
            parser: A valid8r parser function that returns Maybe[T]
            name: Optional custom name for the type
            help_text: Reserved for future help text integration

        Returns:
            A TyperParser instance configured with the given parser

        Note:
            The type: ignore[misc] is intentional - this class uses __new__ as a
            factory pattern to return a TyperParser instead of a ValidatedType.

        """
        return TyperParser(parser, name=name, error_prefix=None)


def validated_prompt(
    prompt_text: str,
    parser: Callable[[str | None], Maybe[object]],
    *validators: Callable[[object], Maybe[object]],
    max_retries: int = 10,
    typer_style: bool = False,
) -> object:
    """Prompt interactively with valid8r validation and retry logic.

    This function prompts the user for input, validates it using a valid8r parser
    and optional validators, and re-prompts on validation failure up to max_retries.
    After max_retries, it raises a Typer exception to exit the CLI.

    Args:
        prompt_text: The prompt message to display
        parser: A valid8r parser function that returns Maybe[T]
        *validators: Optional validator functions to chain after parsing
        max_retries: Maximum number of retry attempts (default: 10)
        typer_style: Whether to use Typer's echo/style for output (default: False)

    Returns:
        The validated and parsed value

    Raises:
        typer.Exit: If max_retries is exceeded without valid input

    Examples:
        >>> from valid8r.core import parsers
        >>> from valid8r.integrations.typer import validated_prompt
        >>> import typer
        >>>
        >>> app = typer.Typer()
        >>>
        >>> @app.command()
        ... def interactive() -> None:
        ...     email = validated_prompt(
        ...         "Enter email",
        ...         parser=parsers.parse_email,
        ...         typer_style=True
        ...     )
        ...     print(f"Got email: {email.local}@{email.domain}")

    """

    def _report_error(msg: str) -> None:
        """Report error using appropriate output method."""
        if typer_style:
            typer.echo(f'Error: {msg}', err=True)
        else:
            print(f'Error: {msg}')

    attempts = 0
    while attempts < max_retries:
        # Prompt for input using appropriate method
        user_input = typer.prompt(prompt_text) if typer_style else input(f'{prompt_text}: ')

        # Parse and validate
        result = parser(user_input)
        for validator in validators:
            result = result.bind(validator)

        # Check result
        match result:
            case Success(val):
                return val
            case Failure(err):
                _report_error(err)
                attempts += 1

    # Max retries exceeded
    _report_error(f'Max retries ({max_retries}) exceeded')
    raise typer.Exit(code=1)


__all__ = [
    'TyperParser',
    'ValidatedType',
    'validate_with',
    'validated_prompt',
    'validator_callback',
]
