"""Unit tests for Typer integration.

Following strict TDD: These tests are written BEFORE implementation.
"""

from __future__ import annotations

import ipaddress
import uuid

import pytest

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.core.parsers import (
    EmailAddress,
    PhoneNumber,
)

click = pytest.importorskip('click')  # Skip tests if click not installed


class DescribeTyperParser:
    """Test TyperParser class that wraps valid8r parsers for Typer CLI."""

    def it_can_be_instantiated_with_a_parser(self) -> None:
        """TyperParser can be created with a valid8r parser function."""
        from valid8r.integrations.typer import TyperParser

        # Create TyperParser with a simple parser
        typer_parser = TyperParser(parsers.parse_email)

        # Verify it was created successfully
        assert typer_parser is not None
        assert typer_parser.parser == parsers.parse_email

    def it_inherits_from_click_param_type_adapter(self) -> None:
        """TyperParser inherits from Click's ParamTypeAdapter."""
        from valid8r.integrations.click import ParamTypeAdapter
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Verify inheritance
        assert isinstance(typer_parser, ParamTypeAdapter)
        assert isinstance(typer_parser, click.ParamType)

    def it_converts_valid_email_to_email_address(self) -> None:
        """TyperParser converts valid email string to EmailAddress object."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Convert a valid email
        result = typer_parser.convert('alice@example.com', None, None)

        # Verify the result is an EmailAddress with correct components
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_raises_bad_parameter_for_invalid_email(self) -> None:
        """TyperParser raises BadParameter for invalid email."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Invalid email should raise BadParameter
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('not-an-email', None, None)

        # Verify error message mentions email
        assert 'email' in str(exc_info.value).lower()

    def it_converts_valid_phone_to_phone_number(self) -> None:
        """TyperParser converts valid phone string to PhoneNumber object."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_phone)

        # Convert a valid phone (using 212 NYC area code, non-reserved exchange)
        result = typer_parser.convert('(212) 456-7890', None, None)

        # Verify the result is a PhoneNumber with correct components
        assert isinstance(result, PhoneNumber)
        assert result.area_code == '212'
        assert result.exchange == '456'
        assert result.subscriber == '7890'

    def it_raises_bad_parameter_for_invalid_phone(self) -> None:
        """TyperParser raises BadParameter for invalid phone."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_phone)

        # Invalid phone should raise BadParameter
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('123', None, None)

        # Verify error message mentions phone
        assert 'phone' in str(exc_info.value).lower()

    def it_works_with_chained_validators(self) -> None:
        """TyperParser works with chained validators for complex validation."""
        from valid8r.core.maybe import Maybe  # noqa: TC001
        from valid8r.integrations.typer import TyperParser

        # Create a parser with chained validators (port: 1-65535)
        def port_parser(text: str | None) -> Maybe[int]:
            return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))

        typer_parser = TyperParser(port_parser)

        # Valid port should convert successfully
        result = typer_parser.convert('8080', None, None)
        assert result == 8080

        # Port 0 should fail (minimum 1)
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('0', None, None)
        assert 'at least 1' in str(exc_info.value).lower()

        # Port 70000 should fail (maximum 65535)
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('70000', None, None)
        assert 'at most 65535' in str(exc_info.value).lower()

    def it_converts_valid_uuid_to_uuid_object(self) -> None:
        """TyperParser converts valid UUID string to UUID object."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_uuid)

        # Convert a valid UUID
        result = typer_parser.convert('550e8400-e29b-41d4-a716-446655440000', None, None)

        # Verify the result is a UUID
        assert isinstance(result, uuid.UUID)
        assert str(result) == '550e8400-e29b-41d4-a716-446655440000'

    def it_raises_bad_parameter_for_invalid_uuid(self) -> None:
        """TyperParser raises BadParameter for invalid UUID."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_uuid)

        # Invalid UUID should raise BadParameter
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('not-a-uuid', None, None)

        # Verify error message mentions UUID
        assert 'uuid' in str(exc_info.value).lower()

    def it_converts_valid_ipv4_to_ipv4_address(self) -> None:
        """TyperParser converts valid IPv4 string to IPv4Address object."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_ipv4)

        # Convert a valid IPv4 address
        result = typer_parser.convert('192.168.1.1', None, None)

        # Verify the result is an IPv4Address
        assert isinstance(result, ipaddress.IPv4Address)
        assert str(result) == '192.168.1.1'

    def it_uses_custom_error_prefix_when_provided(self) -> None:
        """TyperParser prepends custom error prefix to error messages."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email, error_prefix='Email address')

        # Invalid email should raise BadParameter with custom prefix
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser.convert('bad', None, None)

        # Verify error message starts with custom prefix
        error_msg = str(exc_info.value)
        assert 'Email address:' in error_msg

    def it_uses_custom_name_when_provided(self) -> None:
        """TyperParser uses custom name instead of parser function name."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_int, name='port_number')

        # Verify the custom name is used
        assert typer_parser.name == 'port_number'

    def it_defaults_name_to_parser_function_name(self) -> None:
        """TyperParser defaults name to parser function name when not provided."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Verify the name defaults to parser function name
        assert typer_parser.name == 'parse_email'

    def it_is_callable_for_typer_parser_parameter(self) -> None:
        """TyperParser can be called directly when used with Typer's parser parameter."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Call directly (as Typer's FuncParamType would)
        result = typer_parser('alice@example.com')

        # Verify the result is an EmailAddress with correct components
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_raises_bad_parameter_when_called_with_invalid_input(self) -> None:
        """TyperParser raises BadParameter when called with invalid input."""
        from valid8r.integrations.typer import TyperParser

        typer_parser = TyperParser(parsers.parse_email)

        # Invalid email should raise BadParameter
        with pytest.raises(click.exceptions.BadParameter) as exc_info:
            typer_parser('not-an-email')

        # Verify error message mentions email
        assert 'email' in str(exc_info.value).lower()
