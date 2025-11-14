"""Example demonstrating pluggable IO providers for prompt functions.

This example shows how to use the IOProvider protocol to:
1. Test prompt functions without monkeypatching builtins
2. Create custom IO providers for alternative UIs
3. Capture and inspect user interaction for testing

Run this example:
    python examples/io_provider_example.py
"""

from __future__ import annotations

from valid8r.core.parsers import parse_int
from valid8r.core.validators import between
from valid8r.prompt import (
    TestIOProvider,
    ask,
)


def example_test_provider() -> None:
    """Use TestIOProvider for non-interactive testing."""
    print('\n=== Example 1: TestIOProvider for Testing ===')

    # Set up test inputs
    test_provider = TestIOProvider(inputs=['42', 'invalid', '25'])

    # First prompt: successful input
    result1 = ask('Enter age: ', parser=parse_int, io_provider=test_provider)
    print(f'Result 1: {result1.value_or("failed")}')  # 42

    # Second prompt: retry with invalid then valid input
    result2 = ask('Enter age: ', parser=parse_int, retry=1, io_provider=test_provider)
    print(f'Result 2: {result2.value_or("failed")}')  # 25

    # Inspect captured errors
    print(f'Errors captured: {test_provider.errors}')
    print(f'Outputs captured: {test_provider.outputs}')


def example_custom_provider() -> None:
    """Create a custom IO provider for a TUI."""
    print('\n=== Example 2: Custom IO Provider ===')

    class LoggingIOProvider:
        """Custom IO provider that logs all interactions."""

        def __init__(self) -> None:
            self.log: list[str] = []

        def input(self, prompt: str) -> str:
            """Get input and log the prompt."""
            self.log.append(f'PROMPT: {prompt}')
            # Simulate user input
            value = '42'
            self.log.append(f'INPUT: {value}')
            return value

        def output(self, message: str) -> None:
            """Display output and log it."""
            self.log.append(f'OUTPUT: {message}')
            print(message)

        def error(self, message: str) -> None:
            """Display error and log it."""
            self.log.append(f'ERROR: {message}')
            print(f'[ERROR] {message}')

    # Use the custom provider
    logging_provider = LoggingIOProvider()
    result = ask('Enter value: ', parser=parse_int, io_provider=logging_provider)

    print(f'Result: {result.value_or("failed")}')
    print('\nInteraction log:')
    for entry in logging_provider.log:
        print(f'  {entry}')


def example_default_provider() -> None:
    """Use default BuiltinIOProvider for normal CLI behavior."""
    print('\n=== Example 3: Default BuiltinIOProvider ===')
    print('This example would normally prompt for user input.')
    print('Skipping interactive example...')
    print('When no provider specified, BuiltinIOProvider is used automatically')


def example_testing_with_validation() -> None:
    """Test prompts with validation and retries."""
    print('\n=== Example 4: Testing with Validation ===')

    # Create test provider with multiple attempts
    test_provider = TestIOProvider(inputs=['150', '25'])

    # Prompt with validation (age between 0 and 120)
    result = ask(
        'Enter age: ',
        parser=parse_int,
        validator=between(0, 120),
        retry=1,
        io_provider=test_provider,
    )

    print(f'Result: {result.value_or("failed")}')  # 25 (after one retry)
    print(f'Errors: {test_provider.errors}')  # ['Error: ...']


def main() -> None:
    """Run all examples."""
    print('Pluggable IO Provider Examples')
    print('=' * 50)

    example_test_provider()
    example_custom_provider()
    example_default_provider()
    example_testing_with_validation()

    print('\n' + '=' * 50)
    print('Examples complete!')


if __name__ == '__main__':
    main()
