"""Performance benchmarks comparing valid8r to competitor libraries.

Run with: uv run pytest benchmarks/test_benchmarks.py --benchmark-only
Generate report: uv run pytest benchmarks/test_benchmarks.py --benchmark-only --benchmark-json=output.json

This module uses pytest-benchmark to measure performance of:
- valid8r (this library)
- Pydantic (Rust-powered validation)
- marshmallow (schema-based validation)
- cerberus (lightweight validation)
"""

from __future__ import annotations

import pytest

from benchmarks.scenarios import (
    benchmark_cerberus_email,
    benchmark_cerberus_int,
    benchmark_cerberus_list,
    benchmark_cerberus_nested,
    benchmark_cerberus_url,
    benchmark_marshmallow_email,
    benchmark_marshmallow_int,
    benchmark_marshmallow_list,
    benchmark_marshmallow_nested,
    benchmark_marshmallow_url,
    benchmark_pydantic_email,
    benchmark_pydantic_int,
    benchmark_pydantic_list,
    benchmark_pydantic_nested,
    benchmark_pydantic_url,
    benchmark_valid8r_email,
    benchmark_valid8r_int,
    benchmark_valid8r_list,
    benchmark_valid8r_nested,
    benchmark_valid8r_url,
)

# =============================================================================
# Integer Parsing Benchmarks
# =============================================================================


class DescribeIntegerParsing:
    """Benchmark integer parsing (success case)."""

    def it_benchmarks_valid8r_int_success(self, benchmark) -> None:
        """Benchmark valid8r integer parsing (success)."""
        result = benchmark(benchmark_valid8r_int, '42')
        assert result == 42

    def it_benchmarks_pydantic_int_success(self, benchmark) -> None:
        """Benchmark Pydantic integer parsing (success)."""
        result = benchmark(benchmark_pydantic_int, '42')
        assert result == 42

    def it_benchmarks_marshmallow_int_success(self, benchmark) -> None:
        """Benchmark marshmallow integer parsing (success)."""
        result = benchmark(benchmark_marshmallow_int, '42')
        assert result == 42

    def it_benchmarks_cerberus_int_success(self, benchmark) -> None:
        """Benchmark cerberus integer parsing (success)."""
        result = benchmark(benchmark_cerberus_int, '42')
        assert result == 42


class DescribeIntegerParsingFailure:
    """Benchmark integer parsing (failure case)."""

    def it_benchmarks_valid8r_int_failure(self, benchmark) -> None:
        """Benchmark valid8r integer parsing (failure)."""
        result = benchmark(benchmark_valid8r_int, 'not a number')
        assert result is None

    def it_benchmarks_pydantic_int_failure(self, benchmark) -> None:
        """Benchmark Pydantic integer parsing (failure)."""
        result = benchmark(benchmark_pydantic_int, 'not a number')
        assert result is None

    def it_benchmarks_marshmallow_int_failure(self, benchmark) -> None:
        """Benchmark marshmallow integer parsing (failure)."""
        result = benchmark(benchmark_marshmallow_int, 'not a number')
        assert result is None

    def it_benchmarks_cerberus_int_failure(self, benchmark) -> None:
        """Benchmark cerberus integer parsing (failure)."""
        result = benchmark(benchmark_cerberus_int, 'not a number')
        assert result is None


# =============================================================================
# Email Validation Benchmarks
# =============================================================================


class DescribeEmailValidation:
    """Benchmark email validation (success case)."""

    def it_benchmarks_valid8r_email_success(self, benchmark) -> None:
        """Benchmark valid8r email validation (success)."""
        result = benchmark(benchmark_valid8r_email, 'user@example.com')
        assert result is not None

    def it_benchmarks_pydantic_email_success(self, benchmark) -> None:
        """Benchmark Pydantic email validation (success)."""
        result = benchmark(benchmark_pydantic_email, 'user@example.com')
        assert result == 'user@example.com'

    def it_benchmarks_marshmallow_email_success(self, benchmark) -> None:
        """Benchmark marshmallow email validation (success)."""
        result = benchmark(benchmark_marshmallow_email, 'user@example.com')
        assert result == 'user@example.com'

    def it_benchmarks_cerberus_email_success(self, benchmark) -> None:
        """Benchmark cerberus email validation (success)."""
        result = benchmark(benchmark_cerberus_email, 'user@example.com')
        assert result == 'user@example.com'


