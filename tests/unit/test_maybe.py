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
            pytest.param([1, 2], lambda x: Maybe.success(x + [3]), [1, 2, 3], id='append to list'),  # noqa: RUF005
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

    def it_handles_failure_with_empty_error(self) -> None:
        """Test that Failure handles empty error messages."""
        # Create a Failure with an empty error message
        empty_failure = Failure('')

        # Check behavior
        assert empty_failure.is_failure()
        assert not empty_failure.is_success()

        # Check value_or with Failure that has empty error
        default_value = 'default'
        assert empty_failure.value_or(default_value) == default_value

        # Check string representation
        assert str(empty_failure) == 'Failure()'

    def it_converts_to_string_properly(self) -> None:
        """Test the string representation of Maybe objects."""
        # Test Success
        success = Success(42)
        assert str(success) == 'Success(42)'

        # Test complex Success
        complex_success = Success([1, 2, 3])
        assert str(complex_success) == 'Success([1, 2, 3])'

        # Test Failure
        failure = Failure('Error message')
        assert str(failure) == 'Failure(Error message)'

    def it_maps_success_values(self) -> None:
        """Test the map method on Success."""
        # Map int to string
        success = Success(42)
        mapped = success.map(lambda x: str(x))

        assert mapped.is_success()
        assert mapped.value_or('') == '42'
        assert isinstance(mapped.value_or(''), str)

        # Map with more complex function
        mapped = success.map(lambda x: [x, x * 2, x * 3])

        assert mapped.is_success()
        assert mapped.value_or([]) == [42, 84, 126]

    def it_maps_failure_values(self) -> None:
        """Test the map method on Failure."""
        # Map should do nothing on Failure
        failure = Failure('Original error')
        mapped = failure.map(lambda x: str(x))

        assert mapped.is_failure()
        assert mapped.error_or('') == 'Original error'

        # Map with more complex function
        mapped = failure.map(lambda x: [x, x * 2, x * 3])

        assert mapped.is_failure()
        assert mapped.error_or('') == 'Original error'

    def it_handles_bind_with_functions_returning_success(self) -> None:
        """Test bind with functions that return Success."""
        # Create initial Success
        initial = Success(5)

        # Define some transformations
        def double(x: int) -> Maybe[int]:
            return Success(x * 2)

        def add_10(x: int) -> Maybe[int]:
            return Success(x + 10)

        # Chain transformations
        result = initial.bind(double).bind(add_10)

        assert result.is_success()
        assert result.value_or(0) == 20  # (5*2)+10 = 20

    def it_handles_bind_with_functions_returning_failure(self) -> None:
        """Test bind with functions that return Failure."""
        # Create initial Success
        initial = Success(5)

        # Define a transformation that fails
        def fail_if_even(x: int) -> Maybe[int]:
            if x % 2 == 0:
                return Failure('Number cannot be even')
            return Success(x)

        # Test with odd number (should succeed)
        result = initial.bind(fail_if_even)
        assert result.is_success()
        assert result.value_or(0) == 5

        # Test with even number (should fail)
        result = Success(4).bind(fail_if_even)
        assert result.is_failure()
        assert result.error_or('') == 'Number cannot be even'

    def it_allows_type_change_in_bind_and_map(self) -> None:
        """Test that bind and map allow changing the type of the value."""
        # Initial value of type int
        initial = Success(42)

        # Change to string with bind
        str_result = initial.bind(lambda x: Success(str(x)))
        assert str_result.is_success()
        assert str_result.value_or('') == '42'
        assert isinstance(str_result.value_or(''), str)

        # Change to list with map
        list_result = initial.map(lambda x: [x])
        assert list_result.is_success()
        assert list_result.value_or([]) == [42]
        assert isinstance(list_result.value_or([]), list)

        # Change to complex nested structure
        complex_result = initial.map(lambda x: {'value': x, 'metadata': {'is_answer': x == 42}})
        assert complex_result.is_success()
        value = complex_result.value_or({})
        assert value['value'] == 42
        assert value['metadata']['is_answer'] is True

    def it_supports_pattern_matching(self) -> None:
        """Test that Success and Failure support pattern matching."""
        # Test Success matching
        success = Success(42)

        match success:
            case Success(42):
                matched_exactly = True
            case Success(_):
                matched_exactly = False
            case _:
                pytest.fail('Should have matched Success')

        assert matched_exactly

        # Test Failure matching
        failure = Failure('Error')

        match failure:
            case Failure('Error'):
                matched_exactly = True
            case Failure(_):
                matched_exactly = False
            case _:
                pytest.fail('Should have matched Failure')

        assert matched_exactly

        # Test with variable extraction
        match Success({'name': 'Alice', 'age': 30}):
            case Success({'name': name, 'age': age}):
                extracted_name = name
                extracted_age = age
            case _:
                pytest.fail('Should have matched Success with dict')

        assert extracted_name == 'Alice'
        assert extracted_age == 30
