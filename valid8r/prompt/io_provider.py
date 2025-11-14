"""IO provider interface for pluggable input/output in prompt functions.

This module defines the IOProvider protocol and standard implementations
for handling user interaction in prompt functions. By using a pluggable
provider, prompts can be tested without monkeypatching builtins, and
alternative UIs (TUI, GUI) can be easily integrated.
"""

from __future__ import annotations

from typing import (
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class IOProvider(Protocol):
    """Protocol for pluggable input/output in prompt functions.

    Implementations of this protocol can provide custom behavior for
    displaying prompts, collecting input, and showing error messages.
    This enables testing without mocking builtins and supports
    alternative UIs beyond command-line interfaces.

    Examples:
        >>> from valid8r.prompt.io_provider import BuiltinIOProvider
        >>> from valid8r.prompt.basic import ask
        >>> from valid8r.core.parsers import parse_int
        >>>
        >>> # Use default builtin provider
        >>> provider = BuiltinIOProvider()
        >>> result = ask("Age: ", parser=parse_int, io_provider=provider)
        >>>
        >>> # Use test provider for non-interactive testing
        >>> from valid8r.prompt.io_provider import TestIOProvider
        >>> test_provider = TestIOProvider(inputs=["25"])
        >>> result = ask("Age: ", parser=parse_int, io_provider=test_provider)
        >>> # result.value_or(0) == 25
        >>> # test_provider.outputs == []
        >>> # test_provider.errors == []

    """

    def input(self, prompt: str) -> str:
        """Display prompt and get user input.

        Args:
            prompt: The prompt message to display to the user

        Returns:
            str: The user's input as a string

        """
        ...

    def output(self, message: str) -> None:
        """Display an output message to the user.

        Args:
            message: The message to display

        """
        ...

    def error(self, message: str) -> None:
        """Display an error message to the user.

        Args:
            message: The error message to display

        """
        ...


class BuiltinIOProvider:
    """Default IO provider using Python builtins (input/print).

    This provider delegates to Python's built-in input() and print()
    functions, providing standard command-line interaction behavior.

    Examples:
        >>> from valid8r.prompt.io_provider import BuiltinIOProvider
        >>> provider = BuiltinIOProvider()
        >>>
        >>> # Input from user
        >>> user_input = provider.input("Name: ")  # Uses input()
        >>>
        >>> # Output to console
        >>> provider.output("Hello!")  # Uses print()
        >>>
        >>> # Error to console
        >>> provider.error("Invalid input")  # Uses print()

    """

    def input(self, prompt: str) -> str:
        """Display prompt using builtins.input.

        Args:
            prompt: The prompt message to display

        Returns:
            str: The user's input string

        """
        return input(prompt)

    def output(self, message: str) -> None:
        """Display output using builtins.print.

        Args:
            message: The message to display

        """
        print(message)

    def error(self, message: str) -> None:
        """Display error using builtins.print.

        Args:
            message: The error message to display

        """
        print(message)


class TestIOProvider:
    """IO provider for testing that captures I/O without builtins.

    This provider allows testing prompt functions without monkeypatching
    builtins.input and builtins.print. It provides pre-configured inputs
    and captures all outputs and errors for inspection.

    Attributes:
        inputs: List of input strings to return (consumed in order)
        outputs: List of captured output messages
        errors: List of captured error messages

    Examples:
        >>> from valid8r.prompt.io_provider import TestIOProvider
        >>> from valid8r.prompt.basic import ask
        >>> from valid8r.core.parsers import parse_int
        >>>
        >>> # Set up test provider with simulated inputs
        >>> provider = TestIOProvider(inputs=["42", "invalid", "25"])
        >>>
        >>> # First call returns "42"
        >>> result1 = ask("Age: ", parser=parse_int, io_provider=provider)
        >>> # result1.value_or(0) == 42
        >>>
        >>> # Second call with retry consumes "invalid" then "25"
        >>> result2 = ask("Age: ", parser=parse_int, retry=1, io_provider=provider)
        >>> # result2.value_or(0) == 25
        >>>
        >>> # Inspect captured output
        >>> len(provider.errors)  # 1 error for "invalid"
        1
        >>> len(provider.outputs)  # No outputs
        0

    """

    def __init__(self, inputs: list[str]) -> None:
        """Initialize test provider with simulated inputs.

        Args:
            inputs: List of input strings to return in sequence

        """
        self.inputs = list(inputs)  # Copy to avoid mutation
        self.outputs: list[str] = []
        self.errors: list[str] = []

    def input(self, prompt: str) -> str:  # noqa: ARG002
        """Return next simulated input.

        Args:
            prompt: The prompt message (ignored but required by protocol)

        Returns:
            str: Next input from the inputs list

        Raises:
            RuntimeError: If all inputs have been consumed

        """
        if not self.inputs:
            msg = 'No more test inputs available'
            raise RuntimeError(msg)
        return self.inputs.pop(0)

    def output(self, message: str) -> None:
        """Capture output message.

        Args:
            message: The output message to capture

        """
        self.outputs.append(message)

    def error(self, message: str) -> None:
        """Capture error message.

        Args:
            message: The error message to capture

        """
        self.errors.append(message)
