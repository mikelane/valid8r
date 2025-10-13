from __future__ import annotations

from decimal import Decimal

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import parse_decimal
from valid8r.core.validators import (
    between,
    maximum,
    minimum,
)


class DescribeDecimalParser:
    @pytest.mark.parametrize(
        ('text', 'expected'),
        [
            pytest.param('1.23', '1.23', id='simple decimal'),
            pytest.param('0', '0', id='zero'),
            pytest.param('-10.5', '-10.5', id='negative decimal'),
        ],
    )
    def it_parses_valid_decimals(self, text: str, expected: str) -> None:
        match parse_decimal(text):
            case Success(value):
                assert value == Decimal(expected)
            case Failure(error):
                pytest.fail(f'Unexpected failure: {error}')

    def it_rejects_invalid_decimal(self) -> None:
        match parse_decimal('abc'):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'valid number' in error.casefold()

    def it_rejects_empty_input(self) -> None:
        match parse_decimal(''):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert error == 'Input must not be empty'

    def it_works_with_numeric_validators(self) -> None:
        validator = minimum(Decimal(0))
        # Valid case
        match validator(Decimal('1.23')):
            case Success(value):
                assert value == Decimal('1.23')
            case Failure(error):
                pytest.fail(f'Unexpected failure: {error}')
        # Invalid case
        match validator(Decimal('-0.01')):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'at least 0' in error

    def it_validates_maximum_with_decimal_values(self) -> None:
        validator = maximum(Decimal(10))
        # Passes below and at max
        for value in (Decimal('9.99'), Decimal(10)):
            match validator(value):
                case Success(v):
                    assert v == value
                case Failure(error):
                    pytest.fail(f'Unexpected failure: {error}')
        # Fails above max
        match validator(Decimal('10.01')):
            case Success(v):
                pytest.fail(f'Unexpected success: {v}')
            case Failure(error):
                assert 'at most 10' in error

    def it_validates_between_with_decimal_values(self) -> None:
        validator = between(Decimal('-1.5'), Decimal('2.5'))
        # Passes inside and on boundaries
        for value in (Decimal(0), Decimal('-1.5'), Decimal('2.5')):
            match validator(value):
                case Success(v):
                    assert v == value
                case Failure(error):
                    pytest.fail(f'Unexpected failure: {error}')
        # Fails outside range
        for value in (Decimal('-1.51'), Decimal('2.51')):
            match validator(value):
                case Success(v):
                    pytest.fail(f'Unexpected success: {v}')
                case Failure(error):
                    assert 'between -1.5 and 2.5' in error
