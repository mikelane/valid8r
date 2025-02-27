"""Tests for the prompt/basic.py module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from valid8r.core.parsers import parse_int
from valid8r.prompt.basic import ask

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
        assert result.value_or('TESTTEST') == 42
        mock_print.assert_not_called()

    def it_handles_empty_input_with_default(self, mock_input: MockType, mock_print: MockType) -> None:
        """Test empty input with default value."""
        mock_input.return_value = ''

        result = ask('Enter a number: ', parser=parse_int, default=10)

        mock_input.assert_called_once_with('Enter a number:  [10]: ')
        assert result.is_success()
        assert result.value_or('TESTTEST') == 10
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
        assert 'Input must be a valid integer' in result.value_or('TEST')

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
        assert result.value_or('TESTTEST') == expected_value

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
        assert 'Maximum retry attempts reached' in result.value_or('TEST')

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
