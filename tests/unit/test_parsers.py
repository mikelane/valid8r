"""Tests for the parsers module."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

import pytest

from valid8r.core.parsers import (
    parse_bool,
    parse_complex,
    parse_date,
    parse_enum,
    parse_float,
    parse_int,
)

if TYPE_CHECKING:
    from pytest_mock import (
        MockerFixture,
        MockType,
    )


@pytest.fixture
def mock_int(mocker: MockerFixture) -> MockType:
    """Mock the builtins.int function."""
    return mocker.patch('builtins.int')


class Color(Enum):
    """Color enum for testing."""

    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'


class StrangeEnum(Enum):
    """Enum with unusual values for testing."""

    EMPTY = ''
    SPACE = ' '
    NUMBER = '123'


class DescribeParsers:
    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('42', 42, id='integer'),
            pytest.param('-42', -42, id='negative integer'),
            pytest.param('  42  ', 42, id='integer with whitespace'),
            pytest.param('42.0', 42, id='integer-equivalent float'),
        ],
    )
    def it_parses_integers_successfully(self, input_str: str, expected_result: int) -> None:
        """Test that parse_int successfully parses valid integers."""
        assert parse_int(input_str).is_just()
        assert parse_int(input_str).value() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('abc', 'Input must be a valid integer', id='non-numeric string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
            pytest.param('42.5', 'Input must be a valid integer', id='decimal with fractional part'),
        ],
    )
    def it_handles_invalid_integers(self, input_str: str, expected_result: str) -> None:
        """Test that parse_int correctly handles invalid inputs."""
        result = parse_int(input_str)
        assert result.is_nothing()
        assert result.error() == expected_result

    def it_handles_custom_error_messages_for_integers(self) -> None:
        """Test that parse_int uses custom error messages when provided."""
        custom_msg = 'Please provide a valid number'
        assert parse_int('abc', error_message=custom_msg).error() == custom_msg

    def it_handles_large_integers(self) -> None:
        """Test that parse_int handles very large integers."""
        large_int = '999999999999999999999999999999'
        result = parse_int(large_int)
        assert result.is_just()
        assert result.value() == 999999999999999999999999999999

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            ('3.14159', 3.14159),
            ('  3.14  ', 3.14),
            ('42', 42.0),
            ('-42.5', -42.5),
            ('1.23e2', 123.0),
            ('inf', float('inf')),
            ('NaN', float('nan')),
        ],
    )
    def it_parses_floats_successfully(self, input_str: str, expected_result: float) -> None:
        """Test that parse_float successfully parses valid floats."""
        result = parse_float(input_str)
        assert result.is_just()

        # Handle NaN case separately since NaN != NaN in Python
        if input_str == 'NaN':
            assert str(result.value()) == 'nan'
        else:
            assert result.value() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('abc', 'Input must be a valid number', id='non-numeric string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
            pytest.param('123abc', 'Input must be a valid number', id='mixed string'),
        ],
    )
    def it_handles_invalid_floats(self, input_str: str, expected_result: str) -> None:
        """Test that parse_float correctly handles invalid inputs."""
        result = parse_float(input_str)
        assert result.is_nothing()
        assert result.error() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'expected_value'),
        [
            pytest.param('true', True, id='lowercase'),
            pytest.param('True', True, id='capitalized'),
            pytest.param('TRUE', True, id='uppercase'),
            pytest.param('t', True, id='single letter t'),
            pytest.param('yes', True, id='full yes'),
            pytest.param('y', True, id='single letter y'),
            pytest.param('1', True, id='int for True'),
            pytest.param('false', False, id='lowercase false'),
            pytest.param('False', False, id='capitalized false'),
            pytest.param('FALSE', False, id='uppercase false'),
            pytest.param('f', False, id='single letter f'),
            pytest.param('no', False, id='full no'),
            pytest.param('n', False, id='single letter n'),
            pytest.param('0', False, id='int for False'),
        ],
    )
    def it_parses_booleans_successfully(self, input_str: str, expected_value: bool) -> None:
        """Test that parse_bool successfully parses valid boolean strings."""
        result = parse_bool(input_str)
        assert result.is_just()
        assert result.value() == expected_value

    @pytest.mark.parametrize(
        ('input_str', 'expected_value'),
        [
            pytest.param('maybe', 'Input must be a valid boolean', id='invalid string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
        ],
    )
    def it_handles_invalid_booleans(self, input_str: str, expected_value: str) -> None:
        """Test that parse_bool correctly handles invalid inputs."""
        result = parse_bool(input_str)
        assert result.is_nothing()
        assert result.error() == expected_value

    @pytest.mark.parametrize(
        ('input_str', 'expected_value'),
        [
            pytest.param('2023-01-15', date(2023, 1, 15), id='basic ISO format'),
            pytest.param('  2023-01-15  ', date(2023, 1, 15), id='ISO format with whitespace'),
        ],
    )
    def it_parses_dates_with_iso_format(self, input_str: str, expected_value: date) -> None:
        """Test that parse_date successfully parses dates in ISO format."""
        result = parse_date(input_str)
        assert result.is_just()
        assert result.value() == expected_value

    @pytest.mark.parametrize(
        ('input_str', 'format_str', 'expected_date'),
        [
            ('2023-01-15', '%Y-%m-%d', date(2023, 1, 15)),
            ('15/01/2023', '%d/%m/%Y', date(2023, 1, 15)),
            ('Jan 15, 2023', '%b %d, %Y', date(2023, 1, 15)),
            ('20230115', '%Y%m%d', date(2023, 1, 15)),
        ],
    )
    def it_parses_dates_with_custom_formats(self, input_str: str, format_str: str, expected_date: date) -> None:
        """Test that parse_date successfully parses dates with custom formats."""
        result = parse_date(input_str, date_format=format_str)
        assert result.is_just()
        assert result.value() == expected_date

    @pytest.mark.parametrize(
        ('input_str', 'date_format', 'expected_error'),
        [
            pytest.param('2023-13-45', '%Y-%m-%d', 'Input must be a valid date', id='invalid date'),
            pytest.param('', '%Y-%m-%d', 'Input must not be empty', id='empty string'),
            pytest.param('2023-01-15', '%d/%m/%Y', 'Input must be a valid date', id='wrong format'),
            pytest.param('20230115', '%d/%m/%Y', 'Input must be a valid date', id='non-standard format'),
        ],
    )
    def it_handles_invalid_dates(self, input_str: str, date_format: str, expected_error: str) -> None:
        """Test that parse_date correctly handles invalid inputs."""
        result = parse_date(input_str, date_format=date_format)
        assert result.is_nothing()
        assert result.error() == expected_error

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('3+4j', complex(3, 4), id='basic complex'),
            pytest.param('3+4i', complex(3, 4), id='mathematical i notation'),
            pytest.param('5', complex(5, 0), id='real number'),
            pytest.param('3j', complex(0, 3), id='imaginary number'),
            pytest.param('-2-3j', complex(-2, -3), id='negative real and imaginary'),
            pytest.param('  1+2j  ', complex(1, 2), id='complex with whitespace'),
            pytest.param('(3+4j)', complex(3, 4), id='complex with parentheses'),
            pytest.param('3 + 4j', complex(3, 4), id='complex with spaces'),
        ],
    )
    def it_parses_complex_numbers_successfully(self, input_str: str, expected_result: complex) -> None:
        """Test that parse_complex successfully parses complex numbers."""
        result = parse_complex(input_str)
        assert result.is_just()
        assert result.value() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('not a complex', 'Input must be a valid complex number', id='invalid complex'),
            pytest.param('', 'Input must not be empty', id='empty string'),
        ],
    )
    def it_handles_invalid_complex_numbers(self, input_str: str, expected_error: str) -> None:
        """Test that parse_complex correctly handles invalid inputs."""
        result = parse_complex(input_str)
        assert result.is_nothing()
        assert result.error() == expected_error

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('RED', Color.RED, id='valid enum value'),
            pytest.param('  RED  ', Color.RED, id='enum with whitespace'),
        ],
    )
    def it_parses_enums_successfully(self, input_str: str, expected_result: Color) -> None:
        """Test that parse_enum successfully parses enum values."""
        # Match by value
        result = parse_enum(input_str, Color)
        assert result.is_just()
        assert result.value() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('', StrangeEnum.EMPTY, id='empty string'),
            pytest.param(' ', StrangeEnum.SPACE, id='space value'),
            pytest.param('123', StrangeEnum.NUMBER, id='numeric value'),
        ],
    )
    def it_handles_special_enum_cases(self, input_str: str, expected_result: StrangeEnum) -> None:
        """Test that parse_enum handles special enum cases."""
        # Empty string when empty is a valid enum value
        result = parse_enum(input_str, StrangeEnum)
        assert result.is_just()
        assert result.value() == expected_result

    @pytest.mark.parametrize(
        ('input_str', 'enum_class', 'expected_error'),
        [
            pytest.param('YELLOW', Color, 'Input must be a valid enumeration value', id='invalid enum value'),
            pytest.param('', Color, 'Input must not be empty', id='empty string'),
            pytest.param('red', Color, 'Input must be a valid enumeration value', id='case mismatch'),
            pytest.param('test', None, 'Invalid enum class provided', id='invalid enum class'),
        ],
    )
    def it_handles_invalid_enums(self, input_str: str, enum_class: Color | None, expected_error: str) -> None:
        """Test that parse_enum correctly handles invalid inputs."""
        result = parse_enum(input_str, enum_class)
        assert result.is_nothing()
        assert result.error() == expected_error

    def it_handles_custom_error_messages_for_all_parsers(self) -> None:
        """Test that all parsers handle custom error messages correctly."""
        custom_msg = 'Custom error message'

        # Check each parser with invalid input and custom message
        assert parse_int('abc', error_message=custom_msg).error() == custom_msg
        assert parse_float('abc', error_message=custom_msg).error() == custom_msg
        assert parse_bool('invalid', error_message=custom_msg).error() == custom_msg
        assert parse_date('invalid', error_message=custom_msg).error() == custom_msg
        assert parse_complex('invalid', error_message=custom_msg).error() == custom_msg
        assert parse_enum('INVALID', Color, error_message=custom_msg).error() == custom_msg