class DescribeEmailValidationFailure:
    """Benchmark email validation (failure case)."""

    def it_benchmarks_valid8r_email_failure(self, benchmark) -> None:
        """Benchmark valid8r email validation (failure)."""
        result = benchmark(benchmark_valid8r_email, 'not-an-email')
        assert result is None

    def it_benchmarks_pydantic_email_failure(self, benchmark) -> None:
        """Benchmark Pydantic email validation (failure)."""
        result = benchmark(benchmark_pydantic_email, 'not-an-email')
        assert result is None

    def it_benchmarks_marshmallow_email_failure(self, benchmark) -> None:
        """Benchmark marshmallow email validation (failure)."""
        result = benchmark(benchmark_marshmallow_email, 'not-an-email')
        assert result is None

    def it_benchmarks_cerberus_email_failure(self, benchmark) -> None:
        """Benchmark cerberus email validation (failure)."""
        result = benchmark(benchmark_cerberus_email, 'not-an-email')
        assert result is None


# =============================================================================
# URL Validation Benchmarks
# =============================================================================


class DescribeUrlValidation:
    """Benchmark URL validation (success case)."""

    def it_benchmarks_valid8r_url_success(self, benchmark) -> None:
        """Benchmark valid8r URL validation (success)."""
        result = benchmark(benchmark_valid8r_url, 'https://example.com/path?query=value')
        assert result is not None

    def it_benchmarks_pydantic_url_success(self, benchmark) -> None:
        """Benchmark Pydantic URL validation (success)."""
        result = benchmark(benchmark_pydantic_url, 'https://example.com/path?query=value')
        assert result is not None

    def it_benchmarks_marshmallow_url_success(self, benchmark) -> None:
        """Benchmark marshmallow URL validation (success)."""
        result = benchmark(benchmark_marshmallow_url, 'https://example.com/path?query=value')
        assert result is not None

    def it_benchmarks_cerberus_url_success(self, benchmark) -> None:
        """Benchmark cerberus URL validation (success)."""
        result = benchmark(benchmark_cerberus_url, 'https://example.com/path?query=value')
        assert result is not None


class DescribeUrlValidationFailure:
    """Benchmark URL validation (failure case)."""

    def it_benchmarks_valid8r_url_failure(self, benchmark) -> None:
        """Benchmark valid8r URL validation (failure)."""
        result = benchmark(benchmark_valid8r_url, 'not a url')
        assert result is None

    def it_benchmarks_pydantic_url_failure(self, benchmark) -> None:
        """Benchmark Pydantic URL validation (failure)."""
        result = benchmark(benchmark_pydantic_url, 'not a url')
        assert result is None

    def it_benchmarks_marshmallow_url_failure(self, benchmark) -> None:
        """Benchmark marshmallow URL validation (failure)."""
        result = benchmark(benchmark_marshmallow_url, 'not a url')
        assert result is None

    def it_benchmarks_cerberus_url_failure(self, benchmark) -> None:
        """Benchmark cerberus URL validation (failure)."""
        result = benchmark(benchmark_cerberus_url, 'not a url')
        assert result is None


# =============================================================================
# Nested Object Validation Benchmarks
# =============================================================================


class DescribeNestedObjectValidation:
    """Benchmark nested object validation (success case)."""

    @pytest.fixture
    def valid_user_data(self):
        """Provide valid user data."""
        return {'name': 'John Doe', 'age': 30, 'email': 'john@example.com'}

    def it_benchmarks_valid8r_nested_success(self, benchmark, valid_user_data) -> None:
        """Benchmark valid8r nested object validation (success)."""
        result = benchmark(benchmark_valid8r_nested, valid_user_data)
        assert result is not None

    def it_benchmarks_pydantic_nested_success(self, benchmark, valid_user_data) -> None:
        """Benchmark Pydantic nested object validation (success)."""
        result = benchmark(benchmark_pydantic_nested, valid_user_data)
        assert result is not None

    def it_benchmarks_marshmallow_nested_success(self, benchmark, valid_user_data) -> None:
        """Benchmark marshmallow nested object validation (success)."""
        result = benchmark(benchmark_marshmallow_nested, valid_user_data)
        assert result is not None

    def it_benchmarks_cerberus_nested_success(self, benchmark, valid_user_data) -> None:
        """Benchmark cerberus nested object validation (success)."""
        result = benchmark(benchmark_cerberus_nested, valid_user_data)
        assert result is not None


