"""Tests to ensure benchmarks are measuring what they claim to measure.

This module validates that benchmark scenarios are correctly implemented
and produce expected results for all libraries being compared.
"""

from __future__ import annotations


class DescribeBenchmarkCorrectness:
    """Validate benchmark scenarios produce correct results."""

    def it_validates_basic_int_parsing_success(self) -> None:
        """All libraries correctly parse valid integers."""
        from benchmarks.scenarios import (
            benchmark_cerberus_int,
            benchmark_marshmallow_int,
            benchmark_pydantic_int,
            benchmark_valid8r_int,
        )

        # All should successfully parse "42"
        assert benchmark_valid8r_int('42') == 42
        assert benchmark_pydantic_int('42') == 42
        assert benchmark_marshmallow_int('42') == 42
        assert benchmark_cerberus_int('42') == 42

    def it_validates_basic_int_parsing_failure(self) -> None:
        """All libraries correctly reject invalid integers."""
        from benchmarks.scenarios import (
            benchmark_cerberus_int,
            benchmark_marshmallow_int,
            benchmark_pydantic_int,
            benchmark_valid8r_int,
        )

        # All should fail to parse "not a number"
        assert benchmark_valid8r_int('not a number') is None
        assert benchmark_pydantic_int('not a number') is None
        assert benchmark_marshmallow_int('not a number') is None
        assert benchmark_cerberus_int('not a number') is None

    def it_validates_email_parsing_success(self) -> None:
        """All libraries correctly parse valid email addresses."""
        from benchmarks.scenarios import (
            benchmark_cerberus_email,
            benchmark_marshmallow_email,
            benchmark_pydantic_email,
            benchmark_valid8r_email,
        )

        email = 'user@example.com'
        # All should successfully parse the email
        assert benchmark_valid8r_email(email) is not None
        assert benchmark_pydantic_email(email) == email
        assert benchmark_marshmallow_email(email) == email
        assert benchmark_cerberus_email(email) == email

    def it_validates_email_parsing_failure(self) -> None:
        """All libraries correctly reject invalid email addresses."""
        from benchmarks.scenarios import (
            benchmark_cerberus_email,
            benchmark_marshmallow_email,
            benchmark_pydantic_email,
            benchmark_valid8r_email,
        )

        invalid_email = 'not-an-email'
        # All should fail to parse invalid email
        assert benchmark_valid8r_email(invalid_email) is None
        assert benchmark_pydantic_email(invalid_email) is None
        assert benchmark_marshmallow_email(invalid_email) is None
        assert benchmark_cerberus_email(invalid_email) is None

    def it_validates_url_parsing_success(self) -> None:
        """All libraries correctly parse valid URLs."""
        from benchmarks.scenarios import (
            benchmark_cerberus_url,
            benchmark_marshmallow_url,
            benchmark_pydantic_url,
            benchmark_valid8r_url,
        )

        url = 'https://example.com/path?query=value'
        # All should successfully parse the URL
        assert benchmark_valid8r_url(url) is not None
        assert benchmark_pydantic_url(url) is not None
        assert benchmark_marshmallow_url(url) == url
        assert benchmark_cerberus_url(url) == url

    def it_validates_url_parsing_failure(self) -> None:
        """All libraries correctly reject invalid URLs."""
        from benchmarks.scenarios import (
            benchmark_cerberus_url,
            benchmark_marshmallow_url,
            benchmark_pydantic_url,
            benchmark_valid8r_url,
        )

        invalid_url = 'not a url'
        # All should fail to parse invalid URL
        assert benchmark_valid8r_url(invalid_url) is None
        assert benchmark_pydantic_url(invalid_url) is None
        assert benchmark_marshmallow_url(invalid_url) is None
        assert benchmark_cerberus_url(invalid_url) is None

    def it_validates_nested_object_parsing_success(self) -> None:
        """All libraries correctly parse nested objects."""
        from benchmarks.scenarios import (
            benchmark_cerberus_nested,
            benchmark_marshmallow_nested,
            benchmark_pydantic_nested,
            benchmark_valid8r_nested,
        )

        data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
        # All should successfully parse nested data
        assert benchmark_valid8r_nested(data) is not None
        assert benchmark_pydantic_nested(data) is not None
        assert benchmark_marshmallow_nested(data) is not None
        assert benchmark_cerberus_nested(data) is not None

    def it_validates_nested_object_parsing_failure(self) -> None:
        """All libraries correctly reject invalid nested objects."""
        from benchmarks.scenarios import (
            benchmark_cerberus_nested,
            benchmark_marshmallow_nested,
            benchmark_pydantic_nested,
            benchmark_valid8r_nested,
        )

        # Invalid: age is not an integer
        data = {'name': 'John', 'age': 'not a number', 'email': 'john@example.com'}
        # All should fail to parse invalid nested data
        assert benchmark_valid8r_nested(data) is None
        assert benchmark_pydantic_nested(data) is None
        assert benchmark_marshmallow_nested(data) is None
        assert benchmark_cerberus_nested(data) is None

    def it_validates_list_parsing_success(self) -> None:
        """All libraries correctly parse lists of integers."""
        from benchmarks.scenarios import (
            benchmark_cerberus_list,
            benchmark_marshmallow_list,
            benchmark_pydantic_list,
            benchmark_valid8r_list,
        )

        data = ['1', '2', '3', '4', '5']
        # All should successfully parse list
        assert benchmark_valid8r_list(data) == [1, 2, 3, 4, 5]
        assert benchmark_pydantic_list(data) == [1, 2, 3, 4, 5]
        assert benchmark_marshmallow_list(data) == [1, 2, 3, 4, 5]
        assert benchmark_cerberus_list(data) == [1, 2, 3, 4, 5]

    def it_validates_list_parsing_failure(self) -> None:
        """All libraries correctly reject lists with invalid items."""
        from benchmarks.scenarios import (
            benchmark_cerberus_list,
            benchmark_marshmallow_list,
            benchmark_pydantic_list,
            benchmark_valid8r_list,
        )

        data = ['1', 'not a number', '3']
        # All should fail to parse list with invalid item
        assert benchmark_valid8r_list(data) is None
        assert benchmark_pydantic_list(data) is None
        assert benchmark_marshmallow_list(data) is None
        assert benchmark_cerberus_list(data) is None


class DescribeBenchmarkDeterminism:
    """Ensure benchmarks are deterministic and repeatable."""

    def it_produces_consistent_results_for_valid8r_int(self) -> None:
        """Valid8r int parsing produces same result on repeated calls."""
        from benchmarks.scenarios import benchmark_valid8r_int

        results = [benchmark_valid8r_int('42') for _ in range(100)]
        assert all(r == 42 for r in results)

    def it_produces_consistent_results_for_pydantic_int(self) -> None:
        """Pydantic int parsing produces same result on repeated calls."""
        from benchmarks.scenarios import benchmark_pydantic_int

        results = [benchmark_pydantic_int('42') for _ in range(100)]
        assert all(r == 42 for r in results)

    def it_produces_consistent_results_for_valid8r_failures(self) -> None:
        """Valid8r failure handling is consistent."""
        from benchmarks.scenarios import benchmark_valid8r_int

        results = [benchmark_valid8r_int('invalid') for _ in range(100)]
        assert all(r is None for r in results)

    def it_produces_consistent_results_for_pydantic_failures(self) -> None:
        """Pydantic failure handling is consistent."""
        from benchmarks.scenarios import benchmark_pydantic_int

        results = [benchmark_pydantic_int('invalid') for _ in range(100)]
        assert all(r is None for r in results)
