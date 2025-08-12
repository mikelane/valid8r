"""Tests for the testing utilities module."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

import pytest

from valid8r.core.maybe import Maybe
from valid8r.core.validators import (
    maximum,
    minimum,
)
from valid8r.prompt.basic import ask
from valid8r.testing import (
    assert_maybe_failure,
    assert_maybe_success,
    generate_random_inputs,
    generate_test_cases,
    test_validator_composition,
)
from valid8r.testing.mock_input import (
    MockInputContext,
    configure_mock_input,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


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
            assert result.value_or(0) == 42

        # Test with multiple inputs (simulating retry)
        with MockInputContext(['invalid', '42']):
            result = ask(
                'Enter a number: ',
                parser=lambda s: (Maybe.success(int(s)) if s.isdigit() else Maybe.failure('Not a number')),
                retry=True,
            )

            assert result.is_success()
            assert result.value_or(0) == 42

        # Test with validation failure
        with MockInputContext(['-5']):
            result = ask('Enter a positive number: ', parser=lambda s: Maybe.success(int(s)), validator=minimum(0))

            assert result.is_failure()
            assert 'must be at least 0' in result.error_or('')

    def it_raises_index_error_when_no_inputs_available(self) -> None:
        """Test that mock_input raises IndexError when no more inputs are available."""
        # Store original input function
        original_input = builtins.input

        try:
            # Configure with empty inputs list
            configure_mock_input([])

            # Should raise IndexError
            with pytest.raises(IndexError, match='No more mock inputs available'):
                builtins.input('Prompt: ')

            # Configure with one input, then use it up
            configure_mock_input(['test'])
            assert builtins.input('Prompt: ') == 'test'

            # Next call should raise IndexError
            with pytest.raises(IndexError, match='No more mock inputs available'):
                builtins.input('Prompt: ')
        finally:
            # Restore original input
            builtins.input = original_input

    def it_properly_restores_input_function_after_context_exit(self) -> None:
        """Test that MockInputContext properly restores the input function after exiting."""
        # Store original input function
        original_input = builtins.input

        # Use the context manager
        with MockInputContext(['mocked']):
            # Inside context, input should be mocked
            assert builtins.input('Prompt: ') == 'mocked'

            # Input function should be different
            assert builtins.input != original_input

        # After context exit, input should be restored
        assert builtins.input == original_input

        # Input function should work normally
        # We can't easily test this without actually getting user input,
        # but we can check it's the original function
        assert builtins.input is original_input

    def it_handles_exceptions_in_context(self) -> None:
        """Test that MockInputContext restores input even when exceptions occur."""
        # Store original input function
        original_input = builtins.input

        try:
            # Use context manager and raise exception inside
            with pytest.raises(ValueError, match='Test exception'), MockInputContext(['test']):  # noqa: PT012
                assert builtins.input('Prompt: ') == 'test'
                raise ValueError('Test exception')

            # Should have restored input function despite exception
            assert builtins.input == original_input
        finally:
            # Make sure we restore the original input
            builtins.input = original_input

    def it_makes_a_copy_of_the_inputs_list(self) -> None:
        """Test that MockInputContext and configure_mock_input make a copy of the inputs list."""
        # Create a list that we'll modify after configuration
        inputs = ['first', 'second']

        # Store original input function
        original_input = builtins.input

        try:
            # Configure mock input with our list
            configure_mock_input(inputs)

            # Modify the original list
            inputs.clear()
            inputs.append('modified')

            # Mock input should still have the original values
            assert builtins.input('Prompt: ') == 'first'
            assert builtins.input('Prompt: ') == 'second'

            # Test context manager also copies the list
            inputs = ['contextA', 'contextB']

            with MockInputContext(inputs):
                # Modify original list
                inputs.clear()

                # Input should still have original values
                assert builtins.input('Prompt: ') == 'contextA'
                assert builtins.input('Prompt: ') == 'contextB'
        finally:
            # Restore original input
            builtins.input = original_input

    def it_handles_input_prompt_parameter(self) -> None:
        """Test that the mock input function handles the prompt parameter.

        This tests the behavior where the prompt parameter exists but is ignored.
        """
        # Store original input function
        original_input = builtins.input

        try:
            # Configure mock input
            configure_mock_input(['test response'])

            # The mock input should ignore the prompt parameter
            # but we'll pass one anyway to test the coverage
            result = builtins.input('This prompt will be ignored: ')

            # Verify behavior
            assert result == 'test response'

            # Try with a different prompt to make sure it's truly ignored
            with pytest.raises(IndexError):  # No more inputs left
                builtins.input('A different prompt: ')

        finally:
            # Restore original input
            builtins.input = original_input

    def it_displays_prompt_for_context_manager(self, mocker: MockerFixture) -> None:
        """Test that the context manager ignores the prompt but accepts it."""
        # Create a spy to check if the prompt was displayed
        stdout_spy = mocker.MagicMock()
        mocker.patch('builtins.print', stdout_spy)

        # Store original functions
        original_input = builtins.input

        try:
            with MockInputContext(['test response']):
                result = input('Prompt that will be ignored: ')
                assert result == 'test response'

                # The prompt shouldn't be printed
                stdout_spy.assert_not_called()

        finally:
            # Restore original functions
            builtins.input = original_input

    def it_raises_index_error_with_empty_inputs_in_context(self) -> None:
        """Test that MockInputContext raises IndexError when inputs list is empty."""
        # Create a context with an empty list of inputs
        with MockInputContext([]), pytest.raises(IndexError, match='No more mock inputs available'):
            input('This should raise an error')
