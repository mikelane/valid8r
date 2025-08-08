from __future__ import annotations

from decimal import Decimal

import pytest

from valid8r.core.maybe import Failure, Maybe, Success
from valid8r.core.parsers import parse_decimal
from valid8r.core.validators import minimum


class DescribeDecimalParser:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            pytest.param("1.23", "1.23", id="simple decimal"),
            pytest.param("0", "0", id="zero"),
            pytest.param("-10.5", "-10.5", id="negative decimal"),
        ],
    )
    def it_parses_valid_decimals(self, text: str, expected: str) -> None:
        match parse_decimal(text):
            case Success(value):
                assert value == Decimal(expected)
            case Failure(error):
                pytest.fail(f"Unexpected failure: {error}")

    def it_rejects_invalid_decimal(self) -> None:
        match parse_decimal("abc"):
            case Success(value):
                pytest.fail(f"Unexpected success: {value}")
            case Failure(error):
                assert "valid number" in error.casefold()

    def it_works_with_numeric_validators(self) -> None:
        validator = minimum(Decimal("0"))
        # Valid case
        match validator(Decimal("1.23")):
            case Success(value):
                assert value == Decimal("1.23")
            case Failure(error):
                pytest.fail(f"Unexpected failure: {error}")
        # Invalid case
        match validator(Decimal("-0.01")):
            case Success(value):
                pytest.fail(f"Unexpected success: {value}")
            case Failure(error):
                assert "at least 0" in error