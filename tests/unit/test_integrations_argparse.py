"""Unit tests for argparse integration.

Following strict TDD: These tests are written BEFORE implementation.
"""

from __future__ import annotations

import argparse
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


class DescribeTypeFromParser:
    """Test type_from_parser function that converts valid8r parsers to argparse types."""

    def it_can_be_instantiated_with_a_parser(self) -> None:
        """type_from_parser creates an argparse type function from a valid8r parser."""
        from valid8r.integrations.argparse import type_from_parser

        # Create argparse type from a simple parser
        argparse_type = type_from_parser(parsers.parse_email)

        # Verify it was created successfully and is callable
        assert argparse_type is not None
        assert callable(argparse_type)

    def it_converts_valid_email_to_email_address(self) -> None:
        """type_from_parser returns EmailAddress for valid email input."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_email)

        # Convert a valid email
        result = argparse_type('alice@example.com')

        # Verify the result is an EmailAddress with correct components
        assert isinstance(result, EmailAddress)
        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_raises_value_error_for_invalid_email(self) -> None:
        """type_from_parser raises ValueError for invalid email."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_email)

        # Invalid email should raise ValueError
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('not-an-email')

        # Verify error message mentions email
        assert 'email' in str(exc_info.value).lower()

    def it_converts_valid_phone_to_phone_number(self) -> None:
        """type_from_parser returns PhoneNumber for valid phone input."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_phone)

        # Convert a valid phone (using 212 NYC area code, non-reserved exchange)
        result = argparse_type('(212) 456-7890')

        # Verify the result is a PhoneNumber with correct components
        assert isinstance(result, PhoneNumber)
        assert result.area_code == '212'
        assert result.exchange == '456'
        assert result.subscriber == '7890'

    def it_raises_value_error_for_invalid_phone(self) -> None:
        """type_from_parser raises ValueError for invalid phone."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_phone)

        # Invalid phone should raise ValueError
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('123')

        # Verify error message mentions phone
        assert 'phone' in str(exc_info.value).lower()

    def it_works_with_chained_validators(self) -> None:
        """type_from_parser works with chained validators for complex validation."""
        from valid8r.core.maybe import Maybe  # noqa: TC001
        from valid8r.integrations.argparse import type_from_parser

        # Create a parser with chained validators (port: 1-65535)
        def port_parser(text: str | None) -> Maybe[int]:
            return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))

        argparse_type = type_from_parser(port_parser)

        # Valid port should convert successfully
        result = argparse_type('8080')
        assert result == 8080

        # Port 0 should fail (minimum 1)
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('0')
        assert 'at least 1' in str(exc_info.value).lower()

        # Port 70000 should fail (maximum 65535)
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('70000')
        assert 'at most 65535' in str(exc_info.value).lower()

    def it_converts_valid_uuid_to_uuid_object(self) -> None:
        """type_from_parser returns UUID for valid UUID input."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_uuid)

        # Convert a valid UUID
        result = argparse_type('550e8400-e29b-41d4-a716-446655440000')

        # Verify the result is a UUID
        assert isinstance(result, uuid.UUID)
        assert str(result) == '550e8400-e29b-41d4-a716-446655440000'

    def it_raises_value_error_for_invalid_uuid(self) -> None:
        """type_from_parser raises ValueError for invalid UUID."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_uuid)

        # Invalid UUID should raise ValueError
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('not-a-uuid')

        # Verify error message mentions UUID
        assert 'uuid' in str(exc_info.value).lower()

    def it_converts_valid_ipv4_to_ipv4_address(self) -> None:
        """type_from_parser returns IPv4Address for valid IPv4 input."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_ipv4)

        # Convert a valid IPv4 address
        result = argparse_type('192.168.1.1')

        # Verify the result is an IPv4Address
        assert isinstance(result, ipaddress.IPv4Address)
        assert str(result) == '192.168.1.1'

    def it_converts_valid_integer_to_int(self) -> None:
        """type_from_parser returns int for valid integer input."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_int)

        # Convert valid integers
        assert argparse_type('42') == 42
        assert argparse_type('0') == 0
        assert argparse_type('-1') == -1

    def it_raises_value_error_for_invalid_integer(self) -> None:
        """type_from_parser raises ValueError for invalid integer."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_int)

        # Invalid integer should raise ValueError
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('not-a-number')

        # Verify error message is helpful
        assert 'integer' in str(exc_info.value).lower()

    def it_works_with_parse_bool(self) -> None:
        """type_from_parser works with parse_bool for boolean values."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_bool)

        # Valid boolean values
        assert argparse_type('true') is True
        assert argparse_type('yes') is True
        assert argparse_type('1') is True
        assert argparse_type('false') is False
        assert argparse_type('no') is False
        assert argparse_type('0') is False

    def it_raises_value_error_for_invalid_bool(self) -> None:
        """type_from_parser raises ValueError for invalid boolean."""
        from valid8r.integrations.argparse import type_from_parser

        argparse_type = type_from_parser(parsers.parse_bool)

        # Invalid boolean should raise ValueError
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            argparse_type('maybe')

        # Verify error message is helpful
        error_msg = str(exc_info.value).lower()
        assert 'boolean' in error_msg or 'bool' in error_msg


