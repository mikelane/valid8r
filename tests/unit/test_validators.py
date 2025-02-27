from __future__ import annotations

from valid8r.core.validators import (
    between,
    length,
    maximum,
    minimum,
    predicate,
)


class DescribeValidators:
    def it_validates_minimum_value(self) -> None:
        validator = minimum(5)

        # Valid case
        result = validator(10)
        assert result.is_just()
        assert result.value() == 10

        # Invalid case
        result = validator(3)
        assert result.is_nothing()
        assert 'must be at least 5' in result.error()

    def it_validates_maximum_value(self) -> None:
        validator = maximum(10)

        # Valid case
        result = validator(5)
        assert result.is_just()
        assert result.value() == 5

        # Invalid case
        result = validator(15)
        assert result.is_nothing()
        assert 'must be at most 10' in result.error()

    def it_validates_between_values(self) -> None:
        validator = between(5, 10)

        # Valid case
        result = validator(7)
        assert result.is_just()
        assert result.value() == 7

        # Lower bound invalid
        result = validator(3)
        assert result.is_nothing()
        assert 'must be between 5 and 10' in result.error()

        # Upper bound invalid
        result = validator(12)
        assert result.is_nothing()
        assert 'must be between 5 and 10' in result.error()

    def it_validates_predicate(self) -> None:
        is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')

        # Valid case
        result = is_even(4)
        assert result.is_just()
        assert result.value() == 4

        # Invalid case
        result = is_even(3)
        assert result.is_nothing()
        assert 'Value must be even' in result.error()

    def it_validates_string_length(self) -> None:
        validator = length(3, 5)

        # Valid case
        result = validator('abcd')
        assert result.is_just()
        assert result.value() == 'abcd'

        # Too short
        result = validator('ab')
        assert result.is_nothing()
        assert 'length must be between 3 and 5' in result.error()

        # Too long
        result = validator('abcdef')
        assert result.is_nothing()
        assert 'length must be between 3 and 5' in result.error()
