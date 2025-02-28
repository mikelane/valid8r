"""Integration tests demonstrating the full API usage."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    parse_date,
    parse_enum,
    parse_int,
)
from valid8r.core.validators import (
    between,
    maximum,
    minimum,
    predicate,
)
from valid8r.prompt.basic import ask

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe


class DescribeValidatorIntegration:
    def it_chains_parsers_and_validators(self) -> None:
        """Test chaining of parsers and validators."""
        # Parse a string to a number and validate it
        result = parse_int('42').bind(lambda x: minimum(0)(x))

        match result:
            case Success(value):
                assert value == 42
            case _:
                assert pytest.fail('Expected Success')

        # Validation fails
        result = parse_int('42').bind(lambda x: minimum(100)(x))

        match result:
            case Failure(error):
                assert 'at least 100' in error
            case _:
                assert pytest.fail('Expected Failure')

        # Parsing fails before validation
        result = parse_int('not a number').bind(lambda x: minimum(0)(x))

        match result:
            case Failure(error):
                assert 'valid integer' in error
            case _:
                assert pytest.fail('Expected Failure')

    def it_uses_operator_overloading_for_validators(self) -> None:
        """Test operator overloading for validators."""
        # Create composite validators
        is_adult = minimum(18, 'Must be at least 18')
        is_senior = maximum(65, 'Must be at most 65')
        is_even = predicate(lambda x: x % 2 == 0, 'Must be even')

        # Combine with AND
        working_age = is_adult & is_senior

        # Test valid age
        result = working_age(30)
        match result:
            case Success(value):
                assert value == 30
            case _:
                pytest.fail('Expected Success')

        # Test too young
        result = working_age(16)
        match result:
            case Failure(error):
                assert 'Must be at least 18' in error
            case _:
                assert pytest.fail('Expected Failure')

        # Test too old
        result = working_age(70)
        match result:
            case Failure(error):
                assert 'Must be at most 65' in error
            case _:
                assert pytest.fail('Expected Failure')

        # Combine with OR
        valid_number = is_even | is_adult

        # Test passes first condition
        result = valid_number(4)
        match result:
            case Success(value):
                assert value == 4
            case _:
                pytest.fail('Expected Success')

        # Test passes second condition
        result = valid_number(19)
        match result:
            case Success(value):
                assert value == 19
            case _:
                pytest.fail('Expected Success')

        # Test fails both conditions
        result = valid_number(15)
        match result:
            case Failure(_):
                pass  # Just verify it's a failure
            case _:
                assert pytest.fail('Expected Failure')

    def it_works_with_complex_validation_chains(self) -> None:
        """Test complex validation chains."""
        # Create a complex validation chain: between 1-100 AND either even OR divisible by 5
        is_in_range = between(1, 100, 'Number must be between 1 and 100')
        is_even = predicate(lambda x: x % 2 == 0, 'Number must be even')
        is_div_by_5 = predicate(lambda x: x % 5 == 0, 'Number must be divisible by 5')

        valid_number = is_in_range & (is_even | is_div_by_5)

        # Test valid number (in range and even)
        result = valid_number(42)
        match result:
            case Success(value):
                assert value == 42
            case _:
                pytest.fail('Expected Success')

        # Test valid number (in range and divisible by 5)
        result = valid_number(35)
        match result:
            case Success(value):
                assert value == 35
            case _:
                pytest.fail('Expected Success')

        # Test invalid (outside range)
        result = valid_number(101)
        match result:
            case Failure(error):
                assert 'between 1 and 100' in error
            case _:
                assert pytest.fail('Expected Failure')

        # Test invalid (in range but not even or divisible by 5)
        result = valid_number(37)
        match result:
            case Failure(_):
                pass  # Just verify it's a failure
            case _:
                assert pytest.fail('Expected Failure')


class DescribePromptIntegration:
    @patch('builtins.input', return_value='42')
    @patch('builtins.print')
    def it_prompts_with_combined_validation(self, mock_print: MagicMock, mock_input: MagicMock) -> None:  # noqa: ARG002
        """Test prompting with combined validation."""
        # Create a validator that requires a number to be even and positive
        is_positive = minimum(0, 'Number must be positive')
        is_even = predicate(lambda x: x % 2 == 0, 'Number must be even')

        valid_number = is_positive & is_even

        # Ask for input with validation
        result = ask('Enter an even positive number: ', parser=parse_int, validator=valid_number, retry=False)

        match result:
            case Success(value):
                assert value == 42
            case _:
                pytest.fail('Expected Success')

    @patch('builtins.input', side_effect=['2023-02-31', '2023-02-15'])
    @patch('builtins.print')
    def it_handles_complex_data_types(self, mock_print: MagicMock, mock_input: MagicMock) -> None:
        """Test handling complex data types like dates."""
        # Create a validator that requires a date in February 2023
        is_feb_2023 = predicate(lambda d: d.year == 2023 and d.month == 2, 'Date must be in February 2023')

        # Ask for input with validation
        result = ask(
            'Enter a date in February 2023 (YYYY-MM-DD): ', parser=parse_date, validator=is_feb_2023, retry=True
        )

        # First input is invalid (Feb 31 doesn't exist), second is valid
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1

        # Verify final result
        match result:
            case Success(value):
                assert value == date(2023, 2, 15)
            case _:
                pytest.fail('Expected Success')

    @patch('builtins.input', return_value='RED')
    def it_works_with_custom_types(self, mock_input: MagicMock) -> None:  # noqa: ARG002
        """Test working with custom types like enums."""

        # Define an enum
        class Color(Enum):
            RED = 'RED'
            GREEN = 'GREEN'
            BLUE = 'BLUE'

        # Create a custom parser for the enum
        def color_parser(s: str) -> Maybe[Color]:
            return parse_enum(s, Color)

        # Ask for input
        result = ask('Enter a color (RED, GREEN, BLUE): ', parser=color_parser)

        match result:
            case Success(value):
                assert value == Color.RED
            case _:
                assert pytest.fail('Expected Success')
