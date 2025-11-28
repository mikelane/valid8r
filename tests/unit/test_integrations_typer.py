"""Unit tests for valid8r.integrations.typer module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

typer = pytest.importorskip('typer')
click = pytest.importorskip('click')

from valid8r.core import (  # noqa: E402
    parsers,
    validators,
)

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe


class DescribeTyperParser:
    """Test TyperParser class for Typer integration."""

    def it_can_be_instantiated_with_a_parser(self) -> None:
        """Create a TyperParser with a valid8r parser."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int)
        assert adapter.name == 'parse_int'

    def it_has_dunder_name_attribute_for_typer_compatibility(self) -> None:
        """Expose __name__ attribute for Typer's FuncParamType."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_email, name='email')
        assert adapter.__name__ == 'email'

    def it_converts_valid_input_to_success_value(self) -> None:
        """Return the unwrapped value when parser succeeds."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int)

        class MockParam:
            name = '--value'

        class MockContext:
            command = None

        result = adapter.convert('42', MockParam(), MockContext())
        assert result == 42

    def it_raises_bad_parameter_for_invalid_input(self) -> None:
        """Raise BadParameter when parser fails."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int)

        class MockParam:
            name = '--value'

        class MockContext:
            command = None

        with pytest.raises(click.exceptions.BadParameter):
            adapter.convert('not a number', MockParam(), MockContext())

    def it_is_callable_for_typer_parser_parameter(self) -> None:
        """Work when used as parser=TyperParser(...)."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int)

        # TyperParser is callable and returns the converted value
        result = adapter('42')
        assert result == 42

    def it_raises_bad_parameter_when_called_directly_with_invalid_input(self) -> None:
        """Raise BadParameter when called directly with invalid input."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_email)

        with pytest.raises(click.exceptions.BadParameter):
            adapter('not-an-email')

    def it_works_with_email_parser(self) -> None:
        """Work correctly with parse_email parser."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_email)
        result = adapter('alice@example.com')

        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_supports_custom_name_parameter(self) -> None:
        """Use the custom name when provided."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int, name='port')
        assert adapter.name == 'port'
        assert adapter.__name__ == 'port'

    def it_supports_error_prefix_parameter(self) -> None:
        """Use the custom error prefix when provided."""
        from valid8r.integrations.typer import TyperParser

        adapter = TyperParser(parsers.parse_int, error_prefix='Port number')

        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            adapter('invalid')

        assert 'Port number' in str(exc_info.value)


class DescribeValidatorCallback:
    """Test validator_callback function."""

    def it_creates_callback_from_parser(self) -> None:
        """Create a callback function from a parser."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_int)

        result = callback('42')
        assert result == 42

    def it_raises_bad_parameter_on_failure(self) -> None:
        """Raise typer.BadParameter when validation fails."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_int)

        with pytest.raises(typer.BadParameter):
            callback('invalid')

    def it_chains_additional_validators(self) -> None:
        """Chain additional validators after parsing."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(
            parsers.parse_int,
            validators.minimum(1),
            validators.maximum(100),
        )

        # Valid value
        result = callback('50')
        assert result == 50

        # Invalid value (out of range)
        with pytest.raises(typer.BadParameter):
            callback('0')

    def it_uses_error_prefix_in_error_message(self) -> None:
        """Prepend error_prefix to error messages."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_int, error_prefix='Age')

        with pytest.raises(typer.BadParameter) as exc_info:
            callback('invalid')

        assert str(exc_info.value.message).startswith('Age')


class DescribeValidateWith:
    """Test validate_with decorator."""

    def it_returns_function_unchanged_when_param_not_found(self) -> None:
        """Return original function if parameter not in signature."""
        from valid8r.integrations.typer import validate_with

        @validate_with('nonexistent', parsers.parse_int)
        def my_func(value: str) -> str:
            return value

        # Function should work normally
        assert my_func('hello') == 'hello'

    def it_returns_function_unchanged_when_no_default(self) -> None:
        """Return original function if parameter has no default."""
        from valid8r.integrations.typer import validate_with

        @validate_with('value', parsers.parse_int)
        def my_func(value: str) -> str:
            return value

        # Function should work normally
        assert my_func('hello') == 'hello'

    def it_adds_callback_to_typer_option(self) -> None:
        """Add validation callback to typer.Option default."""
        from valid8r.integrations.typer import validate_with

        # Create mock typer.Option with callback attribute
        mock_option = mock.MagicMock()
        mock_option.callback = None

        @validate_with('port', parsers.parse_int)
        def my_func(port: str = mock_option) -> str:  # type: ignore[assignment]
            return port

        # The decorator should have set a callback
        assert mock_option.callback is not None

    def it_chains_with_existing_callback(self) -> None:
        """Chain our callback with an existing callback."""
        from valid8r.integrations.typer import validate_with

        def existing_callback(val: int) -> int:
            return val * 2

        mock_option = mock.MagicMock()
        mock_option.callback = existing_callback

        @validate_with('value', parsers.parse_int)
        def my_func(value: str = mock_option) -> str:  # type: ignore[assignment]
            return value

        # The callback should have been replaced with a chained version
        assert mock_option.callback is not existing_callback

    def it_preserves_function_metadata(self) -> None:
        """Preserve function name and docstring after decoration."""
        from valid8r.integrations.typer import validate_with

        @validate_with('nonexistent', parsers.parse_int)
        def documented_function(value: str) -> str:
            """Example docstring for testing."""
            return value

        assert documented_function.__name__ == 'documented_function'
        assert documented_function.__doc__ == 'Example docstring for testing.'


class DescribeValidatedType:
    """Test ValidatedType factory class."""

    def it_creates_typer_parser_from_parser(self) -> None:
        """Create a TyperParser via ValidatedType factory."""
        from valid8r.integrations.typer import (
            TyperParser,
            ValidatedType,
        )

        Email = ValidatedType(parsers.parse_email)  # noqa: N806

        # ValidatedType returns a TyperParser instance
        assert isinstance(Email, TyperParser)

    def it_supports_custom_name(self) -> None:
        """Support custom name parameter."""
        from valid8r.integrations.typer import ValidatedType

        Port = ValidatedType(parsers.parse_int, name='port')  # noqa: N806

        assert Port.name == 'port'

    def it_ignores_help_text_parameter(self) -> None:
        """Accept but ignore help_text parameter (reserved for future)."""
        from valid8r.integrations.typer import ValidatedType

        # Should not raise, even though help_text is not used
        Port = ValidatedType(parsers.parse_int, help_text='A valid port number')  # noqa: N806

        assert Port.name == 'parse_int'


class DescribeValidatedPrompt:
    """Test validated_prompt function."""

    def it_returns_validated_value_on_success(self) -> None:
        """Return the validated value on successful input."""
        from valid8r.integrations.typer import validated_prompt

        with mock.patch('builtins.input', return_value='42'):
            result = validated_prompt('Enter number', parsers.parse_int)

        assert result == 42

    def it_retries_on_invalid_input(self) -> None:
        """Retry when input is invalid."""
        from valid8r.integrations.typer import validated_prompt

        # First two attempts fail, third succeeds
        with (
            mock.patch('builtins.input', side_effect=['invalid', 'also invalid', '42']),
            mock.patch('builtins.print'),  # Suppress error output
        ):
            result = validated_prompt('Enter number', parsers.parse_int)

        assert result == 42

    def it_exits_after_max_retries(self) -> None:
        """Exit with code 1 after exceeding max_retries."""
        from valid8r.integrations.typer import validated_prompt

        with (
            mock.patch('builtins.input', return_value='invalid'),
            mock.patch('builtins.print'),  # Suppress error output
            pytest.raises(typer.Exit) as exc_info,
        ):
            validated_prompt('Enter number', parsers.parse_int, max_retries=2)

        assert exc_info.value.exit_code == 1

    def it_applies_additional_validators(self) -> None:
        """Apply additional validators after parsing."""
        from valid8r.integrations.typer import validated_prompt

        # First input valid parse but fails validator, second succeeds
        with (
            mock.patch('builtins.input', side_effect=['0', '50']),
            mock.patch('builtins.print'),  # Suppress error output
        ):
            result = validated_prompt(
                'Enter number',
                parsers.parse_int,
                validators.minimum(1),
            )

        assert result == 50

    def it_uses_typer_prompt_when_typer_style_is_true(self) -> None:
        """Use typer.prompt when typer_style=True."""
        from valid8r.integrations.typer import validated_prompt

        with mock.patch.object(typer, 'prompt', return_value='42') as mock_prompt:
            result = validated_prompt('Enter number', parsers.parse_int, typer_style=True)

        mock_prompt.assert_called_once_with('Enter number')
        assert result == 42

    def it_uses_typer_echo_for_errors_when_typer_style_is_true(self) -> None:
        """Use typer.echo for error messages when typer_style=True."""
        from valid8r.integrations.typer import validated_prompt

        with (
            mock.patch.object(typer, 'prompt', side_effect=['invalid', '42']),
            mock.patch.object(typer, 'echo') as mock_echo,
        ):
            result = validated_prompt('Enter number', parsers.parse_int, typer_style=True)

        # Echo should have been called with an error message
        mock_echo.assert_called()
        assert result == 42

    def it_uses_print_for_errors_when_typer_style_is_false(self) -> None:
        """Use print for error messages when typer_style=False."""
        from valid8r.integrations.typer import validated_prompt

        with (
            mock.patch('builtins.input', side_effect=['invalid', '42']),
            mock.patch('builtins.print') as mock_print,
        ):
            result = validated_prompt('Enter number', parsers.parse_int, typer_style=False)

        # Print should have been called with an error message
        mock_print.assert_called()
        assert result == 42


class DescribeTyperParserWithChainedValidators:
    """Test TyperParser with chained validators."""

    def it_works_with_chained_validators(self) -> None:
        """Work with parsers combined with validators."""
        from valid8r.integrations.typer import TyperParser

        def port_parser(value: str) -> Maybe[int]:
            return parsers.parse_int(value).bind(validators.minimum(1)).bind(validators.maximum(65535))

        adapter = TyperParser(port_parser, name='port')

        # Valid port
        result = adapter('8080')
        assert result == 8080

        # Invalid port (out of range)
        with pytest.raises(click.exceptions.BadParameter):
            adapter('0')
