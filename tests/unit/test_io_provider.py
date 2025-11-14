"""Tests for the IO provider protocol and implementations.

This module tests the pluggable IO provider interface for prompt functions,
enabling custom input/output implementations for testing and alternative UIs.
"""

from __future__ import annotations

import pytest


class DescribeBuiltinIOProvider:
    """Tests for the default builtin IO provider."""

    def it_implements_io_provider_protocol(self) -> None:
        """BuiltinIOProvider implements the IOProvider protocol."""
        from valid8r.prompt.io_provider import (
            BuiltinIOProvider,
            IOProvider,
        )

        provider = BuiltinIOProvider()

        # Should have all protocol methods
        assert isinstance(provider, IOProvider)
        assert hasattr(provider, 'input')
        assert hasattr(provider, 'output')
        assert hasattr(provider, 'error')

    def it_delegates_input_to_builtin(self) -> None:
        """BuiltinIOProvider.input delegates to builtins.input."""
        from unittest.mock import patch

        from valid8r.prompt.io_provider import BuiltinIOProvider

        provider = BuiltinIOProvider()

        with patch('builtins.input', return_value='test input') as mock_input:
            result = provider.input('Enter value: ')

            mock_input.assert_called_once_with('Enter value: ')
            assert result == 'test input'

    def it_delegates_output_to_builtin_print(self) -> None:
        """BuiltinIOProvider.output delegates to builtins.print."""
        from unittest.mock import patch

        from valid8r.prompt.io_provider import BuiltinIOProvider

        provider = BuiltinIOProvider()

        with patch('builtins.print') as mock_print:
            provider.output('Test message')

            mock_print.assert_called_once_with('Test message')

    def it_delegates_error_to_builtin_print(self) -> None:
        """BuiltinIOProvider.error delegates to builtins.print."""
        from unittest.mock import patch

        from valid8r.prompt.io_provider import BuiltinIOProvider

        provider = BuiltinIOProvider()

        with patch('builtins.print') as mock_print:
            provider.error('Error message')

            mock_print.assert_called_once_with('Error message')


class DescribeTestIOProvider:
    """Tests for the test IO provider implementation."""

    def it_implements_io_provider_protocol(self) -> None:
        """TestIOProvider implements the IOProvider protocol."""
        from valid8r.prompt.io_provider import (
            IOProvider,
            TestIOProvider,
        )

        provider = TestIOProvider(inputs=['test'])

        # Should have all protocol methods
        assert isinstance(provider, IOProvider)
        assert hasattr(provider, 'input')
        assert hasattr(provider, 'output')
        assert hasattr(provider, 'error')

    def it_returns_inputs_in_sequence(self) -> None:
        """TestIOProvider.input returns inputs in sequence."""
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=['first', 'second', 'third'])

        assert provider.input('Prompt 1: ') == 'first'
        assert provider.input('Prompt 2: ') == 'second'
        assert provider.input('Prompt 3: ') == 'third'

    def it_raises_error_when_inputs_exhausted(self) -> None:
        """TestIOProvider.input raises error when inputs are exhausted."""
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=['only-one'])

        # First call succeeds
        assert provider.input('Prompt: ') == 'only-one'

        # Second call should raise
        with pytest.raises(RuntimeError, match='No more test inputs available'):
            provider.input('Prompt: ')

    def it_captures_output_messages(self) -> None:
        """TestIOProvider.output captures output messages."""
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=[])

        provider.output('Message 1')
        provider.output('Message 2')

        assert provider.outputs == ['Message 1', 'Message 2']

    def it_captures_error_messages(self) -> None:
        """TestIOProvider.error captures error messages."""
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=[])

        provider.error('Error 1')
        provider.error('Error 2')

        assert provider.errors == ['Error 1', 'Error 2']

    def it_allows_inspecting_captured_output(self) -> None:
        """TestIOProvider allows inspecting captured outputs and errors."""
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=['input1', 'input2'])

        # Simulate interaction
        provider.input('First: ')
        provider.output('Output 1')
        provider.error('Error 1')
        provider.input('Second: ')
        provider.output('Output 2')

        # Verify captured data
        assert provider.outputs == ['Output 1', 'Output 2']
        assert provider.errors == ['Error 1']
        assert len(provider.inputs) == 0  # Both consumed


class DescribePromptWithIOProvider:
    """Tests for prompt functions using IO providers."""

    def it_accepts_io_provider_parameter(self) -> None:
        """Accept an io_provider parameter in the ask function."""
        from valid8r.core.parsers import parse_int
        from valid8r.prompt.basic import ask
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=['42'])

        result = ask('Enter number: ', parser=parse_int, io_provider=provider)

        assert result.is_success()
        assert result.value_or(0) == 42

    def it_uses_builtin_provider_by_default(self) -> None:
        """Use BuiltinIOProvider when no provider specified."""
        from unittest.mock import patch

        from valid8r.core.parsers import parse_int
        from valid8r.prompt.basic import ask

        # Should use builtins.input when no provider specified
        with patch('builtins.input', return_value='42'):
            result = ask('Enter number: ', parser=parse_int)

            assert result.is_success()
            assert result.value_or(0) == 42

    def it_displays_errors_using_io_provider(self) -> None:
        """Error messages are displayed using the IO provider."""
        from valid8r.core.parsers import parse_int
        from valid8r.prompt.basic import ask
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=['invalid', '42'])

        result = ask('Enter number: ', parser=parse_int, retry=1, io_provider=provider)

        assert result.is_success()
        assert result.value_or(0) == 42
        # Should have displayed one error for the invalid input
        assert len(provider.errors) == 1
        assert 'valid integer' in provider.errors[0].lower()

    def it_displays_prompts_with_defaults_correctly(self) -> None:
        """Prompts with defaults are displayed correctly via IO provider."""
        from valid8r.core.parsers import parse_int
        from valid8r.prompt.basic import ask
        from valid8r.prompt.io_provider import TestIOProvider

        provider = TestIOProvider(inputs=[''])

        result = ask('Enter port: ', parser=parse_int, default=8080, io_provider=provider)

        assert result.is_success()
        assert result.value_or(0) == 8080
