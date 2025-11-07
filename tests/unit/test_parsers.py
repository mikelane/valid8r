"""Tests for the parsers module."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from enum import Enum
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.parsers import (
    create_parser,
    make_parser,
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
    validated_parser,
)
from valid8r.core.validators import minimum

if TYPE_CHECKING:
    from pytest_mock import (
        MockerFixture,
        MockType,
    )


# Expectation helpers to avoid branching inside test bodies
Expectation = Callable[[Maybe[Any]], None]


def expect_success(expected: Any) -> Expectation:  # noqa: ANN401
    def _check(result: Maybe[Any]) -> None:
        match result:
            case Success(value):
                assert value == expected
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    return _check


def expect_error_equals(expected_error: str) -> Expectation:
    def _check(result: Maybe[Any]) -> None:
        match result:
            case Failure(err):
                assert err == expected_error
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    return _check


def expect_error_contains(text: str) -> Expectation:
    def _check(result: Maybe[Any]) -> None:
        match result:
            case Failure(err):
                assert text in err
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    return _check


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
        match parse_int(input_str):
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('abc', 'Input must be a valid integer', id='non-numeric string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
            pytest.param('42.5', 'Input must be a valid integer', id='decimal with fractional part'),
        ],
    )
    def it_handles_invalid_integers(self, input_str: str, expected_error: str) -> None:
        """Test that parse_int correctly handles invalid inputs."""
        match parse_int(input_str):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == expected_error

    def it_handles_large_integers(self) -> None:
        """Test that parse_int handles very large integers."""
        match parse_int('999999999999999999999999999999'):
            case Success(result):
                assert result == 999999999999999999999999999999
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('3.14159', 3.14159, id='float'),
            pytest.param('  3.14  ', 3.14, id='whitespace-padded float'),
            pytest.param('42', 42.0, id='integer-equivalent float'),
            pytest.param('-42.5', -42.5, id='negative float'),
            pytest.param('1.23e2', 123.0, id='scientific notation'),
            pytest.param('inf', float('inf'), id='infinity'),
            pytest.param('NaN', float('nan'), id='not-a-number'),
        ],
    )
    def it_parses_floats_successfully(self, input_str: str, expected_result: float) -> None:
        """Test that parse_float successfully parses valid floats."""
        match parse_float(input_str):
            case Success(result) if input_str == 'NaN':
                assert str(result) == 'nan'
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('abc', 'Input must be a valid number', id='non-numeric string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
            pytest.param('123abc', 'Input must be a valid number', id='mixed string'),
        ],
    )
    def it_handles_invalid_floats(self, input_str: str, expected_error: str) -> None:
        """Test that parse_float correctly handles invalid inputs."""
        match parse_float(input_str):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == expected_error

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
        match parse_bool(input_str):
            case Success(result):
                assert result == expected_value
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_value'),
        [
            pytest.param('maybe', 'Input must be a valid boolean', id='invalid string'),
            pytest.param('', 'Input must not be empty', id='empty string'),
        ],
    )
    def it_handles_invalid_booleans(self, input_str: str, expected_value: str) -> None:
        """Test that parse_bool correctly handles invalid inputs."""
        match parse_bool(input_str):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == expected_value

    @pytest.mark.parametrize(
        ('input_str', 'expected_value'),
        [
            pytest.param('2023-01-15', date(2023, 1, 15), id='basic ISO format'),
            pytest.param('  2023-01-15  ', date(2023, 1, 15), id='ISO format with whitespace'),
        ],
    )
    def it_parses_dates_with_iso_format(self, input_str: str, expected_value: date) -> None:
        """Test that parse_date successfully parses dates in ISO format."""
        match parse_date(input_str):
            case Success(result):
                assert result == expected_value
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'format_str', 'expected_date'),
        [
            pytest.param('2023-01-15', '%Y-%m-%d', date(2023, 1, 15), id='basic format'),
            pytest.param('15/01/2023', '%d/%m/%Y', date(2023, 1, 15), id='US format'),
            pytest.param('Jan 15, 2023', '%b %d, %Y', date(2023, 1, 15), id='standard written format'),
            pytest.param('20230115', '%Y%m%d', date(2023, 1, 15), id='machine readable format'),
        ],
    )
    def it_parses_dates_with_custom_formats(self, input_str: str, format_str: str, expected_date: date) -> None:
        """Test that parse_date successfully parses dates with custom formats."""
        match parse_date(input_str, date_format=format_str):
            case Success(result):
                assert result == expected_date
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

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
        match parse_date(input_str, date_format=date_format):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == expected_error

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
        match parse_complex(input_str):
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('not a complex', 'Input must be a valid complex number', id='invalid complex'),
            pytest.param('', 'Input must not be empty', id='empty string'),
        ],
    )
    def it_handles_invalid_complex_numbers(self, input_str: str, expected_error: str) -> None:
        """Test that parse_complex correctly handles invalid inputs."""
        match parse_complex(input_str):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(result):
                assert result == expected_error

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('RED', Color.RED, id='valid enum value'),
            pytest.param('  RED  ', Color.RED, id='enum with whitespace'),
        ],
    )
    def it_parses_enums_successfully(self, input_str: str, expected_result: Color) -> None:
        """Test that parse_enum successfully parses enum values."""
        match parse_enum(input_str, Color):
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_enum_by_name(self) -> None:
        """Test that parse_enum can find enum members by name."""

        class TestEnum(Enum):
            WOW = 'omg'

        match parse_enum('WOW', TestEnum):
            case Success(result):
                assert result == TestEnum.WOW
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

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
        match parse_enum(input_str, StrangeEnum):
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'enum_class', 'expected_error'),
        [
            pytest.param('YELLOW', Color, 'Input must be a valid enumeration value', id='invalid enum value'),
            pytest.param('', Color, 'Input must not be empty', id='empty string'),
            pytest.param('xyz', Color, 'Input must be a valid enumeration value', id='no match'),
            pytest.param('test', None, 'Invalid enum class provided', id='invalid enum class'),
        ],
    )
    def it_handles_invalid_enums(self, input_str: str, enum_class: Color | None, expected_error: str) -> None:
        """Test that parse_enum correctly handles invalid inputs."""
        match parse_enum(input_str, enum_class):  # type: ignore
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == expected_error

    @pytest.mark.parametrize(
        ('input_str', 'element_parser', 'custom_msg'),
        [
            pytest.param('abc', parse_int, 'Custom error message', id='int with custom message'),
            pytest.param('abc', parse_float, 'Custom error message', id='float with custom message'),
            pytest.param('invalid', parse_bool, 'Custom error message', id='bool with custom message'),
            pytest.param('invalid', parse_date, 'Custom error message', id='date with custom message'),
            pytest.param('invalid', parse_complex, 'Custom error message', id='complex with custom message'),
            pytest.param(
                'INVALID',
                partial(parse_enum, enum_class=Color),
                'Custom error message',
                id='enum with custom message',
            ),
        ],
    )
    def it_handles_custom_error_messages_for_all_parsers(
        self, input_str: str, element_parser: Callable[..., Maybe[str]], custom_msg: str
    ) -> None:
        """Test that all parsers handle custom error messages correctly."""
        match element_parser(input_str, error_message=custom_msg):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == custom_msg

    def it_handles_valid_custom_date_format(self) -> None:
        """Test that parse_date correctly handles valid custom date format."""
        match parse_date('01/15/2023', date_format='%m/%d/%Y'):
            case result:
                assert result.value_or(date(2000, 1, 1)).isoformat() == '2023-01-15'

    def it_handles_invalid_custom_date_format(self) -> None:
        """Test that parse_date correctly handles invalid custom date format."""
        match parse_date('15/01/2023', date_format='%m/%d/%Y'):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert error == 'Input must be a valid date'

    @pytest.mark.parametrize(
        ('input_str', 'element_parser', 'min_length', 'max_length', 'expectation'),
        [
            pytest.param(
                '1,2,3',
                lambda s: Maybe.success(int(s)),
                5,
                None,
                expect_error_equals('List must have at least 5 elements'),
                id='min length',
            ),
            pytest.param(
                '1,2,3,4,5',
                lambda s: Maybe.success(int(s)),
                None,
                3,
                expect_error_equals('List must have at most 3 elements'),
                id='max length',
            ),
            pytest.param('1,2,3', lambda s: Maybe.success(int(s)), 2, 5, expect_success([1, 2, 3]), id='valid length'),
        ],
    )
    def it_validates_list_length(
        self,
        input_str: str,
        element_parser: Callable[..., Maybe],
        min_length: int,
        max_length: int,
        expectation: Expectation,
    ) -> None:
        """Test that parse_list_with_validation validates list length correctly."""
        match parse_list_with_validation(
            input_str, element_parser=element_parser, min_length=min_length, max_length=max_length
        ):
            case result:
                expectation(result)

    @pytest.mark.parametrize(
        ('input_str', 'required_keys', 'expectation'),
        [
            pytest.param(
                'a:1,b:2,c:3', ['a', 'b', 'c'], expect_success({'a': 1, 'b': 2, 'c': 3}), id='all required keys present'
            ),
            pytest.param(
                'a:1,b:2', ['a', 'b', 'c'], expect_error_equals('Missing required keys: c'), id='missing required keys'
            ),
        ],
    )
    def it_validates_dictionary_required_keys(
        self, input_str: str, required_keys: list[str], expectation: Expectation
    ) -> None:
        """Test that parse_dict_with_validation validates required keys correctly."""
        match parse_dict_with_validation(
            input_str,
            key_parser=lambda s: Maybe.success(s),
            value_parser=lambda s: Maybe.success(int(s)),
            required_keys=required_keys,
        ):
            case result:
                expectation(result)

    def it_parses_set_with_duplicates(self) -> None:
        """Test that parse_set removes duplicates from the input."""
        match parse_set('1,2,3,1,2', element_parser=lambda s: Maybe.success(int(s))):
            case Success(result):
                assert result == {1, 2, 3}
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_handles_non_enum_in_parsing(self) -> None:
        """Test that parse_enum handles non-enum inputs correctly."""

        class NotAnEnum:
            pass

        match parse_enum('value', NotAnEnum):  # type: ignore[arg-type,type-var]
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert 'Invalid enum class provided' in error  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ('input_str', 'min_value', 'max_value', 'error_message', 'expectation'),
        [
            pytest.param('15', 10, 20, None, expect_success(15), id='valid value'),
            pytest.param('5', 10, 20, None, expect_error_equals('Value must be at least 10'), id='below minimum'),
            pytest.param('25', 10, 20, None, expect_error_equals('Value must be at most 20'), id='above maximum'),
            pytest.param('5', 10, 20, 'Custom error', expect_error_equals('Custom error'), id='custom error message'),
        ],
    )
    def it_validates_int_with_min_max(
        self,
        input_str: str,
        min_value: int,
        max_value: int,
        error_message: str,
        expectation: Expectation,
    ) -> None:
        """Test parse_int_with_validation with min and max values."""
        match parse_int_with_validation(
            input_str,
            min_value=min_value,
            max_value=max_value,
            error_message=error_message,
        ):
            case actual:
                expectation(actual)

    @pytest.mark.parametrize(
        ('input_str', 'expected'),
        [
            pytest.param('inf', float('inf'), id='infinity'),
            pytest.param('NaN', 'nan', id='NaN'),
            pytest.param('1.23e-5', 1.23e-5, id='scientific notation'),
        ],
    )
    def it_parses_float_edge_cases(self, input_str: str, expected: float) -> None:
        """Test edge cases in parse_float."""
        match parse_float(input_str):
            case Success(actual) if expected == 'nan':  # required since float('nan') != float('nan')
                assert str(actual) == expected
            case Success(actual):
                assert actual == expected
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    @pytest.mark.parametrize(
        ('input_str', 'date_format', 'expectation'),
        [
            pytest.param('2023/01/15', None, expect_error_equals('Input must be a valid date'), id='invalid date'),
            pytest.param('2023/01/15', '%Y/%m/%d', expect_success(date(2023, 1, 15)), id='valid date with format'),
            pytest.param(
                '20230115', None, expect_error_equals('Input must be a valid date'), id='invalid date with no format'
            ),
        ],
    )
    def it_parses_date_with_non_iso_format(
        self, input_str: str, date_format: str | None, expectation: Expectation
    ) -> None:
        """Test edge cases in parse_date for non-ISO formats."""
        match parse_date(input_str, date_format=date_format):
            case actual:
                expectation(actual)

    @pytest.mark.parametrize(
        ('input_str', 'seperator', 'element_parser', 'expectation'),
        [
            pytest.param('a,b,c,a', None, None, expect_success({'a', 'b', 'c'}), id='default separator'),
            pytest.param('a|b|c', '|', None, expect_success({'a', 'b', 'c'}), id='custom separator'),
            pytest.param('1,2,3', None, create_parser(int), expect_success({1, 2, 3}), id='with element parser'),
            pytest.param('', None, None, expect_error_equals('Parse error'), id='empty string'),
        ],
    )
    def it_parses_set_with_implicit_separators(
        self,
        input_str: str,
        seperator: str | None,
        element_parser: Callable[[str], Any],
        expectation: Expectation,
    ) -> None:
        """Test parsing sets with various separator configurations."""
        match parse_set(input_str, separator=seperator, element_parser=element_parser):
            case actual:
                expectation(actual)

    @pytest.mark.parametrize(
        ('input_str', 'expected_result'),
        [
            pytest.param('RED', Color.RED, id='valid enum name'),
            pytest.param('  RED  ', Color.RED, id='enum name with whitespace'),
            pytest.param('red', Color.RED, id='case insensitive enum name'),
            pytest.param('RED', Color.RED, id='exact enum value'),
            pytest.param('  RED  ', Color.RED, id='enum value with whitespace'),
        ],
    )
    def it_parses_enum_by_name_or_value(self, input_str: str, expected_result: Color) -> None:
        """Test that parse_enum can find enum members by name or value."""
        match parse_enum(input_str, Color):
            case Success(result):
                assert result == expected_result
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_handles_validation_parser_failures_in_int(self) -> None:
        """Test that validation parsers properly handle failures."""
        match parse_int_with_validation('not an integer'):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert 'Input must be a valid integer' in error

    def it_handles_validation_parser_failures_in_list(self) -> None:
        """Test that validation parsers properly handle failures."""
        match parse_list_with_validation(
            'a,b,invalid', element_parser=lambda s: Maybe.failure('Error') if s == 'invalid' else Maybe.success(s)
        ):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert 'Error' in error

    def it_handles_validation_parser_failures_in_dict(self) -> None:
        """Test that validation parsers properly handle failures."""
        match parse_dict_with_validation('invalid dict', error_message='Custom error'):
            case Success(result):
                pytest.fail(f'Unexpected result: {result}')
            case Failure(error):
                assert 'Custom error' in error

    def it_creates_basic_decimal_parser(self) -> None:
        """Test create_parser with Decimal type."""
        decimal_parser = create_parser(Decimal)
        match decimal_parser('123.45'):
            case Success(result):
                assert result == Decimal('123.45')
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_handles_invalid_input_in_decimal_parser(self) -> None:
        """Test error handling in create_parser with invalid input."""
        decimal_parser = create_parser(Decimal)
        match decimal_parser('invalid'):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert 'invalid' in error.casefold()

    def it_uses_custom_error_message_in_decimal_parser(self) -> None:
        """Test create_parser with custom error message."""
        decimal_parser_with_msg = create_parser(Decimal, 'Not a valid decimal')
        match decimal_parser_with_msg('invalid'):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert error == 'Not a valid decimal'

    def it_validates_positive_decimal_values(self) -> None:
        """Test validated_parser with minimum value validation."""

        def min_validator(n: Decimal) -> Maybe[Decimal]:
            return minimum(Decimal(0))(n)

        positive_decimal = validated_parser(Decimal, validator=min_validator)

        match positive_decimal('5.5'):
            case Success(result):
                assert result == Decimal('5.5')
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_rejects_negative_decimal_values(self) -> None:
        """Test validated_parser rejects values that fail validation."""

        def min_validator(n: Decimal) -> Maybe[Decimal]:
            return minimum(Decimal(0))(n)

        positive_decimal = validated_parser(Decimal, min_validator)

        match positive_decimal('-1.5'):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert 'must be at least 0' in error

    def it_fails_with_empty_input(self) -> None:
        """Test validated_parser with empty input."""

        def min_validator(n: Decimal) -> Maybe[Decimal]:
            return minimum(Decimal(0))(n)

        positive_decimal = validated_parser(Decimal, min_validator)

        match positive_decimal(''):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert 'Input must not be empty' in error

    def it_creates_a_parser_using_the_decorator_without_parens(self) -> None:
        """Test using the parser_for decorator to create a parser."""

        @make_parser
        def decimal_parser(s: str) -> Decimal:
            return Decimal(s)

        match decimal_parser('123.45'):
            case Success(result):
                assert result == Decimal('123.45')
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_creates_a_parser_using_the_decorator_with_parens(self) -> None:
        """Test using the parser_for decorator to create a parser."""

        @make_parser()
        def decimal_parser(s: str) -> Decimal:
            return Decimal(s)

        match decimal_parser('123.45'):
            case Success(result):
                assert result == Decimal('123.45')
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_returns_failure_from_decorator_if_input_is_empty(self) -> None:
        """Test that the decorator returns a failure if the input is empty."""

        @make_parser
        def decimal_parser(s: str) -> Decimal:
            return Decimal(s)

        match decimal_parser(''):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert 'Input must not be empty' in error

    def it_returns_failure_from_decorator_if_parser_raises_an_error(self) -> None:
        """Test that the decorator returns a failure if the parser raises an error."""

        @make_parser
        def decimal_parser(s: str) -> Decimal:  # noqa: ARG001
            raise ValueError('Invalid input')

        match decimal_parser('123.45'):
            case Success(result):
                pytest.fail(f'Unexpected success: {result}')
            case Failure(error):
                assert 'Invalid input' in error


class DescribeParsePath:
    """Tests for parse_path function."""

    def it_parses_absolute_posix_path(self) -> None:
        """Parse an absolute POSIX path."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('/home/user/file.txt')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert path.is_absolute()
                assert path.parts == ('/', 'home', 'user', 'file.txt')
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_parses_relative_path(self) -> None:
        """Parse a relative path."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('./data/file.txt')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert not path.is_absolute()
                # Path normalizes './data/file.txt' to 'data/file.txt'
                assert path.parts == ('data', 'file.txt')
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_rejects_none_input(self) -> None:
        """Reject None input."""
        from valid8r.core.parsers import parse_path

        result = parse_path(None)
        match result:
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')
            case Failure(err):
                assert 'Path cannot be empty' in err

    def it_rejects_empty_string(self) -> None:
        """Reject empty string input."""
        from valid8r.core.parsers import parse_path

        result = parse_path('')
        match result:
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')
            case Failure(err):
                assert 'Path cannot be empty' in err

    def it_normalizes_redundant_separators(self) -> None:
        """Normalize paths with redundant separators."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('/home//user///file.txt')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                # Path normalization should collapse multiple separators
                assert str(path) == '/home/user/file.txt'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_handles_current_directory(self) -> None:
        """Handle current directory path."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('.')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert str(path) == '.'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_handles_parent_directory(self) -> None:
        """Handle parent directory path."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('..')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert str(path) == '..'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_expands_user_directory_when_requested(self) -> None:
        """Expand home directory when expand_user=True."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('~/documents/file.txt', expand_user=True)
        match result:
            case Success(path):
                assert isinstance(path, Path)
                # Path should start with the user's home directory
                home_dir = Path('~').expanduser()
                assert str(path).startswith(str(home_dir))
                assert 'documents' in str(path)
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_does_not_expand_user_by_default(self) -> None:
        """Do not expand home directory by default."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('~/documents/file.txt')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                # Should keep the tilde
                assert str(path) == '~/documents/file.txt'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_resolves_to_absolute_path_when_requested(self) -> None:
        """Resolve to absolute path when resolve=True."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('./file.txt', resolve=True)
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert path.is_absolute()
                # Should be in current working directory
                cwd = Path.cwd()
                assert str(path).startswith(str(cwd))
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_does_not_resolve_by_default(self) -> None:
        """Do not resolve paths by default."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path('./file.txt')
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert not path.is_absolute()
                assert str(path) == 'file.txt'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    @pytest.mark.parametrize(
        ('input_path', 'expected_parts'),
        [
            pytest.param('/home/user/file.txt', ('/', 'home', 'user', 'file.txt'), id='absolute-posix'),
            pytest.param('data/file.txt', ('data', 'file.txt'), id='relative-simple'),
            pytest.param('./data/file.txt', ('data', 'file.txt'), id='relative-dot'),  # Path normalizes ./ away
            pytest.param('../parent/file.txt', ('..', 'parent', 'file.txt'), id='relative-parent'),
        ],
    )
    def it_parses_various_path_formats(self, input_path: str, expected_parts: tuple[str, ...]) -> None:
        """Parse various path formats correctly."""
        from pathlib import Path

        from valid8r.core.parsers import parse_path

        result = parse_path(input_path)
        match result:
            case Success(path):
                assert isinstance(path, Path)
                assert path.parts == expected_parts
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')
