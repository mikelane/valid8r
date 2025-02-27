from __future__ import annotations

import pytest

from valid8r.core.maybe import Maybe


class DescribeMaybe:
    def it_maybe_just_creation(self) -> None:
        """Test creating a Maybe with a value."""
        maybe = Maybe.just(42)
        assert maybe.is_just()
        assert not maybe.is_nothing()
        assert maybe.value() == 42

    def it_maybe_nothing_creation(self) -> None:
        """Test creating a Maybe with an error."""
        maybe = Maybe.nothing('Error message')
        assert not maybe.is_just()
        assert maybe.is_nothing()
        assert maybe.error() == 'Error message'

    def it_maybe_bind_success(self) -> None:
        """Test binding a function to a successful Maybe."""
        maybe = Maybe.just(2)
        result = maybe.bind(lambda x: Maybe.just(x * 2))
        assert result.is_just()
        assert result.value() == 4

    def it_maybe_bind_failure(self) -> None:
        """Test binding a function to a failed Maybe."""
        maybe = Maybe.nothing('Error')
        result = maybe.bind(lambda x: Maybe.just(x * 2))
        assert result.is_nothing()
        assert result.error() == 'Error'

    def it_maybe_map_success(self) -> None:
        """Test mapping a function over a successful Maybe."""
        maybe = Maybe.just(2)
        result = maybe.map(lambda x: x * 3)
        assert result.is_just()
        assert result.value() == 6

    def it_maybe_map_failure(self) -> None:
        """Test mapping a function over a failed Maybe."""
        maybe = Maybe.nothing('Error')
        result = maybe.map(lambda x: x * 3)
        assert result.is_nothing()
        assert result.error() == 'Error'

    def it_maybe_value_or(self) -> None:
        """Test the value_or method."""
        assert Maybe.just(5).value_or(10) == 5
        assert Maybe.nothing('Error').value_or(10) == 10

    def it_maybe_str_representation(self) -> None:
        """Test the string representation."""
        assert str(Maybe.just(42)) == 'Just(42)'
        assert str(Maybe.nothing('Error')) == 'Nothing(Error)'

    def it_maybe_value_error(self) -> None:
        """Test that calling value() on Nothing raises ValueError."""
        maybe = Maybe.nothing('Error')
        with pytest.raises(ValueError, match='Cannot get value from Nothing'):
            maybe.value()

    def it_maybe_error_error(self) -> None:
        """Test that calling error() on Just raises ValueError."""
        maybe = Maybe.just(42)
        with pytest.raises(ValueError, match='Cannot get error from Just'):
            maybe.error()
