"""Tests for the generators module to improve coverage."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)
from unittest import mock

from valid8r.core.maybe import Maybe
from valid8r.core.validators import (
    Validator,
    between,
    maximum,
    predicate,
)
from valid8r.testing.generators import (
    _extract_numeric_value_from_closure,
    _extract_two_numeric_values,
    _generate_between_validator_cases,
    _generate_maximum_validator_cases,
    _identify_validator_type,
    generate_random_inputs,
    generate_test_cases,
    test_validator_composition,
)

if TYPE_CHECKING:
    from types import CellType


class DescribeGeneratorsModule:
    def it_returns_none_when_no_numeric_value_in_closure(self) -> None:
        """Test that _extract_numeric_value_from_closure returns None when no numeric value is found."""

        # Create a closure with non-numeric values
        def create_closure_with_string() -> list[CellType]:
            string_value = 'test'

            def inner_func() -> str:
                return string_value

            return inner_func.__closure__

        closure = create_closure_with_string()
        result = _extract_numeric_value_from_closure(closure)
        assert result is None

    def it_generates_maximum_validator_cases(self) -> None:
        """Test that _generate_maximum_validator_cases returns appropriate test cases."""
        valid_cases, invalid_cases = _generate_maximum_validator_cases(10)

        # Check valid cases
        assert 10 in valid_cases  # Boundary value
        assert any(x < 10 for x in valid_cases)  # Values below maximum

        # Check invalid cases
        assert all(x > 10 for x in invalid_cases)  # All invalid cases should be above maximum

    def it_generates_between_validator_cases(self) -> None:
        """Test that _generate_between_validator_cases returns appropriate test cases."""
        valid_cases, invalid_cases = _generate_between_validator_cases(5, 15)

        # Check valid cases
        assert 5 in valid_cases  # Min boundary
        assert 15 in valid_cases  # Max boundary
        assert any(5 < x < 15 for x in valid_cases)  # Values between boundaries

        # Check invalid cases
        assert any(x < 5 for x in invalid_cases)  # Values below min
        assert any(x > 15 for x in invalid_cases)  # Values above max

    def it_identifies_validator_without_closure(self) -> None:
        """Test that _identify_validator_type handles validators without a closure."""

        # Create a validator without a closure
        def validator_func(x: int) -> Maybe[int]:
            return Maybe.success(x)

        validator = Validator(validator_func)

        validator_type, param1, param2 = _identify_validator_type(validator)
        assert validator_type == 'unknown'
        assert param1 is None
        assert param2 is None

    def it_identifies_maximum_validator(self) -> None:
        """Test that _identify_validator_type correctly identifies maximum validators."""
        max_validator = maximum(100)
        validator_type, param1, param2 = _identify_validator_type(max_validator)

        assert validator_type == 'maximum'
        assert param1 == 100
        assert param2 is None

    def it_identifies_between_validator(self) -> None:
        """Test that _identify_validator_type correctly identifies between validators."""
        between_validator = between(10, 50)
        validator_type, param1, param2 = _identify_validator_type(between_validator)

        assert validator_type == 'between'
        # The order of parameters in the closure depends on implementation details
        # Verify we extracted both values, regardless of order
        assert {param1, param2} == {10, 50}
        # Make sure min value and max value are both present
        assert min(param1, param2) == 10
        assert max(param1, param2) == 50

    def it_extracts_two_numeric_values(self) -> None:
        """Test that _extract_two_numeric_values extracts two numeric values from a closure."""

        def create_closure_with_two_numbers() -> list[CellType]:
            first_value = 10
            second_value = 20

            def inner_func() -> tuple[int, int]:
                return first_value, second_value

            return inner_func.__closure__

        closure = create_closure_with_two_numbers()
        first, second = _extract_two_numeric_values(closure)

        assert first == 10
        assert second == 20

    def it_handles_not_enough_values_in_extract_two_numeric_values(self) -> None:
        """Test that _extract_two_numeric_values handles cases with fewer than 2 numeric values."""

        def create_closure_with_one_number() -> list[CellType]:
            first_value = 10

            def inner_func() -> int:
                return first_value

            return inner_func.__closure__

        closure = create_closure_with_one_number()
        first, second = _extract_two_numeric_values(closure)

        assert first is None
        assert second is None

    def it_generates_test_cases_for_maximum_validator(self) -> None:
        """Test that generate_test_cases works with maximum validators."""
        max_validator = maximum(50)
        test_cases = generate_test_cases(max_validator)

        assert 'valid' in test_cases
        assert 'invalid' in test_cases

        # Check that valid cases are all <= 50
        assert all(x <= 50 for x in test_cases['valid'])

        # Check that invalid cases are all > 50
        assert all(x > 50 for x in test_cases['invalid'])

    def it_generates_test_cases_for_between_validator(self) -> None:
        """Test that generate_test_cases works with between validators."""
        between_validator = between(10, 20)
        test_cases = generate_test_cases(between_validator)

        assert 'valid' in test_cases
        assert 'invalid' in test_cases

        # Check that valid cases are all within range
        assert all(10 <= x <= 20 for x in test_cases['valid'])

        # Check that invalid cases are all outside range
        assert all(x < 10 or x > 20 for x in test_cases['invalid'])

    def it_adds_specific_cases_when_random_inputs_lack_valid_cases(self) -> None:
        """Test that generate_random_inputs adds valid cases when they're missing."""
        # Create a validator that only accepts a specific value
        specific_validator = predicate(lambda x: x == 42, 'Value must be 42')

        # Mock generate_test_cases to return our known test cases
        mock_test_cases = {
            'valid': [42],  # The only value that will pass
            'invalid': [43, 44, 45],
        }

        with (
            mock.patch('valid8r.testing.generators.generate_test_cases', return_value=mock_test_cases),
            mock.patch('random.randint', return_value=43),
        ):
            # This ensures all randomly generated values will fail
            # Force the generator to use our mock test cases for valid values
            inputs = generate_random_inputs(specific_validator, count=5)

            # Now we should have at least one valid case (42) in the inputs
            assert any(specific_validator(x).is_success() for x in inputs), 'No valid inputs were added'

            # Verify the specific value was added
            assert 42 in inputs

    def it_adds_specific_cases_when_random_inputs_lack_invalid_cases(self) -> None:
        """Test that generate_random_inputs adds invalid cases when they're missing."""

        # Create a validator that fails only for a specific value
        def rigged_validator(x: int) -> Maybe[int]:
            if x == -9999:
                return Maybe.failure('Rigged to fail')
            return Maybe.success(x)

        rigged = Validator(rigged_validator)

        # Mock generate_test_cases to return our known test cases
        mock_test_cases = {
            'valid': [10, 20, 30],
            'invalid': [-9999],  # The only value that will fail
        }

        with (
            mock.patch('valid8r.testing.generators.generate_test_cases', return_value=mock_test_cases),
            mock.patch('random.randint', return_value=100),
        ):
            # This ensures all randomly generated values will pass
            # Force the generator to use our mock test cases for invalid values
            inputs = generate_random_inputs(rigged, count=5)

            # Now we should have at least one invalid case (-9999) in the inputs
            assert any(rigged(x).is_failure() for x in inputs), 'No invalid inputs were added'

            # Verify the specific value was added
            assert -9999 in inputs

    def it_returns_false_when_valid_case_fails_in_test_validator_composition(self) -> None:
        """Test that test_validator_composition returns False when a valid case fails."""

        # Create a validator with inconsistent behavior
        class InconsistentValidator(Validator[int]):
            def __init__(self) -> None:
                self.call_count = 0
                super().__init__(self._validate)

            def _validate(self, value: int) -> Maybe[int]:
                self.call_count += 1
                # First call return success, second call return failure
                if self.call_count % 2 == 1:
                    return Maybe.success(value)
                return Maybe.failure('Inconsistent failure')

        inconsistent = InconsistentValidator()

        # This should return False since the validator is inconsistent
        assert test_validator_composition(inconsistent) is False

    def it_returns_false_when_invalid_case_succeeds_in_test_validator_composition(self) -> None:
        """Test that test_validator_composition returns False when an invalid case succeeds."""

        # Create a validator that incorrectly accepts negative values
        def always_succeed(value: int) -> Maybe[int]:
            return Maybe.success(value)

        broken_validator = Validator(always_succeed)

        # Mock generate_test_cases to return our controlled test data
        mock_test_cases = {
            'valid': [0, 10, 20],
            'invalid': [-10, -20],  # These should fail but won't with our broken validator
        }

        # Use proper patching to ensure the function under test uses our mock
        with mock.patch('valid8r.testing.generators.generate_test_cases', return_value=mock_test_cases):
            # Should return False since invalid cases succeed
            result = test_validator_composition(broken_validator)
            assert result is False, 'test_validator_composition should return False when invalid cases pass validation'
