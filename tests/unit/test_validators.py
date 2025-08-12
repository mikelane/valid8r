"""Tests for the validator functions."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest

from valid8r.core.validators import (
    Validator,
    between,
    length,
    maximum,
    minimum,
    predicate,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class DescribeValidators:
    @pytest.mark.parametrize(
        ('validator_factory', 'threshold', 'test_values', 'expected_results'),
        [
            pytest.param(
                minimum,
                5,
                [(10, True), (5, True), (4, False), (0, False)],
                'Value must be at least 5',
                id='minimum validator',
            ),
            pytest.param(
                maximum,
                10,
                [(5, True), (10, True), (11, False), (20, False)],
                'Value must be at most 10',
                id='maximum validator',
            ),
        ],
    )
    def it_validates_threshold_values(
        self,
        validator_factory: Callable[[Any], Validator[Any]],
        threshold: int,
        test_values: list[tuple[Any, bool]],
        expected_results: str,
    ) -> None:
        """Test threshold-based validators (minimum and maximum)."""
        validator = validator_factory(threshold)

        for value, should_pass in test_values:
            result = validator(value)

            if should_pass:
                assert result.is_success()
                assert result.value_or(value) == value
            else:
                assert result.is_failure()
                assert result.error_or('') == expected_results

    @pytest.mark.parametrize(
        ('min_val', 'max_val', 'test_value', 'should_pass'),
        [
            pytest.param(1, 10, 5, True, id='in range'),
            pytest.param(1, 10, 1, True, id='min value'),
            pytest.param(1, 10, 10, True, id='max value'),
            pytest.param(1, 10, 0, False, id='below range'),
            pytest.param(1, 10, 11, False, id='above range'),
        ],
    )
    def it_validates_range_with_between(
        self,
        min_val: int,
        max_val: int,
        test_value: int,
        should_pass: bool,
    ) -> None:
        """Test the between validator with various inputs."""
        validator = between(min_val, max_val)
        result = validator(test_value)

        if should_pass:
            assert result.is_success()
            assert result.value_or(test_value) == test_value
        else:
            assert result.is_failure()
            assert f'Value must be between {min_val} and {max_val}' in result.error_or('')

    def it_validates_custom_predicates(self) -> None:
        """Test predicate validator with custom functions."""
        is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')

        # Test valid case
        result = is_even(4)
        assert result.is_success()
        assert result.value_or(0) == 4

        # Test invalid case
        result = is_even(3)
        assert result.is_failure()
        assert result.error_or('') == 'Value must be even'

    @pytest.mark.parametrize(
        ('min_len', 'max_len', 'test_string', 'should_pass'),
        [
            (3, 10, 'hello', True),
            (3, 10, 'abc', True),
            (3, 10, 'helloworld', True),
            (3, 10, 'hi', False),
            (3, 10, 'helloworldplus', False),
        ],
    )
    def it_validates_string_length(
        self,
        min_len: int,
        max_len: int,
        test_string: str,
        should_pass: bool,
    ) -> None:
        """Test the length validator with various inputs."""
        validator = length(min_len, max_len)
        result = validator(test_string)

        if should_pass:
            assert result.is_success()
            assert result.value_or('') == test_string
        else:
            assert result.is_failure()
            assert f'String length must be between {min_len} and {max_len}' in result.error_or('')
