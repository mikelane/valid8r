"""Utilities for mocking user input during tests."""

from __future__ import annotations

import builtins
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# Store the original input function
_original_input = builtins.input


@contextmanager
def MockInputContext(inputs: list[str] | None = None) -> Iterator[None]:  # noqa: N802
    """Context manager for mocking user input.

    Args:
        inputs: A list of strings to be returned sequentially by input().

    Yields:
        None

    Examples:
        >>> with MockInputContext(["yes", "42"]):
        ...     answer = input("Continue? ")  # returns "yes"
        ...     number = input("Enter number: ")  # returns "42"

    """
    input_values = [] if inputs is None else list(inputs)

    def mock_input(prompt: object = '') -> str:  # noqa: ARG001
        """Mock implementation of input function.

        Args:
            prompt: The input prompt (ignored in mock)

        Returns:
            The next string from the predefined inputs list

        Raises:
            IndexError: If there are no more inputs available

        """
        if not input_values:
            raise IndexError('No more mock inputs available')
        return input_values.pop(0)

    # Replace the builtin input function
    builtins.input = mock_input

    try:
        yield
    finally:
        # Restore the original input function
        builtins.input = _original_input


def configure_mock_input(inputs: list[str]) -> None:
    """Configure input to be mocked globally.

    Unlike MockInputContext, this function replaces the input function
    globally without restoring it automatically. Use for simple tests
    where cleanup isn't critical.

    Args:
        inputs: A list of strings to be returned sequentially by input().

    Examples:
        >>> configure_mock_input(["yes", "42"])
        >>> answer = input("Continue? ")  # returns "yes"
        >>> number = input("Enter number: ")  # returns "42"

    """
    input_values = list(inputs)  # Create a copy

    def mock_input(prompt: object = '') -> str:  # noqa: ARG001
        if not input_values:
            raise IndexError('No more mock inputs available')
        return input_values.pop(0)

    builtins.input = mock_input
