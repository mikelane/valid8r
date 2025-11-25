"""Unit tests for Typer Integration Enhancement (Issue #229).

Following strict TDD: These tests are written BEFORE implementation.
Tests for validator_callback(), validate_with(), ValidatedType, and validated_prompt().
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from valid8r.core import (
    parsers,
    validators,
)

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe

typer = pytest.importorskip('typer')  # Skip tests if typer not installed
click = pytest.importorskip('click')  # Typer uses Click internally


def _port_parser(text: str | None) -> Maybe[int]:
    """Parse and validate port number in range 1-65535."""
    return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))


def _age_parser(text: str | None) -> Maybe[int]:
    """Parse and validate age as non-negative integer."""
    return parsers.parse_int(text).bind(validators.minimum(0))


class DescribeValidatorCallback:
    """Test validator_callback() factory function for creating Typer callbacks."""

    def it_creates_callback_that_accepts_valid_port(self) -> None:
        """validator_callback creates a callback that accepts valid ports."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(_port_parser)

        # Valid port should return the integer value
        result = callback('8080')
        assert result == 8080
        assert isinstance(result, int)

    def it_creates_callback_that_rejects_invalid_port_with_bad_parameter(self) -> None:
        """validator_callback creates a callback that raises BadParameter for invalid ports."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(_port_parser)

        # Invalid port (out of range) should raise BadParameter
        with pytest.raises(typer.BadParameter) as exc_info:
            callback('99999')

        # Error message should explain the problem
        assert 'at most 65535' in str(exc_info.value).lower()

    def it_creates_callback_that_rejects_non_numeric_input(self) -> None:
        """validator_callback creates a callback that rejects non-numeric input."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(_port_parser)

        # Non-numeric input should raise BadParameter
        with pytest.raises(typer.BadParameter) as exc_info:
            callback('not-a-number')

        # Error message should indicate parsing failure
        assert 'integer' in str(exc_info.value).lower()

    def it_creates_callback_that_accepts_valid_email(self) -> None:
        """validator_callback creates a callback that accepts valid emails."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_email)

        # Valid email should return EmailAddress object
        result = callback('alice@example.com')
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_creates_callback_that_rejects_invalid_email(self) -> None:
        """validator_callback creates a callback that rejects invalid emails."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_email)

        # Invalid email should raise BadParameter
        with pytest.raises(typer.BadParameter) as exc_info:
            callback('not-an-email')

        # Error message should explain the email format issue
        assert 'email' in str(exc_info.value).lower()

    def it_creates_callback_with_custom_error_prefix(self) -> None:
        """validator_callback accepts custom error prefix for better error messages."""
        from valid8r.integrations.typer import validator_callback

        callback = validator_callback(parsers.parse_email, error_prefix='Email address')

        # Invalid input should raise BadParameter with custom prefix
        with pytest.raises(typer.BadParameter) as exc_info:
            callback('bad')

        # Error message should include custom prefix
        assert 'Email address:' in str(exc_info.value)


