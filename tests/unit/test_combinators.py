from __future__ import annotations

from valid8r.core.combinators import (
    and_then,
    not_validator,
    or_else,
)
from valid8r.core.maybe import Maybe
from valid8r.core.validators import (
    maximum,
    minimum,
    predicate,
)


class DescribeCombinators:
    def it_combines_validators_with_and_then(self) -> None:
        # Create two validators
        is_adult = minimum(18, 'Must be at least 18')
        is_senior = maximum(65, 'Must be at most 65')

        # Combine with AND logic
        is_working_age = and_then(is_adult, is_senior)

        # Test valid case (passes both validators)
        result = is_working_age(30)
        assert result.is_just()
        assert result.value() == 30

        # Test failing first validator
        result = is_working_age(16)
        assert result.is_nothing()
        assert result.error() == 'Must be at least 18'

        # Test failing second validator
        result = is_working_age(70)
        assert result.is_nothing()
        assert result.error() == 'Must be at most 65'

    def it_combines_validators_with_or_else(self) -> None:
        # Create two validators
        is_even = predicate(lambda x: x % 2 == 0, 'Must be even')
        is_divisible_by_five = predicate(lambda x: x % 5 == 0, 'Must be divisible by 5')

        # Combine with OR logic
        is_valid_number = or_else(is_even, is_divisible_by_five)

        # Test passing first validator
        result = is_valid_number(4)
        assert result.is_just()
        assert result.value() == 4

        # Test passing second validator
        result = is_valid_number(15)
        assert result.is_just()
        assert result.value() == 15

        # Test passing both validators
        result = is_valid_number(10)
        assert result.is_just()
        assert result.value() == 10

        # Test failing both validators
        result = is_valid_number(7)
        assert result.is_nothing()
        assert result.error() == 'Must be divisible by 5'

    def it_negates_validators_with_not_validator(self) -> None:
        # Create a validator
        is_even = predicate(lambda x: x % 2 == 0, 'Must be even')

        # Negate it
        is_odd = not_validator(is_even, 'Must be odd')

        # Test passing the negated validator
        result = is_odd(3)
        assert result.is_just()
        assert result.value() == 3

        # Test failing the negated validator
        result = is_odd(4)
        assert result.is_nothing()
        assert result.error() == 'Must be odd'

    def it_chains_multiple_validators(self) -> None:
        # Create validators
        is_positive = minimum(0, 'Must be positive')
        is_less_than_hundred = maximum(100, 'Must be less than 100')
        is_even = predicate(lambda x: x % 2 == 0, 'Must be even')

        # Chain multiple validators
        valid_even_number = and_then(and_then(is_positive, is_less_than_hundred), is_even)

        # Test passing all validators
        result = valid_even_number(42)
        assert result.is_just()
        assert result.value() == 42

        # Test failing the first validator
        result = valid_even_number(-2)
        assert result.is_nothing()
        assert result.error() == 'Must be positive'

        # Test failing the middle validator
        result = valid_even_number(102)
        assert result.is_nothing()
        assert result.error() == 'Must be less than 100'

        # Test failing the last validator
        result = valid_even_number(43)
        assert result.is_nothing()
        assert result.error() == 'Must be even'

    def it_combines_validators_with_different_error_precedence(self) -> None:
        # Test that OR validators properly report the last validator's error
        first_validator = predicate(lambda _: False, 'First error')
        second_validator = predicate(lambda _: False, 'Second error')

        combined = or_else(first_validator, second_validator)
        result = combined(42)

        assert result.is_nothing()
        assert result.error() == 'Second error'

    def it_works_with_manually_created_maybes(self) -> None:
        # Test that the combinators work with manually created Maybe objects
        def custom_validator(value: int) -> Maybe[int]:
            if value > 0:
                return Maybe.just(value)
            return Maybe.nothing('Custom error')

        # Combine with an existing validator
        positive_and_even = and_then(custom_validator, predicate(lambda x: x % 2 == 0, 'Must be even'))

        # Test passing
        result = positive_and_even(4)
        assert result.is_just()
        assert result.value() == 4

        # Test failing first validator
        result = positive_and_even(-2)
        assert result.is_nothing()
        assert result.error() == 'Custom error'

        # Test failing second validator
        result = positive_and_even(3)
        assert result.is_nothing()
        assert result.error() == 'Must be even'

    def it_overloads_operators_for_validators(self) -> None:
        # Create some validators
        is_positive = minimum(0, 'Must be positive')
        is_even = predicate(lambda x: x % 2 == 0, 'Must be even')
        is_less_than_hundred = maximum(100, 'Must be less than 100')

        combined_and = is_positive & is_even

        # Valid case
        result = combined_and(4)
        assert result.is_just()
        assert result.value() == 4

        # Invalid case
        result = combined_and(-2)
        assert result.is_nothing()
        assert result.error() == 'Must be positive'

        combined_or = is_even | is_less_than_hundred

        # Pass first validator
        result = combined_or(102)
        assert result.is_just()
        assert result.value() == 102

        # Pass second validator
        result = combined_or(99)
        assert result.is_just()
        assert result.value() == 99

        # Test ~ operator (NOT)
        negated = ~is_even

        # Valid case for negated
        result = negated(3)
        assert result.is_just()
        assert result.value() == 3

        # Invalid case for negated
        result = negated(4)
        assert result.is_nothing()
        assert 'Negated validation failed' in result.error()

        # Test chaining multiple operators
        complex_validator = is_positive & is_less_than_hundred & is_even

        # Valid case
        result = complex_validator(42)
        assert result.is_just()
        assert result.value() == 42

        # Invalid case
        result = complex_validator(43)
        assert result.is_nothing()
        assert result.error() == 'Must be even'
