"""Tests for phone number parsing."""

from __future__ import annotations

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)

# Test the PhoneNumber class structure first


class DescribePhoneNumber:
    """Tests for the PhoneNumber dataclass."""

    def it_has_required_attributes(self) -> None:
        """PhoneNumber has area_code, exchange, subscriber, country_code, region, extension attributes."""
        from valid8r.core.parsers import PhoneNumber

        phone = PhoneNumber(
            area_code='415',
            exchange='555',
            subscriber='2671',
            country_code='1',
            region='US',
            extension=None,
        )

        assert phone.area_code == '415'
        assert phone.exchange == '555'
        assert phone.subscriber == '2671'
        assert phone.country_code == '1'
        assert phone.region == 'US'
        assert phone.extension is None


# Test basic parsing - simplest case first


class DescribeParsePhone:
    """Tests for the parse_phone function."""

    @pytest.mark.parametrize(
        ('raw', 'expected_area', 'expected_exchange', 'expected_subscriber'),
        [
            pytest.param('4155552671', '415', '555', '2671', id='plain-digits'),
            pytest.param('415-555-2671', '415', '555', '2671', id='dashes'),
            pytest.param('(415) 555-2671', '415', '555', '2671', id='standard-format'),
            pytest.param('415.555.2671', '415', '555', '2671', id='dots'),
            pytest.param('415 555 2671', '415', '555', '2671', id='spaces'),
        ],
    )
    def it_parses_basic_10_digit_numbers(
        self, raw: str, expected_area: str, expected_exchange: str, expected_subscriber: str
    ) -> None:
        """Parse various 10-digit phone number formats."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone(raw)

        match result:
            case Success(phone):
                assert phone.area_code == expected_area
                assert phone.exchange == expected_exchange
                assert phone.subscriber == expected_subscriber
                assert phone.country_code == '1'
                assert phone.region == 'US'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_parses_number_with_country_code(self) -> None:
        """Parse phone number with +1 country code."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('+1 415 555 2671')

        match result:
            case Success(phone):
                assert phone.country_code == '1'
                assert phone.area_code == '415'
                assert phone.exchange == '555'
                assert phone.subscriber == '2671'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_parses_number_with_leading_1(self) -> None:
        """Parse phone number with leading 1 (no plus sign)."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('1(415)555-2671')

        match result:
            case Success(phone):
                assert phone.country_code == '1'
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_strips_whitespace(self) -> None:
        """Parse phone number with leading/trailing whitespace."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('  (415) 555-2671  ')

        match result:
            case Success(phone):
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_rejects_empty_string(self) -> None:
        """Reject empty phone number string."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('')

        match result:
            case Failure(err):
                assert 'cannot be empty' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    def it_rejects_none(self) -> None:
        """Reject None as phone number."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone(None)  # type: ignore[arg-type]

        match result:
            case Failure(err):
                assert 'cannot be empty' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    def it_rejects_whitespace_only(self) -> None:
        """Reject phone number with only whitespace."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('   ')

        match result:
            case Failure(err):
                assert 'cannot be empty' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    def it_rejects_too_few_digits(self) -> None:
        """Reject phone number with fewer than 10 digits."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('555-2671')

        match result:
            case Failure(err):
                assert '10 digits' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    def it_rejects_too_many_digits(self) -> None:
        """Reject phone number with more than 11 digits."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('1234567890123')

        match result:
            case Failure(err):
                assert '10 digits' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    def it_rejects_excessively_long_input(self) -> None:
        """Reject extremely long input to prevent DoS attacks."""
        import time

        from valid8r.core.parsers import parse_phone

        # Create input longer than 100 characters (DoS mitigation threshold)
        malicious_input = '4' * 1000

        # Measure time to ensure fast rejection
        start = time.perf_counter()
        result = parse_phone(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should reject with appropriate error message
        match result:
            case Failure(err):
                assert 'too long' in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

        # Should reject quickly (< 10ms for DoS protection)
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'


class DescribeParsePhoneExtensions:
    """Tests for extension parsing."""

    @pytest.mark.parametrize(
        ('raw', 'expected_ext'),
        [
            pytest.param('415-555-2671 x123', '123', id='x-marker'),
            pytest.param('415-555-2671 ext. 456', '456', id='ext-marker'),
            pytest.param('(415) 555-2671 extension 789', '789', id='extension-word'),
            pytest.param('415-555-2671,123', '123', id='comma-separator'),
            pytest.param('415-555-2671 x5', '5', id='single-digit'),
        ],
    )
    def it_parses_extensions(self, raw: str, expected_ext: str) -> None:
        """Parse phone numbers with various extension formats."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone(raw)

        match result:
            case Success(phone):
                assert phone.extension == expected_ext
                assert phone.area_code == '415'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_parses_phone_without_extension(self) -> None:
        """Parse phone number without extension has None extension."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('415-555-2671')

        match result:
            case Success(phone):
                assert phone.extension is None
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')


class DescribeParsePhoneValidation:
    """Tests for area code and exchange validation."""

    @pytest.mark.parametrize(
        ('raw', 'error_text'),
        [
            pytest.param('055-555-2671', 'invalid area code', id='area-starts-0'),
            pytest.param('155-555-2671', 'invalid area code', id='area-starts-1'),
            pytest.param('555-123-4567', 'reserved', id='area-555'),
            pytest.param('415-011-2671', 'invalid exchange', id='exchange-starts-0'),
            pytest.param('415-155-2671', 'invalid exchange', id='exchange-starts-1'),
            pytest.param('415-911-2671', 'emergency', id='exchange-911'),
            pytest.param('415-555-5555', 'fiction', id='exchange-555-5xxx'),
        ],
    )
    def it_rejects_invalid_area_codes_and_exchanges(self, raw: str, error_text: str) -> None:
        """Reject phone numbers with invalid area codes or exchanges."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone(raw)

        match result:
            case Failure(err):
                assert error_text.lower() in err.lower()
            case Success(value):
                pytest.fail(f'Expected failure but got success: {value}')

    @pytest.mark.parametrize(
        'raw',
        [
            pytest.param('1-800-555-1234', id='toll-free-800'),
            pytest.param('888-555-1234', id='toll-free-888'),
        ],
    )
    def it_accepts_toll_free_numbers(self, raw: str) -> None:
        """Accept toll-free area codes."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone(raw)

        match result:
            case Success(phone):
                assert phone.area_code in ('800', '888', '877', '866', '855', '844', '833')
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')


class DescribePhoneNumberFormatting:
    """Tests for PhoneNumber formatting methods."""

    def it_provides_e164_format(self) -> None:
        """PhoneNumber provides E.164 format (+14155552671)."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('415-555-2671')

        match result:
            case Success(phone):
                assert phone.e164 == '+14155552671'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_e164_format_with_extension(self) -> None:
        """PhoneNumber provides E.164 format with extension."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('415-555-2671 x123')

        match result:
            case Success(phone):
                assert phone.e164 == '+14155552671 x123'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_national_format(self) -> None:
        """PhoneNumber provides national format ((415) 555-2671)."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('4155552671')

        match result:
            case Success(phone):
                assert phone.national == '(415) 555-2671'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_national_format_with_extension(self) -> None:
        """PhoneNumber provides national format with extension."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('415-555-2671 extension 123')

        match result:
            case Success(phone):
                assert phone.national == '(415) 555-2671 ext. 123'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_international_format(self) -> None:
        """PhoneNumber provides international format (+1 415-555-2671)."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('(415) 555-2671')

        match result:
            case Success(phone):
                assert phone.international == '+1 415-555-2671'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_international_format_with_extension(self) -> None:
        """PhoneNumber provides international format with extension."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('+1 415 555 2671 x456')

        match result:
            case Success(phone):
                assert phone.international == '+1 415-555-2671 ext. 456'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')

    def it_provides_raw_digits(self) -> None:
        """PhoneNumber provides raw digits (14155552671)."""
        from valid8r.core.parsers import parse_phone

        result = parse_phone('(415) 555-2671')

        match result:
            case Success(phone):
                assert phone.raw_digits == '14155552671'
            case Failure(err):
                pytest.fail(f'Expected success but got failure: {err}')
