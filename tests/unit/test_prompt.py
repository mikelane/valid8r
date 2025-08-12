"""Tests for the prompt/basic.py module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from valid8r.core.maybe import (
    Maybe,
)
from valid8r.core.parsers import parse_int
from valid8r.prompt.basic import (
    PromptConfig,
    _ask_with_config,
    _display_error,
    _handle_user_input,
    _process_input,
    _run_prompt_loop,
    ask,
)

if TYPE_CHECKING:
    from pytest_mock import (
        MockerFixture,
        MockType,
    )


@pytest.fixture
def mock_input(mocker: MockerFixture) -> MockType:
    """Mock the builtins.input function."""
    return mocker.patch('builtins.input')


@pytest.fixture
def mock_print(mocker: MockerFixture) -> MockType:
    """Mock the builtins.print function."""
    return mocker.patch('builtins.print')


@pytest.fixture(autouse=True)
def setup_input_scenario(request: pytest.FixtureRequest, mock_input: MockType) -> None:
    """Set up input mock based on the parameter."""
    if hasattr(request, 'param'):
        mock_input.side_effect = request.param


class DescribePrompt:
    def it_handles_successful_input(self, mock_input: MockType, mock_print: MockType) -> None:
        """Test successful input handling."""
        mock_input.return_value = '42'

        result = ask('Enter a number: ', parser=parse_int)

        mock_input.assert_called_once_with('Enter a number: ')
        assert result.is_success()
        assert result.value_or(0) == 42
        mock_print.assert_not_called()

    def it_handles_empty_input_with_default(self, mock_input: MockType, mock_print: MockType) -> None:
        """Test empty input with default value."""
        mock_input.return_value = ''

        result = ask('Enter a number: ', parser=parse_int, default=10)

        mock_input.assert_called_once_with('Enter a number:  [10]: ')
        assert result.is_success()
        assert result.value_or(0) == 10
        mock_print.assert_not_called()

    @pytest.mark.parametrize(
        ('setup_input_scenario', 'max_retries'),
        [
            pytest.param(['invalid'], 0, id='no retries'),
            pytest.param(['invalid', 'still-invalid', 'not-a-number'], 2, id='max retries'),
        ],
        indirect=['setup_input_scenario'],
    )
    def it_returns_nothing_for_failed_prompts(
        self,
        max_retries: int,
    ) -> None:
        """Test prompt failure cases."""
        result = ask('Enter a number: ', parser=parse_int, retry=max_retries)

        assert result.is_failure()
        assert 'Input must be a valid integer' in result.error_or('')

    @pytest.mark.parametrize(
        ('setup_input_scenario', 'max_retries', 'expected_value'),
        [
            pytest.param(['invalid', '42'], 1, 42, id='valid input after retries'),
        ],
        indirect=['setup_input_scenario'],
    )
    def it_returns_just_for_successful_prompts(
        self,
        max_retries: int,
        expected_value: int,
    ) -> None:
        """Test prompt success cases after retries."""
        result = ask('Enter a number: ', parser=parse_int, retry=max_retries)

        assert result.is_success()
        assert result.value_or(0) == expected_value

    @pytest.mark.parametrize(
        ('setup_input_scenario', 'max_retries'),
        [
            pytest.param(['invalid'], -1, id='negative retries - immediate exit'),
        ],
        indirect=['setup_input_scenario'],
    )
    def it_returns_nothing_when_loop_exits_immediately(self, max_retries: int) -> None:
        """Test when loop exits immediately due to negative max_retries."""
        result = ask('Enter a number: ', parser=parse_int, retry=max_retries)

        assert result.is_failure()
        assert 'Maximum retry attempts reached' in result.error_or('')

    def it_tests_display_error_different_retry_modes(self, mock_print: MockType) -> None:
        """Test error display behavior with different retry modes."""
        # Import the function we need to test
        from valid8r.prompt.basic import _display_error

        # Test with finite retries - should show "remaining"
        _display_error('Test error', None, 5, 2)
        mock_print.assert_called_once()
        assert 'remaining' in mock_print.call_args[0][0]

        # Reset mock
        mock_print.reset_mock()

        # Test with infinite retries - should NOT show "remaining"
        _display_error('Test error', None, float('inf'), 1)
        mock_print.assert_called_once()
        assert 'remaining' not in mock_print.call_args[0][0]

    def it_tests_ask_with_config_in_test_mode(self) -> None:
        """Test _ask_with_config in test mode."""
        # Create config with test mode enabled
        config = PromptConfig(
            parser=lambda s: Maybe.success(s),
            error_message='Test mode error',
            _test_mode=True,
        )

        # Call the function in test mode
        result = _ask_with_config('Enter value: ', config)

        # Should return failure with the error message
        assert result.is_failure()
        assert result.error_or('') == 'Test mode error'

        # If no error message was provided, check the default
        config = PromptConfig(_test_mode=True)
        result = _ask_with_config('Enter value: ', config)
        assert result.is_failure()
        assert result.error_or('') == 'Maximum retry attempts reached'

    def it_handles_infinite_retries(self) -> None:
        """Test _run_prompt_loop with infinite retries (float('inf'))."""

        # Create a mock parser that always fails
        def parser(_: str) -> Maybe[str]:
            return Maybe.failure('Always fails')

        # Create mock for input function that returns a few values then raises StopIteration
        mock_handle_input = MagicMock(
            side_effect=[
                ('input1', False),  # First input, not using default
                ('input2', False),  # Second input, not using default
                StopIteration,  # Stop the loop
            ]
        )

        # Patch the internal functions to avoid actual input
        with (
            patch('valid8r.prompt.basic._handle_user_input', mock_handle_input),
            patch('valid8r.prompt.basic._display_error'),
            pytest.raises(StopIteration),
        ):
            _run_prompt_loop(
                'Enter value: ',
                parser,
                lambda x: Maybe.success(x),  # Simple validator
                default=None,
                max_retries=float('inf'),
                error_message=None,
            )

        # Check that we called the input handler multiple times
        assert mock_handle_input.call_count == 3

    def it_uses_custom_validators(self) -> None:
        """Test ask with custom validators."""

        # Create a parser and validator that always succeed
        def parser(s: str) -> Maybe[int]:
            return Maybe.success(int(s))

        def validator(x: int) -> Maybe[int]:
            return Maybe.success(x)

        # Mock the input function
        with patch('builtins.input', return_value='42'):
            result = ask(
                'Enter value: ',
                parser=parser,
                validator=validator,
            )

        # Should succeed
        assert result.is_success()
        assert result.value_or(0) == 42

        # Create a validator that fails for even numbers
        def fail_even(x: int) -> Maybe[str]:
            return Maybe.failure('Cannot be even') if x % 2 == 0 else Maybe.success(x)

        # Try with an even number (should fail)
        with patch('builtins.input', return_value='42'):
            result = ask(
                'Enter value: ',
                parser=parser,
                validator=fail_even,
            )

        # Should fail
        assert result.is_failure()
        assert result.error_or('') == 'Cannot be even'

        # Try with an odd number (should succeed)
        with patch('builtins.input', return_value='43'):
            result = ask(
                'Enter value: ',
                parser=parser,
                validator=fail_even,
            )

        # Should succeed
        assert result.is_success()
        assert result.value_or(0) == 43

    def it_tests_process_input_with_validation_failure(self) -> None:
        """Test _process_input where the parser succeeds but the validator fails."""

        # Parser succeeds, validator fails
        def parser(s: str) -> Maybe[int]:
            return Maybe.success(int(s))

        def validator(_: None) -> Maybe[str]:
            return Maybe.failure('Validation error')

        result = _process_input('42', parser, validator)

        # Should return the validator's failure
        assert result.is_failure()
        assert result.error_or('') == 'Validation error'

    def it_handles_default_values_properly(self) -> None:
        """Test that _handle_user_input handles default values correctly."""
        # With a default value and empty input
        with patch('builtins.input', return_value=''):
            user_input, use_default = _handle_user_input('Enter value', default=42)

            # Should indicate to use the default
            assert user_input == ''
            assert use_default is True

        # With a default value but non-empty input
        with patch('builtins.input', return_value='user value'):
            user_input, use_default = _handle_user_input('Enter value', default=42)

            # Should not use the default
            assert user_input == 'user value'
            assert use_default is False

        # Without a default value
        with patch('builtins.input', return_value='user value'):
            user_input, use_default = _handle_user_input('Enter value', default=None)

            # Cannot use default
            assert user_input == 'user value'
            assert use_default is False

    def it_tests_display_error_with_finite_remaining_attempts(self) -> None:
        """Test _display_error with remaining attempts displayed."""
        # Mock print function
        mock_print = MagicMock()

        with patch('builtins.print', mock_print):
            # Call with finite remaining attempts
            _display_error('Error message', None, 5, 2)

            # Should have called print with the error and remaining attempts
            mock_print.assert_called_once()
            args = mock_print.call_args[0][0]
            assert 'Error: Error message' in args
            assert '3 attempt(s) remaining' in args

            # Reset mock
            mock_print.reset_mock()

            # Call with custom error message
            _display_error('Original error', 'Custom error', 5, 2)

            # Should use the custom error
            args = mock_print.call_args[0][0]
            assert 'Error: Custom error' in args
            assert 'Original error' not in args
