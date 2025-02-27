"""Tests for the Maybe monad."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

import pytest

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

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
    def it_success_creation_preserves_values(self, value: T, expected_value: T) -> None:
        """Test creating a Maybe.success preserves the value."""
        maybe = Maybe.success(value)

        match maybe:
            case Success(val):
                assert val == expected_value
            case _:
                pytest.fail('Expected Success but got something else')

    @pytest.mark.parametrize(
        'error_message',
        [
            pytest.param('Error message', id='string error'),
            pytest.param('', id='empty error'),
            pytest.param('Multiple\nline\nerror', id='multiline error'),
        ],
    )
    def it_failure_creation_preserves_error(self, error_message: str) -> None:
        """Test creating a Maybe.failure preserves the error message."""
        maybe = Maybe.failure(error_message)

        match maybe:
            case Failure(err):
                assert err == error_message
            case _:
                pytest.fail('Expected Failure but got something else')

    @pytest.mark.parametrize(
        ('initial_value', 'transform_func', 'expected_value'),
        [
            pytest.param(2, lambda x: Maybe.success(x * 2), 4, id='double'),
            pytest.param('hello', lambda x: Maybe.success(x + ' world'), 'hello world', id='string concat'),
            pytest.param(5, lambda x: Maybe.success(x**2), 25, id='square'),
            pytest.param([1, 2], lambda x: Maybe.success(x + [3]), [1, 2, 3], id='append to list'),
        ],
    )
    def it_bind_success_applies_function(
        self, initial_value: int | str | list[int], transform_func: Callable, expected_value: int | str | list[int]
    ) -> None:
        """Test binding a function to a successful Maybe."""
        maybe = Maybe.success(initial_value)
        result = maybe.bind(transform_func)

        match result:
            case Success(val):
                assert val == expected_value
            case _:
                pytest.fail('Expected Success but got something else')

    @pytest.mark.parametrize(
        ('error_message', 'transform_func'),
        [
            pytest.param('Error', lambda x: Maybe.success(x * 2), id='numeric transform'),
            pytest.param('Not found', lambda x: Maybe.success(x.upper()), id='string transform'),
            pytest.param('Invalid', lambda x: Maybe.success(len(x)), id='length transform'),
        ],
    )
    def it_bind_failure_preserves_error(self, error_message: str, transform_func: Callable) -> None:
        """Test binding a function to a failed Maybe preserves the error."""
        maybe = Maybe.failure(error_message)
        result = maybe.bind(transform_func)

        match result:
            case Failure(err):
                assert err == error_message
            case _:
                pytest.fail('Expected Failure but got something else')

    def it_chains_multiple_binds(self) -> None:
        """Test chaining multiple bind operations."""
        result = (
            Maybe.success(5)
            .bind(lambda x: Maybe.success(x * 2))
            .bind(lambda x: Maybe.success(x + 3))
            .bind(lambda x: Maybe.success(x**2))
        )

        match result:
            case Success(val):
                assert val == 169  # ((5*2)+3)^2 = 13^2 = 169
            case Failure(err):
                pytest.fail(f'Expected Success but got Failure: {err}')

    def it_chains_binds_with_early_failure(self) -> None:
        """Test that failure short-circuits bind chains."""
        result = (
            Maybe.success(5)
            .bind(lambda x: Maybe.success(x * 2))
            .bind(lambda _: Maybe.failure('Error in the middle'))
            .bind(lambda x: Maybe.success(x + 3))
        )

        match result:
            case Failure(err):
                assert err == 'Error in the middle'
            case Success(_):
                pytest.fail('Expected Failure but got Success')

    def it_demonstrates_pattern_matching_with_complex_conditions(self) -> None:
        """Test pattern matching with complex conditions."""
        def describe_value(maybe_val: Maybe[int]) -> str:
            match maybe_val:
                case Success(val) if val > 100:
                    return 'Large success'
                case Success(val) if val % 2 == 0:
                    return 'Even success'
                case Success(val):
                    return 'Odd success'
                case Failure(err) if 'invalid' in err.lower():
                    return 'Invalid input error'
                case Failure(err):
                    return f'Other error: {err}'

        assert describe_value(Maybe.success(120)) == 'Large success'
        assert describe_value(Maybe.success(42)) == 'Even success'
        assert describe_value(Maybe.success(7)) == 'Odd success'
        assert describe_value(Maybe.failure('Invalid input')) == 'Invalid input error'
        assert describe_value(Maybe.failure('Something went wrong')) == 'Other error: Something went wrong'
