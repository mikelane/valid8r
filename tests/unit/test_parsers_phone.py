"""Unit tests for phone number parsing."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    PhoneNumber,
    parse_phone,
)


class DescribeParsePhone:
    """Unit tests for parse_phone function."""

    # Basic Parsing Success Cases

    @pytest.mark.parametrize(
        ('input_str', 'expected_area', 'expected_exchange', 'expected_subscriber'),
        [
            pytest.param('(415) 555-2671', '415', '555', '2671', id='standard-formatted'),
            pytest.param('415-555-2671', '415', '555', '2671', id='dash-separated'),
            pytest.param('415.555.2671', '415', '555', '2671', id='dot-separated'),
            pytest.param('415 555 2671', '415', '555', '2671', id='space-separated'),
            pytest.param('4155552671', '415', '555', '2671', id='plain-10-digits'),
        ],
    )
    def it_parses_basic_phone_formats(
        self, input_str: str, expected_area: str, expected_exchange: str, expected_subscriber: str
    ) -> None:
        """Test parse_phone with various basic formats."""
        match parse_phone(input_str):
            case Success(phone):
                assert phone.area_code == expected_area
                assert phone.exchange == expected_exchange
                assert phone.subscriber == expected_subscriber
                assert phone.country_code == '1'
                assert phone.extension is None
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_country', 'expected_area'),
        [
            pytest.param('+1 415 555 2671', '1', '415', id='plus-one-spaces'),
            pytest.param('+1-415-555-2671', '1', '415', id='plus-one-dashes'),
            pytest.param('+1 (415) 555-2671', '1', '415', id='plus-one-mixed'),
            pytest.param('1(415)555-2671', '1', '415', id='leading-one-no-plus'),
            pytest.param('14155552671', '1', '415', id='eleven-digits'),
        ],
    )
    def it_parses_phone_with_country_code(self, input_str: str, expected_country: str, expected_area: str) -> None:
        """Test parse_phone with explicit country codes."""
        match parse_phone(input_str):
            case Success(phone):
                assert phone.country_code == expected_country
                assert phone.area_code == expected_area
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    @pytest.mark.parametrize(
        ('input_str', 'expected_ext'),
        [
            pytest.param('415-555-2671 x123', '123', id='x-prefix'),
            pytest.param('415-555-2671 ext. 456', '456', id='ext-dot-prefix'),
            pytest.param('415-555-2671 ext 789', '789', id='ext-no-dot'),
            pytest.param('(415) 555-2671 extension 999', '999', id='extension-word'),
            pytest.param('415-555-2671 X123', '123', id='uppercase-x'),
        ],
    )
    def it_parses_extensions(self, input_str: str, expected_ext: str) -> None:
        """Test parse_phone with various extension formats."""
        match parse_phone(input_str):
            case Success(phone):
                assert phone.extension == expected_ext
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    def it_parses_phone_without_extension(self) -> None:
        """Test parse_phone correctly identifies no extension."""
        match parse_phone('415-555-2671'):
            case Success(phone):
                assert phone.extension is None
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    def it_handles_whitespace_padding(self) -> None:
        """Test parse_phone with extra whitespace."""
        match parse_phone('  (415) 555-2671  '):
            case Success(phone):
                assert phone.area_code == '415'
                assert phone.exchange == '555'
                assert phone.subscriber == '2671'
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    # Region Parameter

    def it_accepts_region_parameter(self) -> None:
        """Test parse_phone with region parameter."""
        match parse_phone('+1 604 555 1234', region='CA'):
            case Success(phone):
                assert phone.region == 'CA'
                assert phone.country_code == '1'
                assert phone.area_code == '604'
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    def it_defaults_to_us_region(self) -> None:
        """Test parse_phone defaults to US region."""
        match parse_phone('415-555-2671'):
            case Success(phone):
                assert phone.region == 'US'
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    # Error Cases

    def it_rejects_empty_string(self) -> None:
        """Test parse_phone rejects empty input."""
        match parse_phone(''):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert 'cannot be empty' in err

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('555-2671', 'must have 10 digits', id='too-few-digits'),
            pytest.param('1234567890123', 'must have 10 digits', id='too-many-digits'),
            pytest.param('415-555-267', 'must have 10 digits', id='nine-digits'),
        ],
    )
    def it_rejects_invalid_digit_count(self, input_str: str, expected_error: str) -> None:
        """Test parse_phone rejects wrong number of digits."""
        match parse_phone(input_str):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert expected_error in err

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('055-555-2671', 'Invalid area code', id='area-starts-with-0'),
            pytest.param('155-555-2671', 'Invalid area code', id='area-starts-with-1'),
            pytest.param('555-123-4567', 'reserved', id='area-555-reserved'),
        ],
    )
    def it_rejects_invalid_area_codes(self, input_str: str, expected_error: str) -> None:
        """Test parse_phone rejects invalid area codes."""
        match parse_phone(input_str):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert expected_error in err

    @pytest.mark.parametrize(
        ('input_str', 'expected_error'),
        [
            pytest.param('415-055-2671', 'Invalid exchange', id='exchange-starts-with-0'),
            pytest.param('415-155-2671', 'Invalid exchange', id='exchange-starts-with-1'),
            pytest.param('415-911-2671', 'Invalid exchange', id='emergency-911'),
            pytest.param('415-555-0100', 'reserved', id='reserved-555-01xx'),
            pytest.param('415-555-0199', 'reserved', id='reserved-555-0199'),
        ],
    )
    def it_rejects_invalid_exchanges(self, input_str: str, expected_error: str) -> None:
        """Test parse_phone rejects invalid exchange codes."""
        match parse_phone(input_str):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert expected_error in err

    def it_rejects_non_north_american_country_codes(self) -> None:
        """Test parse_phone rejects non-NANP country codes."""
        match parse_phone('+44 20 7946 0958'):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert 'Only North American' in err

    def it_rejects_alphabetic_characters(self) -> None:
        """Test parse_phone rejects letters in input."""
        match parse_phone('1-800-FLOWERS'):
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert 'Invalid format' in err or 'invalid characters' in err

    # Strict Mode

    def it_rejects_unformatted_number_in_strict_mode(self) -> None:
        """Test parse_phone rejects plain digits in strict mode."""
        match parse_phone('4155552671', strict=True):
            case Success(phone):
                pytest.fail(f'Unexpected success in strict mode: {phone}')
            case Failure(err):
                assert 'strict mode requires formatting' in err.lower()

    def it_accepts_formatted_number_in_strict_mode(self) -> None:
        """Test parse_phone accepts formatted numbers in strict mode."""
        match parse_phone('(415) 555-2671', strict=True):
            case Success(phone):
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Unexpected failure in strict mode: {err}')

    def it_allows_non_strict_mode(self) -> None:
        """Test parse_phone with strict=False."""
        match parse_phone('4155552671', strict=False):
            case Success(phone):
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Unexpected failure: {err}')

    # Type Validation

    def it_rejects_non_string_input(self) -> None:
        """Test parse_phone rejects non-string types."""
        match parse_phone(''):  # Empty string is the simplest non-phone case
            case Success(phone):
                pytest.fail(f'Unexpected success: {phone}')
            case Failure(err):
                assert 'cannot be empty' in err.lower()


class DescribePhoneNumber:
    """Unit tests for PhoneNumber dataclass properties."""

    def it_provides_e164_format(self) -> None:
        """Test PhoneNumber.e164 property returns correct format."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        assert phone.e164 == '+14155552671'

    def it_provides_e164_format_with_extension(self) -> None:
        """Test PhoneNumber.e164 includes extension."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='123',
            region='US',
        )
        assert phone.e164 == '+14155552671 x123'

    def it_provides_national_format(self) -> None:
        """Test PhoneNumber.national property returns correct format."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        assert phone.national == '(415) 555-2671'

    def it_provides_national_format_with_extension(self) -> None:
        """Test PhoneNumber.national includes extension with ext. prefix."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='456',
            region='US',
        )
        assert phone.national == '(415) 555-2671 ext. 456'

    def it_provides_international_format(self) -> None:
        """Test PhoneNumber.international property returns correct format."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        assert phone.international == '+1 415-555-2671'

    def it_provides_international_format_with_extension(self) -> None:
        """Test PhoneNumber.international includes extension with ext. prefix."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='789',
            region='US',
        )
        assert phone.international == '+1 415-555-2671 ext. 789'

    def it_provides_raw_digits(self) -> None:
        """Test PhoneNumber.raw_digits property."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='123',
            region='US',
        )
        assert phone.raw_digits == '14155552671'

    def it_excludes_extension_from_raw_digits(self) -> None:
        """Test PhoneNumber.raw_digits excludes extension."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='999',
            region='US',
        )
        # raw_digits should not include extension
        assert phone.raw_digits == '14155552671'
        assert '999' not in phone.raw_digits

    def it_is_frozen_dataclass(self) -> None:
        """Test PhoneNumber is immutable."""
        phone = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        with pytest.raises(FrozenInstanceError):
            phone.area_code = '510'  # type: ignore[misc]

    def it_supports_equality_comparison(self) -> None:
        """Test PhoneNumber supports equality."""
        phone1 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        phone2 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        assert phone1 == phone2

    def it_distinguishes_different_phones(self) -> None:
        """Test PhoneNumber distinguishes different numbers."""
        phone1 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension=None,
            region='US',
        )
        phone2 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2672',  # Different subscriber
            extension=None,
            region='US',
        )
        assert phone1 != phone2

    def it_distinguishes_phones_with_different_extensions(self) -> None:
        """Test PhoneNumber treats different extensions as different numbers."""
        phone1 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='123',
            region='US',
        )
        phone2 = PhoneNumber(
            country_code='1',
            area_code='415',
            exchange='555',
            subscriber='2671',
            extension='456',
            region='US',
        )
        assert phone1 != phone2
