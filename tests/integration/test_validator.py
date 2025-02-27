"""Integration tests demonstrating the full API usage."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING
from unittest.mock import (
    MagicMock,
    patch,
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

        assert result.is_just()
        assert result.value() == 42

        # Validation fails
        result = parse_int('42').bind(lambda x: minimum(100)(x))

        assert result.is_nothing()
        assert 'at least 100' in result.error()

        # Parsing fails before validation
        result = parse_int('not a number').bind(lambda x: minimum(0)(x))

        assert result.is_nothing()
        assert 'valid integer' in result.error()

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
        assert result.is_just()
        assert result.value() == 30

        # Test too young
        result = working_age(16)
        assert result.is_nothing()
        assert 'Must be at least 18' in result.error()

        # Test too old
        result = working_age(70)
        assert result.is_nothing()
        assert 'Must be at most 65' in result.error()

        # Combine with OR
        valid_number = is_even | is_adult

        # Test passes first condition
        result = valid_number(4)
        assert result.is_just()
        assert result.value() == 4

        # Test passes second condition
        result = valid_number(19)
        assert result.is_just()
        assert result.value() == 19

        # Test fails both conditions
        result = valid_number(15)
        assert result.is_nothing()

    def it_works_with_complex_validation_chains(self) -> None:
        """Test complex validation chains."""
        # Create a complex validation chain: between 1-100 AND either even OR divisible by 5
        is_in_range = between(1, 100, 'Number must be between 1 and 100')
        is_even = predicate(lambda x: x % 2 == 0, 'Number must be even')
        is_div_by_5 = predicate(lambda x: x % 5 == 0, 'Number must be divisible by 5')

        valid_number = is_in_range & (is_even | is_div_by_5)

        # Test valid number (in range and even)
        result = valid_number(42)
        assert result.is_just()
        assert result.value() == 42

        # Test valid number (in range and divisible by 5)
        result = valid_number(35)
        assert result.is_just()
        assert result.value() == 35

        # Test invalid (outside range)
        result = valid_number(101)
        assert result.is_nothing()
        assert 'between 1 and 100' in result.error()

        # Test invalid (in range but not even or divisible by 5)
        result = valid_number(37)
        assert result.is_nothing()


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

        assert result.is_just()
        assert result.value() == 42

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
        assert result.is_just()
        assert result.value() == date(2023, 2, 15)

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

        assert result.is_just()
        assert result.value() == Color.RED
