"""Tests for datetime and timedelta parsers."""

from __future__ import annotations

from datetime import (
    UTC,
    timedelta,
)

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    parse_datetime,
    parse_timedelta,
)


class DescribeParseDatetime:
    """Test suite for parse_datetime."""

    def it_parses_iso_datetime_with_z_suffix(self) -> None:
        """Parse ISO 8601 datetime with Z suffix indicating UTC."""
        result = parse_datetime('2024-01-01T12:00:00Z')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.month == 1
                assert dt.day == 1
                assert dt.hour == 12
                assert dt.minute == 0
                assert dt.second == 0
                assert dt.tzinfo == UTC
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_datetime_with_utc_offset(self) -> None:
        """Parse ISO 8601 datetime with explicit UTC offset."""
        result = parse_datetime('2024-01-01T12:00:00+00:00')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.month == 1
                assert dt.day == 1
                assert dt.hour == 12
                assert dt.minute == 0
                assert dt.second == 0
                assert dt.tzinfo == UTC
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_datetime_with_positive_offset(self) -> None:
        """Parse ISO 8601 datetime with positive timezone offset."""
        result = parse_datetime('2024-01-01T12:00:00+05:30')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.month == 1
                assert dt.day == 1
                assert dt.hour == 12
                assert dt.minute == 0
                assert dt.second == 0
                # Verify timezone offset is +05:30
                assert dt.utcoffset() == timedelta(hours=5, minutes=30)
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_datetime_with_negative_offset(self) -> None:
        """Parse ISO 8601 datetime with negative timezone offset."""
        result = parse_datetime('2024-01-01T12:00:00-08:00')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.month == 1
                assert dt.day == 1
                assert dt.hour == 12
                assert dt.minute == 0
                assert dt.second == 0
                # Verify timezone offset is -08:00
                assert dt.utcoffset() == timedelta(hours=-8)
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_datetime_with_microseconds(self) -> None:
        """Parse ISO 8601 datetime with fractional seconds."""
        result = parse_datetime('2024-01-01T12:00:00.123456Z')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.microsecond == 123456
                assert dt.tzinfo == UTC
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_strips_whitespace_from_input(self) -> None:
        """Parse datetime with leading and trailing whitespace."""
        result = parse_datetime('  2024-01-01T12:00:00Z  ')

        match result:
            case Success(dt):
                assert dt.year == 2024
                assert dt.tzinfo == UTC
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_rejects_empty_input(self) -> None:
        """Reject empty string input."""
        result = parse_datetime('')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'empty' in error.lower()

    def it_rejects_none_input(self) -> None:
        """Reject None input."""
        result = parse_datetime(None)  # type: ignore[arg-type]

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'empty' in error.lower()

    def it_rejects_invalid_datetime_format(self) -> None:
        """Reject datetime string that doesn't match ISO 8601 format."""
        result = parse_datetime('not a datetime')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'valid' in error.lower()

    def it_rejects_naive_datetime_without_timezone(self) -> None:
        """Reject datetime without timezone information (naive datetime)."""
        result = parse_datetime('2024-01-01T12:00:00')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'timezone' in error.lower()

    def it_rejects_excessively_long_input(self) -> None:
        """Reject extremely long input to prevent DoS attacks."""
        import time

        malicious_input = '2024-01-01T12:00:00Z' * 100

        start = time.perf_counter()
        result = parse_datetime(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'too long' in error.lower()
                # DoS protection: should reject immediately
                assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_handles_custom_error_message(self) -> None:
        """Use custom error message when provided."""
        custom_msg = 'Custom datetime error'
        result = parse_datetime('invalid', error_message=custom_msg)

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert error == custom_msg


class DescribeParseTimedelta:
    """Test suite for parse_timedelta."""

    def it_parses_simple_minutes(self) -> None:
        """Parse simple minute notation (e.g., '90m')."""
        result = parse_timedelta('90m')

        match result:
            case Success(td):
                assert td.total_seconds() == 5400  # 90 * 60
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_simple_hours(self) -> None:
        """Parse simple hour notation (e.g., '2h')."""
        result = parse_timedelta('2h')

        match result:
            case Success(td):
                assert td.total_seconds() == 7200  # 2 * 3600
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_simple_seconds(self) -> None:
        """Parse simple second notation (e.g., '45s')."""
        result = parse_timedelta('45s')

        match result:
            case Success(td):
                assert td.total_seconds() == 45
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_simple_days(self) -> None:
        """Parse simple day notation (e.g., '3d')."""
        result = parse_timedelta('3d')

        match result:
            case Success(td):
                assert td.total_seconds() == 259200  # 3 * 86400
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_combined_hours_and_minutes(self) -> None:
        """Parse combined duration (e.g., '1h 30m')."""
        result = parse_timedelta('1h 30m')

        match result:
            case Success(td):
                assert td.total_seconds() == 5400  # (1 * 3600) + (30 * 60)
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_combined_days_hours_minutes_seconds(self) -> None:
        """Parse fully combined duration (e.g., '1d 2h 30m 45s')."""
        result = parse_timedelta('1d 2h 30m 45s')

        match result:
            case Success(td):
                expected = (1 * 86400) + (2 * 3600) + (30 * 60) + 45
                assert td.total_seconds() == expected
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_8601_duration(self) -> None:
        """Parse ISO 8601 duration format (e.g., 'PT1H30M')."""
        result = parse_timedelta('PT1H30M')

        match result:
            case Success(td):
                assert td.total_seconds() == 5400  # (1 * 3600) + (30 * 60)
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_8601_with_days(self) -> None:
        """Parse ISO 8601 duration with days (e.g., 'P1DT2H')."""
        result = parse_timedelta('P1DT2H')

        match result:
            case Success(td):
                assert td.total_seconds() == 93600  # (1 * 86400) + (2 * 3600)
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_iso_8601_with_seconds(self) -> None:
        """Parse ISO 8601 duration with seconds (e.g., 'PT45S')."""
        result = parse_timedelta('PT45S')

        match result:
            case Success(td):
                assert td.total_seconds() == 45
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_strips_whitespace_from_input(self) -> None:
        """Parse timedelta with leading and trailing whitespace."""
        result = parse_timedelta('  90m  ')

        match result:
            case Success(td):
                assert td.total_seconds() == 5400
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_parses_without_whitespace_between_units(self) -> None:
        """Parse timedelta without spaces between units (e.g., '1h30m')."""
        result = parse_timedelta('1h30m')

        match result:
            case Success(td):
                assert td.total_seconds() == 5400
            case Failure(error):
                pytest.fail(f'Unexpected error: {error}')

    def it_rejects_empty_input(self) -> None:
        """Reject empty string input."""
        result = parse_timedelta('')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'empty' in error.lower()

    def it_rejects_none_input(self) -> None:
        """Reject None input."""
        result = parse_timedelta(None)  # type: ignore[arg-type]

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'empty' in error.lower()

    def it_rejects_invalid_format(self) -> None:
        """Reject invalid timedelta format."""
        result = parse_timedelta('not a duration')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'valid' in error.lower()

    def it_rejects_negative_durations(self) -> None:
        """Reject negative duration values."""
        result = parse_timedelta('-90m')

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'negative' in error.lower()

    def it_rejects_excessively_long_input(self) -> None:
        """Reject extremely long input to prevent DoS attacks."""
        import time

        malicious_input = '1h30m' * 200

        start = time.perf_counter()
        result = parse_timedelta(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'too long' in error.lower()
                # DoS protection: should reject immediately
                assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_invalid_iso_8601_duration_format(self) -> None:
        """Reject malformed ISO 8601 duration format."""
        result = parse_timedelta('P1X')  # Invalid unit 'X'

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'valid' in error.lower()

    def it_handles_custom_error_message(self) -> None:
        """Use custom error message when provided."""
        custom_msg = 'Custom timedelta error'
        result = parse_timedelta('invalid', error_message=custom_msg)

        match result:
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert error == custom_msg