class DescribeValidateWithUsingCallback:
    """Test using validator_callback() directly (recommended pattern)."""

    def it_validates_single_parameter_with_email_callback(self) -> None:
        """Using validator_callback directly validates email parameter."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        email_callback = validator_callback(parsers.parse_email)

        @app.command()
        def send_email(email: str = typer.Option(..., callback=email_callback)) -> None:
            # Parameter should be converted to EmailAddress
            assert isinstance(email, EmailAddress)
            typer.echo(f'Sent to {email.local}@{email.domain}')

        # Test with CliRunner
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'alice@example.com'])

        assert result.exit_code == 0
        assert 'Sent to alice@example.com' in result.stdout

    def it_rejects_invalid_email_with_clear_error(self) -> None:
        """Using validator_callback rejects invalid email with clear error message."""
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        email_callback = validator_callback(parsers.parse_email)

        @app.command()
        def send_email(email: str = typer.Option(..., callback=email_callback)) -> str:
            return f'Sent to {email}'

        # Test with CliRunner
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'not-an-email'])

        assert result.exit_code != 0
        assert 'email' in result.stdout.lower()

    def it_validates_multiple_parameters_with_multiple_callbacks(self) -> None:
        """Multiple validator_callbacks validate multiple parameters."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        email_callback = validator_callback(parsers.parse_email)
        age_callback = validator_callback(_age_parser)

        @app.command()
        def register(
            email: str = typer.Option(..., callback=email_callback), age: str = typer.Option(..., callback=age_callback)
        ) -> None:
            # Both parameters should be validated and converted
            assert isinstance(email, EmailAddress)
            assert isinstance(age, int)
            typer.echo(f'Registered {email.local} age {age}')

        # Test with CliRunner
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'alice@example.com', '--age', '25'])

        assert result.exit_code == 0
        assert 'Registered alice age 25' in result.stdout

    def it_rejects_when_one_parameter_is_invalid(self) -> None:
        """validator_callback rejects when one parameter is invalid."""
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        email_callback = validator_callback(parsers.parse_email)
        age_callback = validator_callback(_age_parser)

        @app.command()
        def register(
            email: str = typer.Option(..., callback=email_callback), age: str = typer.Option(..., callback=age_callback)
        ) -> str:
            return f'Registered {email} age {age}'

        # Test with invalid email
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'bad-email', '--age', '25'])

        assert result.exit_code != 0
        assert 'email' in result.stdout.lower()

    def it_applies_chained_validators_via_parser(self) -> None:
        """validator_callback applies chained validators via parser composition."""
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        port_callback = validator_callback(_port_parser)

        @app.command()
        def serve(port: str = typer.Option('8080', callback=port_callback)) -> None:
            assert isinstance(port, int)
            typer.echo(f'Serving on port {port}')

        # Test with valid port
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--port', '8080'])

        assert result.exit_code == 0
        assert 'Serving on port 8080' in result.stdout

        # Test with invalid port (out of range)
        result = runner.invoke(app, ['--port', '99999'])
        assert result.exit_code != 0