class DescribeNestedObjectValidationFailure:
    """Benchmark nested object validation (failure case)."""

    @pytest.fixture
    def invalid_user_data(self):
        """Provide invalid user data (age is not an integer)."""
        return {'name': 'John Doe', 'age': 'not a number', 'email': 'john@example.com'}

    def it_benchmarks_valid8r_nested_failure(self, benchmark, invalid_user_data) -> None:
        """Benchmark valid8r nested object validation (failure)."""
        result = benchmark(benchmark_valid8r_nested, invalid_user_data)
        assert result is None

    def it_benchmarks_pydantic_nested_failure(self, benchmark, invalid_user_data) -> None:
        """Benchmark Pydantic nested object validation (failure)."""
        result = benchmark(benchmark_pydantic_nested, invalid_user_data)
        assert result is None

    def it_benchmarks_marshmallow_nested_failure(self, benchmark, invalid_user_data) -> None:
        """Benchmark marshmallow nested object validation (failure)."""
        result = benchmark(benchmark_marshmallow_nested, invalid_user_data)
        assert result is None

    def it_benchmarks_cerberus_nested_failure(self, benchmark, invalid_user_data) -> None:
        """Benchmark cerberus nested object validation (failure)."""
        result = benchmark(benchmark_cerberus_nested, invalid_user_data)
        assert result is None


# =============================================================================
# List Validation Benchmarks
# =============================================================================


class DescribeListValidation:
    """Benchmark list validation (success case with 100 items)."""

    @pytest.fixture
    def valid_list_data(self):
        """Provide list of 100 valid integers."""
        return [str(i) for i in range(100)]

    def it_benchmarks_valid8r_list_success(self, benchmark, valid_list_data) -> None:
        """Benchmark valid8r list validation (success, 100 items)."""
        result = benchmark(benchmark_valid8r_list, valid_list_data)
        assert result == list(range(100))

    def it_benchmarks_pydantic_list_success(self, benchmark, valid_list_data) -> None:
        """Benchmark Pydantic list validation (success, 100 items)."""
        result = benchmark(benchmark_pydantic_list, valid_list_data)
        assert result == list(range(100))

    def it_benchmarks_marshmallow_list_success(self, benchmark, valid_list_data) -> None:
        """Benchmark marshmallow list validation (success, 100 items)."""
        result = benchmark(benchmark_marshmallow_list, valid_list_data)
        assert result == list(range(100))

    def it_benchmarks_cerberus_list_success(self, benchmark, valid_list_data) -> None:
        """Benchmark cerberus list validation (success, 100 items)."""
        result = benchmark(benchmark_cerberus_list, valid_list_data)
        assert result == list(range(100))


class DescribeListValidationFailure:
    """Benchmark list validation (failure case - invalid item at position 50)."""

    @pytest.fixture
    def invalid_list_data(self):
        """Provide list with invalid item at position 50."""
        data = [str(i) for i in range(100)]
        data[50] = 'invalid'
        return data

    def it_benchmarks_valid8r_list_failure(self, benchmark, invalid_list_data) -> None:
        """Benchmark valid8r list validation (failure)."""
        result = benchmark(benchmark_valid8r_list, invalid_list_data)
        assert result is None

    def it_benchmarks_pydantic_list_failure(self, benchmark, invalid_list_data) -> None:
        """Benchmark Pydantic list validation (failure)."""
        result = benchmark(benchmark_pydantic_list, invalid_list_data)
        assert result is None

    def it_benchmarks_marshmallow_list_failure(self, benchmark, invalid_list_data) -> None:
        """Benchmark marshmallow list validation (failure)."""
        result = benchmark(benchmark_marshmallow_list, invalid_list_data)
        assert result is None

    def it_benchmarks_cerberus_list_failure(self, benchmark, invalid_list_data) -> None:
        """Benchmark cerberus list validation (failure)."""
        result = benchmark(benchmark_cerberus_list, invalid_list_data)
        assert result is None