class DescribeArgparseIntegration:
    """Integration tests with real ArgumentParser."""

    def it_works_with_argument_parser_email_option(self) -> None:
        """type_from_parser works with ArgumentParser for email validation."""
        from valid8r.integrations.argparse import type_from_parser

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--email',
            type=type_from_parser(parsers.parse_email),
            help='Email address',
        )

        # Parse valid email
        args = parser.parse_args(['--email', 'alice@example.com'])
        assert isinstance(args.email, EmailAddress)
        assert args.email.local == 'alice'
        assert args.email.domain == 'example.com'

    def it_shows_helpful_error_for_invalid_email_option(self) -> None:
        """ArgumentParser shows helpful error for invalid email."""
        from valid8r.integrations.argparse import type_from_parser

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--email',
            type=type_from_parser(parsers.parse_email),
            help='Email address',
        )

        # Parse invalid email should raise SystemExit (argparse's error behavior)
        with pytest.raises(SystemExit):
            parser.parse_args(['--email', 'not-an-email'])

    def it_works_with_port_validation(self) -> None:
        """type_from_parser works with port range validation."""
        from valid8r.core.maybe import Maybe  # noqa: TC001
        from valid8r.integrations.argparse import type_from_parser

        def port_parser(text: str | None) -> Maybe[int]:
            return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--port',
            type=type_from_parser(port_parser),
            help='Port number (1-65535)',
        )

        # Parse valid port
        args = parser.parse_args(['--port', '8080'])
        assert args.port == 8080

    def it_shows_helpful_error_for_invalid_port(self) -> None:
        """ArgumentParser shows helpful error for invalid port."""
        from valid8r.core.maybe import Maybe  # noqa: TC001
        from valid8r.integrations.argparse import type_from_parser

        def port_parser(text: str | None) -> Maybe[int]:
            return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--port',
            type=type_from_parser(port_parser),
            help='Port number (1-65535)',
        )

        # Parse invalid port should raise SystemExit
        with pytest.raises(SystemExit):
            parser.parse_args(['--port', '70000'])

    def it_works_with_positional_arguments(self) -> None:
        """type_from_parser works with positional arguments."""
        from valid8r.integrations.argparse import type_from_parser

        parser = argparse.ArgumentParser()
        parser.add_argument(
            'email',
            type=type_from_parser(parsers.parse_email),
            help='Email address',
        )

        # Parse valid email as positional argument
        args = parser.parse_args(['alice@example.com'])
        assert isinstance(args.email, EmailAddress)
        assert args.email.local == 'alice'

    def it_works_with_multiple_arguments(self) -> None:
        """type_from_parser works with multiple arguments of different types."""
        from valid8r.core.maybe import Maybe  # noqa: TC001
        from valid8r.integrations.argparse import type_from_parser

        def port_parser(text: str | None) -> Maybe[int]:
            return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--email',
            type=type_from_parser(parsers.parse_email),
            help='Email address',
        )
        parser.add_argument(
            '--port',
            type=type_from_parser(port_parser),
            help='Port number',
        )
        parser.add_argument(
            '--uuid',
            type=type_from_parser(parsers.parse_uuid),
            help='UUID',
        )

        # Parse multiple arguments
        args = parser.parse_args(
            [
                '--email',
                'alice@example.com',
                '--port',
                '8080',
                '--uuid',
                '550e8400-e29b-41d4-a716-446655440000',
            ]
        )

        assert isinstance(args.email, EmailAddress)
        assert args.port == 8080
        assert isinstance(args.uuid, uuid.UUID)

    def it_works_with_optional_arguments_with_defaults(self) -> None:
        """type_from_parser works with optional arguments that have defaults."""
        from valid8r.integrations.argparse import type_from_parser

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--port',
            type=type_from_parser(parsers.parse_int),
            default=8080,
            help='Port number',
        )

        # Parse without providing the argument
        args = parser.parse_args([])
        assert args.port == 8080

        # Parse with the argument
        args = parser.parse_args(['--port', '9000'])
        assert args.port == 9000
