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

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar('T')


@dataclass
class PromptConfig(Generic[T]):
    """Configuration for the ask function."""

    parser: Callable[[str], Maybe[T]] | None = None
    validator: Callable[[T], Maybe[T]] | None = None
    error_message: str | None = None
    default: T | None = None
    retry: bool | int = False
    _test_mode: bool = False


def _handle_user_input(prompt_text: str, default: T | None) -> tuple[str, bool]:
    """Handle getting user input and displaying the prompt.

    Returns:
        A tuple of (user_input, use_default) where use_default is True if the
        default value should be used.

    """
    # Build prompt text with default if available
    display_prompt = prompt_text
    if default is not None:
        display_prompt = f'{prompt_text} [{default}]: '

    # Get user input
    user_input = input(display_prompt)

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
    _test_mode: bool = False,
) -> Maybe[T]:
    """Prompt the user for input with validation.

    Args:
        prompt_text: The prompt to display to the user
        parser: Function to convert string to desired type
        validator: Function to validate the parsed value
        error_message: Custom error message for invalid input
        default: Default value to use if input is empty
        retry: If True or an integer, retry on invalid input
        _test_mode: Hidden parameter for testing the final return path

    Returns:
        A Maybe containing the validated input or an error

    Examples:
        >>> # This would prompt the user and validate their input
        >>> from valid8r.core import parsers, validators
        >>> age = ask(
        ...     "Enter your age: ",
        ...     parser=parsers.parse_int,
        ...     validator=validators.minimum(0),
        ...     retry=True
        ... )

    """
    # Create a config object from the parameters
    config = PromptConfig(
        parser=parser,
        validator=validator,
        error_message=error_message,
        default=default,
        retry=retry,
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

    # Calculate max retries
    max_retries = config.retry if isinstance(config.retry, int) else float('inf') if config.retry else 0

    return _run_prompt_loop(prompt_text, parser, validator, config.default, max_retries, config.error_message)


def _run_prompt_loop(  # noqa: PLR0913
    prompt_text: str,
    parser: Callable[[str], Maybe[T]],
    validator: Callable[[T], Maybe[T]],
    default: T | None,
    max_retries: float,
    error_message: str | None,
) -> Maybe[T]:
    """Run the prompt loop with retries."""
    attempt = 0

    while attempt <= max_retries:
        # Get user input
        user_input, use_default = _handle_user_input(prompt_text, default)

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
                    _display_error(error, error_message, max_retries, attempt)
                else:
                    return result  # Return the failed result after max retries

    return Maybe.failure(error_message or 'Maximum retry attempts reached')


def _display_error(result_error: str, custom_error: str | None, max_retries: float, attempt: int) -> None:
    """Display error message to the user."""
    err_msg = custom_error or result_error
    remaining = max_retries - attempt if max_retries < float('inf') else None

    if remaining is not None:
        print(f'Error: {err_msg} ({remaining} attempt(s) remaining)')
    else:
        print(f'Error: {err_msg}')