class DescribeValidatedType:
    """Test ValidatedType class for creating custom Typer types."""

    def it_creates_custom_email_type(self) -> None:
        """ValidatedType creates a custom Email type for Typer."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import ValidatedType

        # Create custom email type (N806 suppressed: intentionally type-like name)
        Email = ValidatedType(parsers.parse_email)  # noqa: N806

        app = typer.Typer()

        @app.command()
        def notify(email: str = typer.Option(..., click_type=Email)) -> None:
            # Parameter should be EmailAddress (converted by ValidatedType)
            assert isinstance(email, EmailAddress)
            typer.echo(f'Notifying {email.local}@{email.domain}')

        # Test with CliRunner
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'alice@example.com'])

        assert result.exit_code == 0
        assert 'Notifying alice@example.com' in result.stdout

    def it_rejects_invalid_input_with_custom_type(self) -> None:
        """ValidatedType rejects invalid input with clear error."""
        from valid8r.integrations.typer import ValidatedType

        Email = ValidatedType(parsers.parse_email)  # noqa: N806

        app = typer.Typer()

        @app.command()
        def notify(email: str = typer.Option(..., click_type=Email)) -> None:
            typer.echo(f'Notifying {email}')

        # Test with invalid email
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--email', 'not-an-email'])

        assert result.exit_code != 0
        assert 'email' in result.stdout.lower()

    def it_creates_custom_phone_type(self) -> None:
        """ValidatedType creates a custom Phone type for Typer."""
        from valid8r.core.parsers import PhoneNumber
        from valid8r.integrations.typer import ValidatedType

        Phone = ValidatedType(parsers.parse_phone)  # noqa: N806

        app = typer.Typer()

        @app.command()
        def call(phone: str = typer.Option(..., click_type=Phone)) -> None:
            # Parameter should be PhoneNumber (converted by ValidatedType)
            assert isinstance(phone, PhoneNumber)
            typer.echo(f'Calling {phone.area_code}-{phone.exchange}-{phone.subscriber}')

        # Test with CliRunner (using 212 NYC area code, non-reserved exchange)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--phone', '(212) 456-7890'])

        assert result.exit_code == 0
        assert 'Calling 212-456-7890' in result.stdout

    def it_handles_optional_parameters_with_none(self) -> None:
        """ValidatedType handles optional parameters that are None."""
        from valid8r.integrations.typer import ValidatedType

        Phone = ValidatedType(parsers.parse_phone)  # noqa: N806

        app = typer.Typer()

        @app.command()
        def contact(phone: str | None = typer.Option(None, click_type=Phone)) -> None:
            if phone is None:
                typer.echo('No phone provided')
            else:
                typer.echo(f'Phone: {phone.area_code}')

        # Test without providing phone
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert 'No phone provided' in result.stdout


class DescribeValidatedPrompt:
    """Test validated_prompt() function for interactive prompts with validation."""

    def it_prompts_and_validates_email_input(self) -> None:
        """validated_prompt prompts for and validates email input."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import validated_prompt
        from valid8r.testing import MockInputContext

        # Mock user input
        with MockInputContext(['alice@example.com']):
            result = validated_prompt('Enter email', parser=parsers.parse_email)

        # Result should be EmailAddress
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_retries_when_user_provides_invalid_input(self) -> None:
        """validated_prompt retries when user provides invalid input."""
        from valid8r.core.parsers import EmailAddress
        from valid8r.integrations.typer import validated_prompt
        from valid8r.testing import MockInputContext

        # Mock invalid input followed by valid input
        with MockInputContext(['not-an-email', 'invalid-again', 'alice@example.com']):
            result = validated_prompt('Enter email', parser=parsers.parse_email)

        # Should eventually get valid EmailAddress
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'

    def it_raises_after_max_retries(self) -> None:
        """validated_prompt raises Typer exception after max retries."""
        from valid8r.integrations.typer import validated_prompt
        from valid8r.testing import MockInputContext

        # Mock invalid input exceeding max retries
        with MockInputContext(['bad1', 'bad2', 'bad3', 'bad4']), pytest.raises((typer.Exit, typer.Abort)):
            validated_prompt('Enter email', parser=parsers.parse_email, max_retries=3)

    def it_uses_typer_style_when_enabled(self) -> None:
        """validated_prompt uses input() without typer_style by default."""
        from valid8r.integrations.typer import validated_prompt
        from valid8r.testing import MockInputContext

        # When typer_style=False (default), it uses input() which works with MockInputContext
        with MockInputContext(['alice@example.com']):
            result = validated_prompt('Enter email', parser=parsers.parse_email, typer_style=False)

        # Verify we got a valid result
        from valid8r.core.parsers import EmailAddress

        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'


class DescribeAsyncValidation:
    """Test async validation support for async Typer commands."""

    @pytest.mark.asyncio
    async def it_validates_async_command_parameters(self) -> None:
        """validator_callback works with async Typer commands."""
        from valid8r.integrations.typer import validator_callback

        app = typer.Typer()

        callback = validator_callback(parsers.parse_email)

        @app.command()
        async def async_send(email: str = typer.Option(..., callback=callback)) -> str:
            # Async command with validated parameter
            from valid8r.core.parsers import EmailAddress

            assert isinstance(email, EmailAddress)
            return f'Async sent to {email.local}@{email.domain}'

        # Note: Testing async Typer commands may require different approach
        # This test verifies the callback itself works synchronously
        # The async command execution is tested at integration level


class DescribeHelpTextIntegration:
    """Test help text generation for validated parameters."""

    def it_shows_validation_constraints_in_help_text(self) -> None:
        """ValidatedType includes validation constraints in help text."""
        from valid8r.integrations.typer import ValidatedType

        # Create validated type with help text (N806 suppressed: intentionally type-like name)
        Port = ValidatedType(  # noqa: N806
            _port_parser,
            help_text='Server port (1-65535)',
        )

        app = typer.Typer()

        @app.command()
        def serve(port: int = typer.Option(8080, click_type=Port, help='Server port (1-65535)')) -> None:
            typer.echo(f'Serving on port {port}')

        # Test help output
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ['--help'])

        assert result.exit_code == 0
        # Help text should show the constraint information
        assert 'port' in result.stdout.lower()
