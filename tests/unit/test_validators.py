"""Tests for the validator functions."""

from __future__ import annotations

import re
from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest

from valid8r.core.validators import (
    Validator,
    between,
    in_set,
    is_sorted,
    length,
    matches_regex,
    maximum,
    minimum,
    non_empty_string,
    predicate,
    subset_of,
    superset_of,
    unique_items,
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
            pytest.param(3, 10, 'hello', True, id='valid string'),
            pytest.param(3, 10, 'abc', True, id='valid string with length 3'),
            pytest.param(3, 10, 'helloworld', True, id='valid string with length 10'),
            pytest.param(3, 10, 'hi', False, id='invalid string with length 2'),
            pytest.param(3, 10, 'helloworldplus', False, id='invalid string with length 11'),
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


class DescribeMatchesRegex:
    """Tests for the matches_regex validator."""

    def it_validates_string_matching_pattern(self) -> None:
        """Test matches_regex accepts a string matching the pattern."""
        validator = matches_regex(r'^\d{3}-\d{2}-\d{4}$')

        result = validator('123-45-6789')

        assert result.is_success()
        assert result.value_or('') == '123-45-6789'

    def it_rejects_string_not_matching_pattern(self) -> None:
        """Test matches_regex rejects a string that doesn't match the pattern."""
        validator = matches_regex(r'^\d{3}-\d{2}-\d{4}$')

        result = validator('abc-de-fghi')

        assert result.is_failure()
        assert 'must match pattern' in result.error_or('').lower()

    def it_accepts_compiled_regex_pattern(self) -> None:
        """Test matches_regex works with pre-compiled regex patterns."""
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
        validator = matches_regex(pattern)

        result = validator('123-456-7890')

        assert result.is_success()
        assert result.value_or('') == '123-456-7890'

    def it_supports_custom_error_messages(self) -> None:
        """Test matches_regex uses custom error message when provided."""
        validator = matches_regex(r'^\d{5}$', error_message='Must be a 5-digit ZIP code')

        result = validator('1234')

        assert result.is_failure()
        assert result.error_or('') == 'Must be a 5-digit ZIP code'


class DescribeInSet:
    """Tests for the in_set validator."""

    def it_accepts_value_in_allowed_set(self) -> None:
        """Test in_set accepts a value that is in the allowed set."""
        validator = in_set({'red', 'green', 'blue'})

        result = validator('red')

        assert result.is_success()
        assert result.value_or('') == 'red'

    def it_rejects_value_not_in_allowed_set(self) -> None:
        """Test in_set rejects a value that is not in the allowed set."""
        validator = in_set({'red', 'green', 'blue'})

        result = validator('yellow')

        assert result.is_failure()
        assert 'must be one of' in result.error_or('').lower()

    def it_supports_custom_error_messages(self) -> None:
        """Test in_set uses custom error message when provided."""
        validator = in_set({'small', 'medium', 'large'}, error_message='Size must be S, M, or L')

        result = validator('extra-large')

        assert result.is_failure()
        assert result.error_or('') == 'Size must be S, M, or L'


class DescribeNonEmptyString:
    """Tests for the non_empty_string validator."""

    def it_accepts_non_empty_string(self) -> None:
        """Test non_empty_string accepts a string with content."""
        validator = non_empty_string()

        result = validator('hello')

        assert result.is_success()
        assert result.value_or('') == 'hello'

    def it_rejects_empty_string(self) -> None:
        """Test non_empty_string rejects an empty string."""
        validator = non_empty_string()

        result = validator('')

        assert result.is_failure()
        assert 'must not be empty' in result.error_or('').lower()

    def it_rejects_whitespace_only_string(self) -> None:
        """Test non_empty_string rejects a string with only whitespace."""
        validator = non_empty_string()

        result = validator('   ')

        assert result.is_failure()
        assert 'must not be empty' in result.error_or('').lower()


class DescribeUniqueItems:
    """Tests for the unique_items validator."""

    def it_accepts_list_with_unique_items(self) -> None:
        """Test unique_items accepts a list where all items are unique."""
        validator = unique_items()

        result = validator([1, 2, 3, 4, 5])

        assert result.is_success()
        assert result.value_or([]) == [1, 2, 3, 4, 5]

    def it_rejects_list_with_duplicate_items(self) -> None:
        """Test unique_items rejects a list with duplicate items."""
        validator = unique_items()

        result = validator([1, 2, 2, 3, 4])

        assert result.is_failure()
        assert 'must be unique' in result.error_or('').lower()


class DescribeSubsetOf:
    """Tests for the subset_of validator."""

    def it_accepts_set_that_is_subset(self) -> None:
        """Test subset_of accepts a set that is a subset of the allowed set."""
        validator = subset_of({1, 2, 3, 4, 5})

        result = validator({1, 2, 3})

        assert result.is_success()
        assert result.value_or(set()) == {1, 2, 3}

    def it_rejects_set_that_is_not_subset(self) -> None:
        """Test subset_of rejects a set that is not a subset of the allowed set."""
        validator = subset_of({1, 2, 3})

        result = validator({1, 2, 3, 4, 5})

        assert result.is_failure()
        assert 'subset' in result.error_or('').lower()


class DescribeSupersetOf:
    """Tests for the superset_of validator."""

    def it_accepts_set_that_is_superset(self) -> None:
        """Test superset_of accepts a set that is a superset of the required set."""
        validator = superset_of({1, 2, 3})

        result = validator({1, 2, 3, 4, 5})

        assert result.is_success()
        assert result.value_or(set()) == {1, 2, 3, 4, 5}

    def it_rejects_set_that_is_not_superset(self) -> None:
        """Test superset_of rejects a set that is not a superset of the required set."""
        validator = superset_of({1, 2, 3, 4, 5})

        result = validator({1, 2, 3})

        assert result.is_failure()
        assert 'superset' in result.error_or('').lower()


class DescribeIsSorted:
    """Tests for the is_sorted validator."""

    def it_accepts_ascending_sorted_list(self) -> None:
        """Test is_sorted accepts a list sorted in ascending order."""
        validator = is_sorted()

        result = validator([1, 2, 3, 4, 5])

        assert result.is_success()
        assert result.value_or([]) == [1, 2, 3, 4, 5]

    def it_rejects_unsorted_list(self) -> None:
        """Test is_sorted rejects an unsorted list."""
        validator = is_sorted()

        result = validator([3, 1, 4, 2, 5])

        assert result.is_failure()
        assert 'sorted' in result.error_or('').lower()

    def it_accepts_descending_sorted_list_when_reverse_true(self) -> None:
        """Test is_sorted accepts descending order when reverse=True."""
        validator = is_sorted(reverse=True)

        result = validator([5, 4, 3, 2, 1])

        assert result.is_success()
        assert result.value_or([]) == [5, 4, 3, 2, 1]
