"""Basic input prompting functions with validation support.

This module provides functionality for prompting users for input via the command line
with built-in parsing, validation, and retry logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    cast,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.prompt.io_provider import BuiltinIOProvider

if TYPE_CHECKING:
    from collections.abc import Callable

    from valid8r.prompt.io_provider import IOProvider

T = TypeVar('T')


@dataclass
class PromptConfig(Generic[T]):
    """Configuration for the ask function."""

    parser: Callable[[str], Maybe[T]] | None = None
    validator: Callable[[T], Maybe[T]] | None = None
    error_message: str | None = None
    default: T | None = None
    retry: bool | int = False
    io_provider: IOProvider | None = None
    _test_mode: bool = False


def _handle_user_input(prompt_text: str, default: T | None, io_provider: IOProvider) -> tuple[str, bool]:
    """Handle getting user input and displaying the prompt.

    Args:
        prompt_text: The prompt message to display
        default: Default value to use if user provides empty input
        io_provider: IO provider for handling input

    Returns:
        A tuple of (user_input, use_default) where use_default is True if the
        default value should be used.

    """
    # Build prompt text with default if available
    display_prompt = prompt_text
    if default is not None:
        display_prompt = f'{prompt_text} [{default}]: '

    # Get user input using the IO provider
    user_input = io_provider.input(display_prompt)

    # Check if we should use the default value
    use_default = not user_input and default is not None

    return user_input, use_default


def _process_input(user_input: str, parser: Callable[[str], Maybe[T]], validator: Callable[[T], Maybe[T]]) -> Maybe[T]:
    """Process user input by parsing and validating."""
    # Parse input
    result = parser(user_input)

    # Validate if parsing was successful
    match result:
        case Success(value):
            return validator(value)
        case Failure(_):
            return result

    return result  # This line is unreachable but keeps type checkers happy  pragma: no cover


def ask(  # noqa: PLR0913
    prompt_text: str,
    *,  # Force all other parameters to be keyword-only
    parser: Callable[[str], Maybe[T]] | None = None,
    validator: Callable[[T], Maybe[T]] | None = None,
    error_message: str | None = None,
    default: T | None = None,
    retry: bool | int = False,
    io_provider: IOProvider | None = None,
    _test_mode: bool = False,
) -> Maybe[T]:
    """Prompt the user for input with parsing and validation.

    Displays a prompt to the user, parses their input using the provided parser,
    validates the result, and optionally retries on failure. Returns a Maybe monad
    containing either the validated input or an error message.

    Args:
        prompt_text: The prompt message to display to the user
        parser: Function to convert string input to desired type (default: returns string as-is)
        validator: Function to validate the parsed value (default: accepts any value)
        error_message: Custom error message to display on validation failure
        default: Default value to use if user provides empty input (displays in prompt)
        retry: Enable retry on failure - True for unlimited, integer for max attempts, False to disable
        io_provider: IO provider for handling input/output (default: BuiltinIOProvider)
        _test_mode: Internal testing parameter (do not use)

    Returns:
        Maybe[T]: Success with validated input, or Failure with error message

    Examples:
        >>> from valid8r.core import parsers, validators
        >>> from valid8r.prompt import ask
        >>>
        >>> # Basic integer input with validation
        >>> result = ask(
        ...     "Enter your age: ",
        ...     parser=parsers.parse_int,
        ...     validator=validators.between(0, 120),
        ...     retry=True
        ... )
        >>> # User enters "25" -> Success(25)
        >>> # User enters "invalid" -> prompts again with error message
        >>>
        >>> # Input with default value
        >>> result = ask(
        ...     "Enter port: ",
        ...     parser=parsers.parse_int,
        ...     default=8080
        ... )
        >>> # User presses Enter -> Success(8080)
        >>> # User enters "3000" -> Success(3000)
        >>>
        >>> # Limited retries with custom error
        >>> result = ask(
        ...     "Email: ",
        ...     parser=parsers.parse_email,
        ...     error_message="Invalid email format",
        ...     retry=3
        ... )
        >>> # User has 3 attempts to enter valid email
        >>>
        >>> # Boolean input with retry
        >>> result = ask(
        ...     "Continue? (yes/no): ",
        ...     parser=parsers.parse_bool,
        ...     retry=True
        ... )
        >>> # User enters "yes" -> Success(True)
        >>> # User enters "maybe" -> error, retry prompt

    Note:
        The returned Maybe must be unwrapped to access the value.
        Use pattern matching or .value_or() to extract the result.

    """
    # Create a config object from the parameters
    config = PromptConfig(
        parser=parser,
        validator=validator,
        error_message=error_message,
        default=default,
        retry=retry,
        io_provider=io_provider,
        _test_mode=_test_mode,
    )

    return _ask_with_config(prompt_text, config)


def _ask_with_config(prompt_text: str, config: PromptConfig[T]) -> Maybe[T]:
    """Implement ask using a PromptConfig object."""
    # For testing the final return path
    if config._test_mode:  # noqa: SLF001
        return Maybe.failure(config.error_message or 'Maximum retry attempts reached')

    # Set default parser and validator if not provided
    def default_parser(s: str) -> Maybe[T]:
        return Maybe.success(cast('T', s))

    parser: Callable[[str], Maybe[T]] = config.parser if config.parser is not None else default_parser
    validator = config.validator or (lambda v: Maybe.success(v))

    # Get or create IO provider
    io_provider: IOProvider = config.io_provider if config.io_provider is not None else BuiltinIOProvider()

    # Calculate max retries
    max_retries = config.retry if isinstance(config.retry, int) else float('inf') if config.retry else 0

    return _run_prompt_loop(
        prompt_text, parser, validator, config.default, max_retries, config.error_message, io_provider
    )


def _run_prompt_loop(  # noqa: PLR0913
    prompt_text: str,
    parser: Callable[[str], Maybe[T]],
    validator: Callable[[T], Maybe[T]],
    default: T | None,
    max_retries: float,
    error_message: str | None,
    io_provider: IOProvider,
) -> Maybe[T]:
    """Run the prompt loop with retries.

    Args:
        prompt_text: The prompt message to display
        parser: Function to convert string input to desired type
        validator: Function to validate the parsed value
        default: Default value to use if user provides empty input
        max_retries: Maximum number of retry attempts
        error_message: Custom error message to display on validation failure
        io_provider: IO provider for handling input/output

    Returns:
        Maybe[T]: Success with validated input, or Failure with error message

    """
    attempt = 0

    while attempt <= max_retries:
        # Get user input
        user_input, use_default = _handle_user_input(prompt_text, default, io_provider)

        # Use default if requested
        if use_default:
            if default is None:
                return Maybe.failure('No default value provided')
            return Maybe.success(default)
        # Process the input
        result = _process_input(user_input, parser, validator)

        match result:
            case Success(_):
                return result
            case Failure(error):
                # Handle invalid input
                attempt += 1
                if attempt <= max_retries:
                    _display_error(error, error_message, max_retries, attempt, io_provider)
                else:
                    return result  # Return the failed result after max retries

    return Maybe.failure(error_message or 'Maximum retry attempts reached')


def _display_error(
    result_error: str,
    custom_error: str | None,
    max_retries: float,
    attempt: int,
    io_provider: IOProvider,
) -> None:
    """Display error message to the user.

    Args:
        result_error: The original error message from parsing/validation
        custom_error: Custom error message to display (overrides result_error)
        max_retries: Maximum number of retry attempts
        attempt: Current attempt number
        io_provider: IO provider for displaying the error

    """
    err_msg = custom_error or result_error
    remaining = max_retries - attempt if max_retries < float('inf') else None

    if remaining is not None:
        io_provider.error(f'Error: {err_msg} ({remaining} attempt(s) remaining)')
    else:
        io_provider.error(f'Error: {err_msg}')
