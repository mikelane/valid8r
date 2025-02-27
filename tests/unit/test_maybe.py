"""Tests for the Maybe monad."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

import pytest

from valid8r.core.maybe import Maybe

if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar('T')


class DescribeMaybe:
    @pytest.mark.parametrize(
        ('value', 'expected_value'),
        [
            pytest.param(42, 42, id='integer'),
            pytest.param('hello', 'hello', id='string'),
            pytest.param([1, 2, 3], [1, 2, 3], id='list'),
            pytest.param(None, None, id='None'),
            pytest.param(3.14, 3.14, id='float'),
        ],
    )
    def it_just_creation_preserves_values(self, value: T, expected_value: T) -> None:
        """Test creating a Maybe.just preserves the value."""
        maybe = Maybe.just(value)
        assert maybe.is_just()
        assert not maybe.is_nothing()
        assert maybe.value() == expected_value

    @pytest.mark.parametrize(
        'error_message',
        [
            pytest.param('Error message', id='string error'),
            pytest.param('', id='empty error'),
            pytest.param('Multiple\nline\nerror', id='multiline error'),
        ],
    )
    def it_nothing_creation_preserves_error(self, error_message: str) -> None:
        """Test creating a Maybe.nothing preserves the error message."""
        maybe = Maybe.nothing(error_message)
        assert not maybe.is_just()
        assert maybe.is_nothing()
        assert maybe.error() == error_message

    @pytest.mark.parametrize(
        ('initial_value', 'transform_func', 'expected_value'),
        [
            pytest.param(2, lambda x: Maybe.just(x * 2), 4, id='double'),
            pytest.param('hello', lambda x: Maybe.just(x + ' world'), 'hello world', id='string concat'),
            pytest.param(5, lambda x: Maybe.just(x**2), 25, id='square'),
            pytest.param([1, 2], lambda x: Maybe.just(x + [3]), [1, 2, 3], id='append to list'),  # noqa: RUF005
        ],
    )
    def it_bind_success_applies_function(
        self, initial_value: int | str | list[int], transform_func: Callable, expected_value: int | str | list[int]
    ) -> None:
        """Test binding a function to a successful Maybe."""
        maybe = Maybe.just(initial_value)
        result = maybe.bind(transform_func)
        assert result.is_just()
        assert result.value() == expected_value

    @pytest.mark.parametrize(
        ('error_message', 'transform_func'),
        [
            pytest.param('Error', lambda x: Maybe.just(x * 2), id='numeric transform'),
            pytest.param('Not found', lambda x: Maybe.just(x.upper()), id='string transform'),
            pytest.param('Invalid', lambda x: Maybe.just(len(x)), id='length transform'),
        ],
    )
    def it_bind_failure_preserves_error(self, error_message: str, transform_func: Callable) -> None:
        """Test binding a function to a failed Maybe preserves the error."""
        maybe = Maybe.nothing(error_message)
        result = maybe.bind(transform_func)
        assert result.is_nothing()
        assert result.error() == error_message

    @pytest.mark.parametrize(
        ('initial_value', 'transform_func', 'expected_value'),
        [
            pytest.param(2, lambda x: x * 3, 6, id='triple'),
            pytest.param('hello', lambda x: x.upper(), 'HELLO', id='uppercase'),
            pytest.param([1, 2], lambda x: len(x), 2, id='length'),
            pytest.param(10, lambda x: x - 5, 5, id='subtract'),
        ],
    )
    def it_map_success_transforms_value(
        self, initial_value: int | str | list[int], transform_func: Callable, expected_value: int | str
    ) -> None:
        """Test mapping a function over a successful Maybe."""
        maybe = Maybe.just(initial_value)
        result = maybe.map(transform_func)
        assert result.is_just()
        assert result.value() == expected_value

    @pytest.mark.parametrize(
        ('error_message', 'transform_func'),
        [
            pytest.param('Error', lambda x: x * 3, id='numeric transform'),
            pytest.param('Not found', lambda x: x.upper(), id='string transform'),
            pytest.param('Invalid', lambda x: len(x), id='length transform'),
        ],
    )
    def it_map_failure_preserves_error(self, error_message: str, transform_func: Callable) -> None:
        """Test mapping a function over a failed Maybe preserves the error."""
        maybe = Maybe.nothing(error_message)
        result = maybe.map(transform_func)
        assert result.is_nothing()
        assert result.error() == error_message

    @pytest.mark.parametrize(
        ('maybe_obj', 'default_value', 'expected_result'),
        [
            pytest.param(Maybe.just(5), 10, 5, id='just with default'),
            pytest.param(Maybe.nothing('Error'), 10, 10, id='nothing with default'),
            pytest.param(Maybe.just(None), 'default', None, id='just None with default'),
            pytest.param(Maybe.just(''), 'default', '', id='just empty string with default'),
            pytest.param(Maybe.just(0), 42, 0, id='just zero with default'),
        ],
    )
    def it_value_or_returns_correct_value(
        self, maybe_obj: Maybe, default_value: int | str, expected_result: int | str | None
    ) -> None:
        """Test the value_or method correctly handles defaults."""
        assert maybe_obj.value_or(default_value) == expected_result

    @pytest.mark.parametrize(
        ('maybe_obj', 'expected_string'),
        [
            pytest.param(Maybe.just(42), 'Just(42)', id='just integer'),
            pytest.param(Maybe.just('hello'), 'Just(hello)', id='just string'),
            pytest.param(Maybe.nothing('Error'), 'Nothing(Error)', id='nothing with error'),
            pytest.param(Maybe.nothing(''), 'Nothing()', id='nothing with empty error'),
            pytest.param(Maybe.just(None), 'Just(None)', id='just None'),
        ],
    )
    def it_string_representation_is_correct(self, maybe_obj: Maybe, expected_string: str) -> None:
        """Test the string representation is correct."""
        assert str(maybe_obj) == expected_string

    def it_value_raises_error_on_nothing(self) -> None:
        """Test that calling value() on Nothing raises ValueError."""
        maybe = Maybe.nothing('Error')
        with pytest.raises(ValueError, match='Cannot get value from Nothing'):
            maybe.value()

    def it_error_raises_error_on_just(self) -> None:
        """Test that calling error() on Just raises ValueError."""
        maybe = Maybe.just(42)
        with pytest.raises(ValueError, match='Cannot get error from Just'):
            maybe.error()

    def it_chains_multiple_binds(self) -> None:
        """Test chaining multiple bind operations."""
        result = (
            Maybe.just(5)
            .bind(lambda x: Maybe.just(x * 2))
            .bind(lambda x: Maybe.just(x + 3))
            .bind(lambda x: Maybe.just(x**2))
        )
        assert result.is_just()
        assert result.value() == 169  # ((5*2)+3)^2 = 13^2 = 169

    def it_chains_binds_with_early_failure(self) -> None:
        """Test that failure short-circuits bind chains."""
        result = (
            Maybe.just(5)
            .bind(lambda x: Maybe.just(x * 2))
            .bind(lambda _: Maybe.nothing('Error in the middle'))
            .bind(lambda x: Maybe.just(x + 3))
        )
        assert result.is_nothing()
        assert result.error() == 'Error in the middle'
