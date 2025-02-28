from __future__ import annotations

import ipaddress
from enum import Enum

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    ParserRegistry,
    parse_int,
)


class Color(Enum):
    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'


class DescribeParserRegistry:
    def it_registers_and_retrieves_parsers(self):
        """Test that parsers can be registered and retrieved."""

        # Define a custom parser
        def parse_ip_address(input_value: str) -> Maybe[ipaddress.IPv4Address]:
            try:
                return Maybe.success(ipaddress.IPv4Address(input_value))
            except ValueError:
                return Maybe.failure('Invalid IP address')

        # Register the parser
        ParserRegistry.register(ipaddress.IPv4Address, parse_ip_address)

        # Get the parser
        parser = ParserRegistry.get_parser(ipaddress.IPv4Address)
        assert parser is not None

        # Test the parser
        result = parser('192.168.1.1')
        assert result.is_success()
        assert str(result.value_or('TEST')) == '192.168.1.1'

        # Clean up
        ParserRegistry._parsers.pop(ipaddress.IPv4Address, None)

    def it_parses_with_registered_parser(self):
        """Test that ParserRegistry.parse uses the registered parser."""

        # Define a custom parser
        def parse_ip_address(input_value: str) -> Maybe[ipaddress.IPv4Address]:
            try:
                return Maybe.success(ipaddress.IPv4Address(input_value))
            except ValueError:
                return Maybe.failure('Invalid IP address')

        # Register the parser
        ParserRegistry.register(ipaddress.IPv4Address, parse_ip_address)

        # Test parsing
        result = ParserRegistry.parse('192.168.1.1', ipaddress.IPv4Address)
        assert result.is_success()
        assert str(result.value_or('TEST')) == '192.168.1.1'

        # Clean up
        ParserRegistry._parsers.pop(ipaddress.IPv4Address, None)

    def it_returns_none_for_unknown_types(self):
        """Test that get_parser returns None for unknown types."""

        class UnknownType:
            pass

        parser = ParserRegistry.get_parser(UnknownType)
        assert parser is None

    def it_fails_parsing_for_unknown_types(self):
        """Test that parse fails for unknown types."""

        class UnknownType:
            pass

        result = ParserRegistry.parse('anything', UnknownType)
        assert result.is_failure()
        assert 'No parser found for type' in result.value_or('TEST')

    def it_supports_inheritance(self):
        """Test that parsers can be inherited from parent classes."""

        # Define parent and child classes
        class Animal:
            pass

        class Dog(Animal):
            pass

        # Define and register a parser for the parent class
        def parse_animal(input_value: str) -> Maybe[Animal]:
            return Maybe.success(Animal())

        ParserRegistry.register(Animal, parse_animal)

        # Get the parser for the child class
        parser = ParserRegistry.get_parser(Dog)
        assert parser is not None

        # Test the parser
        result = parser('anything')
        assert result.is_success()
        assert isinstance(result.value_or(None), Animal)

        # Clean up
        ParserRegistry._parsers.pop(Animal, None)

    def it_registers_default_parsers(self):
        """Test that default parsers are registered for built-in types."""
        # Clear existing parsers
        old_parsers = ParserRegistry._parsers.copy()
        ParserRegistry._parsers.clear()

        # Register default parsers
        ParserRegistry.register_defaults()

        # Check default parsers
        assert ParserRegistry.get_parser(int) is not None
        assert ParserRegistry.get_parser(float) is not None
        assert ParserRegistry.get_parser(bool) is not None
        assert ParserRegistry.get_parser(complex) is not None
        assert ParserRegistry.get_parser(str) is not None
        assert ParserRegistry.get_parser(list) is not None
        assert ParserRegistry.get_parser(dict) is not None
        assert ParserRegistry.get_parser(set) is not None

        # Test parsing with default parsers
        result = ParserRegistry.parse('123', int)
        assert result.is_success()
        assert result.value_or('TEST') == 123

        # Restore original parsers
        ParserRegistry._parsers = old_parsers

    def it_handles_custom_error_messages(self):
        """Test that parse handles custom error messages."""

        class UnknownType:
            pass

        custom_msg = 'Custom error message'
        result = ParserRegistry.parse('anything', UnknownType, error_message=custom_msg)
        assert result.is_failure()
        assert custom_msg == result.value_or('TEST')

    def it_parses_with_type_specific_options(self):
        """Test parsing with type-specific options."""

        # Register a parser with options
        def parse_int_with_options(input_value: str, *, min_value=None, max_value=None, **kwargs) -> Maybe[int]:
            result = parse_int(input_value)
            if result.is_failure():
                return result

            value = result.value_or(0)

            if min_value is not None and value < min_value:
                return Maybe.failure(f'Value must be at least {min_value}')

            if max_value is not None and value > max_value:
                return Maybe.failure(f'Value must be at most {max_value}')

            return Maybe.success(value)

        ParserRegistry.register(int, parse_int_with_options)

        # Test with options
        result = ParserRegistry.parse('5', int, min_value=10)
        assert result.is_failure()
        assert 'Value must be at least 10' in result.value_or('TEST')

        result = ParserRegistry.parse('15', int, min_value=10, max_value=20)
        assert result.is_success()
        assert result.value_or('TEST') == 15

        # Clean up
        ParserRegistry._parsers.pop(int, None)
