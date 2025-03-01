"""Tests for the parsers module."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

import pytest

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    ParserRegistry,
    _check_enum_has_empty_value,
    _find_enum_by_name,
    _find_enum_by_value,
    _parse_key_value_pair,
    parse_bool,
    parse_complex,
    parse_date,
    parse_dict_with_validation,
    parse_enum,
    parse_float,
    parse_int,
    parse_int_with_validation,
    parse_list_with_validation,
    parse_set,
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
        result = parse_int(input_str)
        assert result.is_success()
        assert result.value_or('TEST') == expected_result

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_result

    def it_handles_custom_error_messages_for_integers(self) -> None:
        """Test that parse_int uses custom error messages when provided."""
        custom_msg = 'Please provide a valid number'
        assert parse_int('abc', error_message=custom_msg).value_or('TEST') == custom_msg

    def it_handles_large_integers(self) -> None:
        """Test that parse_int handles very large integers."""
        large_int = '999999999999999999999999999999'
        result = parse_int(large_int)
        assert result.is_success()
        assert result.value_or('TEST') == 999999999999999999999999999999

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
        assert result.is_success()

        # Handle NaN case separately since NaN != NaN in Python
        if input_str == 'NaN':
            assert str(result.value_or('TEST')) == 'nan'
        else:
            assert result.value_or('TEST') == expected_result

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_result

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_value

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_value

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_value

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_date

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_error

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_result

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_error

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_result

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
        assert result.is_success()
        assert result.value_or('TEST') == expected_result

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
        assert result.is_failure()
        assert result.value_or('TEST') == expected_error

    def it_handles_custom_error_messages_for_all_parsers(self) -> None:
        """Test that all parsers handle custom error messages correctly."""
        custom_msg = 'Custom error message'

        # Check each parser with invalid input and custom message
        assert parse_int('abc', error_message=custom_msg).value_or('TEST') == custom_msg
        assert parse_float('abc', error_message=custom_msg).value_or('TEST') == custom_msg
        assert parse_bool('invalid', error_message=custom_msg).value_or('TEST') == custom_msg
        assert parse_date('invalid', error_message=custom_msg).value_or('TEST') == custom_msg
        assert parse_complex('invalid', error_message=custom_msg).value_or('TEST') == custom_msg
        assert parse_enum('INVALID', Color, error_message=custom_msg).value_or('TEST') == custom_msg

    def it_handles_empty_string_value_in_enum(self) -> None:
        """Test that _check_enum_has_empty_value correctly identifies enums with empty string values."""

        # Create enum with empty string value
        class EmptyEnum(Enum):
            EMPTY = ''
            OTHER = 'other'

        # Create enum without empty string value
        class NonEmptyEnum(Enum):
            ONE = 'one'
            TWO = 'two'

        assert _check_enum_has_empty_value(EmptyEnum) is True
        assert _check_enum_has_empty_value(NonEmptyEnum) is False

    def it_handles_non_enum_in_check_enum_has_empty_value(self) -> None:
        """Test that _check_enum_has_empty_value handles non-enum inputs."""

        class NotAnEnum:
            pass

        # Should handle gracefully and return False
        assert _check_enum_has_empty_value(NotAnEnum) is False

    def it_handles_custom_date_formats(self) -> None:
        """Test that parse_date correctly handles various date formats."""
        # Test non-standard date format with custom format string
        result = parse_date('01/15/2023', date_format='%m/%d/%Y')
        assert result.is_success()
        assert result.value_or(None).isoformat() == '2023-01-15'

        # Test invalid date with custom format
        result = parse_date('15/01/2023', date_format='%m/%d/%Y')
        assert result.is_failure()

    def it_validates_list_length(self) -> None:
        """Test that parse_list_with_validation validates list length correctly."""
        # Test minimum length validation
        result = parse_list_with_validation('1,2,3', element_parser=lambda s: Maybe.success(int(s)), min_length=5)
        assert result.is_failure()
        assert 'at least 5' in result.value_or('')

        # Test maximum length validation
        result = parse_list_with_validation('1,2,3,4,5', element_parser=lambda s: Maybe.success(int(s)), max_length=3)
        assert result.is_failure()
        assert 'at most 3' in result.value_or('')

        # Test both min and max length (valid case)
        result = parse_list_with_validation(
            '1,2,3', element_parser=lambda s: Maybe.success(int(s)), min_length=2, max_length=5
        )
        assert result.is_success()
        assert result.value_or([]) == [1, 2, 3]

    def it_validates_dictionary_required_keys(self) -> None:
        """Test that parse_dict_with_validation validates required keys correctly."""
        # Test missing required keys
        result = parse_dict_with_validation(
            'a:1,b:2',
            key_parser=lambda s: Maybe.success(s),
            value_parser=lambda s: Maybe.success(int(s)),
            required_keys=['a', 'b', 'c'],
        )
        assert result.is_failure()
        assert 'Missing required keys' in result.value_or('')

        # Test with all required keys present
        result = parse_dict_with_validation(
            'a:1,b:2,c:3',
            key_parser=lambda s: Maybe.success(s),
            value_parser=lambda s: Maybe.success(int(s)),
            required_keys=['a', 'b', 'c'],
        )
        assert result.is_success()
        assert result.value_or({}) == {'a': 1, 'b': 2, 'c': 3}

    def it_parses_set_with_duplicates(self) -> None:
        """Test that parse_set removes duplicates from the input."""
        # Parse a list with duplicates to a set
        result = parse_set('1,2,3,1,2', element_parser=lambda s: Maybe.success(int(s)))
        assert result.is_success()

        set_result = result.value_or(set())
        assert set_result == {1, 2, 3}
        assert len(set_result) == 3  # Confirm duplicates were removed

    def it_handles_parser_registry_inheritance(self) -> None:
        """Test that ParserRegistry supports inheritance in parser lookup."""

        # Define parent and child classes
        class Animal:
            pass

        class Dog(Animal):
            def bark(self) -> str:
                return 'Woof!'

        # Register a parser for the parent class
        def parse_animal(input_value: str) -> Maybe[Animal]:
            animal = Animal()
            return Maybe.success(animal)

        ParserRegistry.register(Animal, parse_animal)

        # Test parsing with the child class
        result = ParserRegistry.parse('any input', Dog)
        assert result.is_success()

        # The result should be an Animal instance, not a Dog instance
        # (since we're using the parent parser)
        parsed_object = result.value_or(None)
        assert isinstance(parsed_object, Animal)
        assert not hasattr(parsed_object, 'bark')  # It's not actually a Dog

        # Clean up
        ParserRegistry._parsers.pop(Animal, None)  # noqa: SLF001

    def it_registers_and_uses_default_parsers(self) -> None:
        """Test that ParserRegistry.register_defaults adds parsers for built-in types."""
        # Clear existing parsers
        old_parsers = ParserRegistry._parsers.copy()  # noqa: SLF001
        ParserRegistry._parsers.clear()  # noqa: SLF001

        # Register default parsers
        ParserRegistry.register_defaults()

        # Test parsing different types
        types_to_test = [
            (int, '42', 42),
            (float, '3.14', 3.14),
            (bool, 'true', True),
            (str, 'hello', 'hello'),
            (list, 'a,b,c', ['a', 'b', 'c']),
            (dict, 'a:1,b:2', {'a': '1', 'b': '2'}),
            (set, 'a,b,a,c', {'a', 'b', 'c'}),
        ]

        for type_class, input_str, expected in types_to_test:
            result = ParserRegistry.parse(input_str, type_class)
            assert result.is_success(), f'Failed to parse {input_str} as {type_class.__name__}'

            value = result.value_or(None)
            if isinstance(expected, (list, dict, set)):
                # For collections, compare contents not exact equality
                assert type(value) == type(expected)
                if isinstance(expected, dict):
                    assert value.keys() == expected.keys()
                    for k in expected:
                        assert value[k] == expected[k]
                else:
                    assert len(value) == len(expected)
                    for item in expected:
                        assert item in value
            else:
                assert value == expected

        # Restore original parsers
        ParserRegistry._parsers = old_parsers  # noqa: SLF001

    def it_parses_with_type_specific_options(self) -> None:
        """Test ParserRegistry.parse with type-specific options."""
        # Clear existing parsers
        old_parsers = ParserRegistry._parsers.copy()  # noqa: SLF001
        ParserRegistry._parsers.clear()  # noqa: SLF001

        # Register a custom parser that takes options
        def parse_int_with_options(
            input_value: str, *, min_value: int | None = None, max_value: int | None = None
        ) -> Maybe[int]:
            try:
                value = int(input_value)

                if min_value is not None and value < min_value:
                    return Maybe.failure(f'Value must be at least {min_value}')

                if max_value is not None and value > max_value:
                    return Maybe.failure(f'Value must be at most {max_value}')

                return Maybe.success(value)
            except ValueError:
                return Maybe.failure('Invalid integer')

        ParserRegistry.register(int, parse_int_with_options)

        # Test with options
        result = ParserRegistry.parse('25', int, min_value=10, max_value=30)
        assert result.is_success()
        assert result.value_or(0) == 25

        # Test with min_value validation
        result = ParserRegistry.parse('5', int, min_value=10)
        assert result.is_failure()
        assert 'at least 10' in result.value_or('')

        # Test with max_value validation
        result = ParserRegistry.parse('35', int, max_value=30)
        assert result.is_failure()
        assert 'at most 30' in result.value_or('')

        # Restore original parsers
        ParserRegistry._parsers = old_parsers  # noqa: SLF001

    def it_finds_enum_by_value(self) -> None:
        """Test that _find_enum_by_value correctly finds enum members."""

        class TestEnum(Enum):
            A = 'a'
            B = 'b'
            EMPTY = ''

        # Find existing value
        result = _find_enum_by_value(TestEnum, 'a')
        assert result == TestEnum.A

        # Find empty string value
        result = _find_enum_by_value(TestEnum, '')
        assert result == TestEnum.EMPTY

        # Non-existent value
        result = _find_enum_by_value(TestEnum, 'not_exists')
        assert result is None

    def it_finds_enum_by_name(self) -> None:
        """Test that _find_enum_by_name correctly finds enum members."""

        class TestEnum(Enum):
            A = 'a'
            B = 'b'

        # Find existing name
        result = _find_enum_by_name(TestEnum, 'A')
        assert result == TestEnum.A

        # Non-existent name
        result = _find_enum_by_name(TestEnum, 'C')
        assert result is None

        # Try with KeyError (by creating a mock enum)
        class MockEnum:
            @classmethod
            def __class_getitem__(cls, key: str) -> None:
                raise KeyError(f'Key {key} not found')

        result = _find_enum_by_name(MockEnum, 'anything')  # type: ignore
        assert result is None

    def it_parses_key_value_pairs(self) -> None:
        """Test _parse_key_value_pair function with various inputs."""
        # Valid pair
        success, key, value, error = _parse_key_value_pair(
            'a:1', 0, lambda s: Maybe.success(s), lambda s: Maybe.success(int(s)), ':', None
        )
        assert success is True
        assert key == 'a'
        assert value == 1
        assert error is None

        # Missing separator
        success, key, value, error = _parse_key_value_pair(
            'no-separator', 0, lambda s: Maybe.success(s), lambda s: Maybe.success(int(s)), ':', None
        )
        assert success is False
        assert key is None
        assert value is None
        assert 'missing separator' in error

        # Custom error message
        success, key, value, error = _parse_key_value_pair(
            'no-separator', 0, lambda s: Maybe.success(s), lambda s: Maybe.success(int(s)), ':', 'Custom error'
        )
        assert success is False
        assert error == 'Custom error'

        # Key parsing failure
        success, key, value, error = _parse_key_value_pair(
            'a:1', 0, lambda s: Maybe.failure('Bad key'), lambda s: Maybe.success(int(s)), ':', None
        )
        assert success is False
        assert key is None
        assert value is None
        assert 'Failed to parse key' in error

        # Value parsing failure
        success, key, value, error = _parse_key_value_pair(
            'a:not-int', 0, lambda s: Maybe.success(s), lambda s: Maybe.failure('Bad value'), ':', None
        )
        assert success is False
        assert key is None
        assert value is None
        assert 'Failed to parse value' in error

    def it_handles_non_enum_in_parsing(self) -> None:
        """Test that parse_enum handles non-enum inputs correctly."""

        class NotAnEnum:
            pass

        result = parse_enum('value', NotAnEnum)  # type: ignore
        assert result.is_failure()
        assert 'Invalid enum class provided' in result.value_or('')

    def it_parser_registry_handles_missing_parser(self) -> None:
        """Test ParserRegistry with missing parser."""

        # Make sure the type doesn't have a parser
        class CustomType:
            pass

        if CustomType in ParserRegistry._parsers:  # noqa: SLF001
            del ParserRegistry._parsers[CustomType]  # noqa: SLF001

        # Try to parse with missing parser
        result = ParserRegistry.parse('value', CustomType)
        assert result.is_failure()
        assert 'No parser found for type' in result.value_or('')

    def it_validates_int_with_min_max(self) -> None:
        """Test parse_int_with_validation with min and max values."""
        # Valid within range
        result = parse_int_with_validation('15', min_value=10, max_value=20)
        assert result.is_success()
        assert result.value_or(0) == 15

        # Below minimum
        result = parse_int_with_validation('5', min_value=10, max_value=20)
        assert result.is_failure()
        assert 'must be at least 10' in result.value_or('')

        # Above maximum
        result = parse_int_with_validation('25', min_value=10, max_value=20)
        assert result.is_failure()
        assert 'must be at most 20' in result.value_or('')

        # Custom error message
        result = parse_int_with_validation('5', min_value=10, error_message='Custom error')
        assert result.is_failure()
        assert result.value_or('') == 'Custom error'

    def it_parses_float_edge_cases(self) -> None:
        """Test edge cases in parse_float."""
        # Parse special values
        infinity_result = parse_float('inf')
        assert infinity_result.is_success()
        assert infinity_result.value_or(0) == float('inf')

        # NaN case
        nan_result = parse_float('NaN')
        assert nan_result.is_success()
        assert str(nan_result.value_or(0)) == 'nan'  # NaN doesn't equal itself, so check string

        # Scientific notation
        sci_result = parse_float('1.23e-5')
        assert sci_result.is_success()
        assert sci_result.value_or(0) == 1.23e-5

    def it_parses_date_with_non_iso_format(self) -> None:
        """Test edge cases in parse_date for non-ISO formats."""
        # Date that looks like ISO format but isn't exactly
        result = parse_date('2023/01/15')  # Forward slashes instead of hyphens
        assert result.is_failure()

        # Valid date with explicit format
        result = parse_date('2023/01/15', date_format='%Y/%m/%d')
        assert result.is_success()

        # Date too short for ISO
        result = parse_date('20230115')
        assert result.is_failure()

    def it_parses_set_with_implicit_separators(self) -> None:
        """Test parsing sets with various separator configurations."""
        # Default separator
        result = parse_set('a,b,c,a')  # Duplicate 'a' should be removed
        assert result.is_success()
        assert result.value_or(set()) == {'a', 'b', 'c'}

        # Custom separator
        result = parse_set('a|b|c|a', separator='|')
        assert result.is_success()
        assert result.value_or(set()) == {'a', 'b', 'c'}

        # With element parser
        result = parse_set('1,2,3,1', element_parser=lambda s: Maybe.success(int(s)))
        assert result.is_success()
        assert result.value_or(set()) == {1, 2, 3}

        # Empty input
        result = parse_set('')
        assert result.is_failure()
        assert 'Input must not be empty' in result.value_or('')
