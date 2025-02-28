"""Tests for the testing utilities module."""

from __future__ import annotations

from valid8r.core.maybe import Maybe
from valid8r.core.validators import (
    maximum,
    minimum,
)
from valid8r.prompt.basic import ask
from valid8r.testing import (
    MockInputContext,
    assert_maybe_failure,
    assert_maybe_success,
    configure_mock_input,
    generate_random_inputs,
    generate_test_cases,
    test_validator_composition,
)


class DescribeTestingUtilities:
    def it_mocks_user_input(self) -> None:
        """Test that MockInputContext correctly mocks user input."""
        with MockInputContext(['42']):
            result = input('Enter something: ')
            assert result == '42'

    def it_configures_mock_input_globally(self) -> None:
        """Test configure_mock_input for global input mocking."""
        configure_mock_input(['hello', 'world'])
        result1 = input('First: ')
        result2 = input('Second: ')
        assert result1 == 'hello'
        assert result2 == 'world'

    def it_asserts_maybe_success(self) -> None:
        """Test that assert_maybe_success correctly verifies success cases."""
        success_result = Maybe.success(42)
        assert assert_maybe_success(success_result, 42) is True

        # Should fail for wrong value
        success_result_wrong_value = Maybe.success(43)
        assert assert_maybe_success(success_result_wrong_value, 42) is False

        # Should fail for Failure
        failure_result = Maybe.failure('Error')
        assert assert_maybe_success(failure_result, 42) is False

    def it_asserts_maybe_failure(self) -> None:
        """Test that assert_maybe_failure correctly verifies failure cases."""
        failure_result = Maybe.failure('Error message')
        assert assert_maybe_failure(failure_result, 'Error message') is True

        # Should fail for wrong error message
        failure_result_wrong_msg = Maybe.failure('Different error')
        assert assert_maybe_failure(failure_result_wrong_msg, 'Error message') is False

        # Should fail for Success
        success_result = Maybe.success(42)
        assert assert_maybe_failure(success_result, 'Any message') is False

    def it_generates_test_cases_for_validators(self) -> None:
        """Test that generate_test_cases produces appropriate test cases."""
        # Test for minimum validator
        min_validator = minimum(10)
        test_cases = generate_test_cases(min_validator)

        assert 'valid' in test_cases
        assert 'invalid' in test_cases
        assert len(test_cases['valid']) > 0
        assert len(test_cases['invalid']) > 0

        # All valid cases should be >= 10
        for case in test_cases['valid']:
            assert case >= 10

        # All invalid cases should be < 10
        for case in test_cases['invalid']:
            assert case < 10

    def it_tests_validator_composition(self) -> None:
        """Test that test_validator_composition verifies composed validators."""
        # Test a range validator (between 10 and 20)
        range_validator = minimum(10) & maximum(20)
        assert test_validator_composition(range_validator) is True

        # It should test various cases internally
        # We're just testing that it returns the expected result here

    def it_generates_random_inputs(self) -> None:
        """Test that generate_random_inputs creates diverse test cases."""
        validator = minimum(0)
        inputs = generate_random_inputs(validator, count=20)

        assert len(inputs) == 20

        # There should be a mix of valid and invalid inputs
        valid = [i for i in inputs if validator(i).is_success()]
        invalid = [i for i in inputs if validator(i).is_failure()]

        assert len(valid) > 0, 'Should have at least one valid input'
        assert len(invalid) > 0, 'Should have at least one invalid input'

    def it_tests_prompt_functions(self) -> None:
        """Test that MockInputContext works with prompt functions."""
        # Test with success case
        with MockInputContext(['42']):
            result = ask('Enter a number: ', parser=lambda s: Maybe.success(int(s)))

            assert result.is_success()
            assert result.value_or('FAIL') == 42

        # Test with multiple inputs (simulating retry)
        with MockInputContext(['invalid', '42']):
            result = ask(
                'Enter a number: ',
                parser=lambda s: (Maybe.success(int(s)) if s.isdigit() else Maybe.failure('Not a number')),
                retry=True,
            )

            assert result.is_success()
            assert result.value_or('FAIL') == 42

        # Test with validation failure
        with MockInputContext(['-5']):
            result = ask('Enter a positive number: ', parser=lambda s: Maybe.success(int(s)), validator=minimum(0))

            assert result.is_failure()
            assert 'must be at least 0' in result.value_or('FAIL')
