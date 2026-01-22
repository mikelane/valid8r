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


class DescribeUnwrapError:
    """Tests for the UnwrapError exception class."""

    def it_is_an_exception(self) -> None:
        """UnwrapError is a proper exception that can be raised and caught."""
        from valid8r.core.maybe import UnwrapError

        with pytest.raises(UnwrapError):
            raise UnwrapError('test message')

    def it_contains_error_message(self) -> None:
        """UnwrapError stores and returns the error message."""
        from valid8r.core.maybe import UnwrapError

        error = UnwrapError('custom error message')
        assert str(error) == 'custom error message'

    def it_inherits_from_exception(self) -> None:
        """UnwrapError inherits from Exception (or ValueError)."""
        from valid8r.core.maybe import UnwrapError

        assert issubclass(UnwrapError, Exception)


class DescribeUnwrap:
    """Tests for the unwrap() method on Maybe types."""

    def it_returns_value_for_success(self) -> None:
        """unwrap() returns the contained value for Success."""
        result = Success(42)
        assert result.unwrap() == 42

    def it_returns_complex_value_for_success(self) -> None:
        """unwrap() returns complex values for Success."""
        data = {'key': [1, 2, 3]}
        result = Success(data)
        assert result.unwrap() == data

    def it_raises_unwrap_error_for_failure(self) -> None:
        """unwrap() raises UnwrapError for Failure."""
        from valid8r.core.maybe import UnwrapError

        result: Maybe[int] = Failure('something went wrong')
        with pytest.raises(UnwrapError) as exc_info:
            result.unwrap()
        assert 'something went wrong' in str(exc_info.value)

    def it_raises_with_error_message_in_exception(self) -> None:
        """unwrap() includes the Failure error message in the UnwrapError."""
        from valid8r.core.maybe import UnwrapError

        result: Maybe[str] = Failure('validation failed: invalid email')
        with pytest.raises(UnwrapError) as exc_info:
            result.unwrap()
        assert 'validation failed' in str(exc_info.value)

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            pytest.param(42, 42, id='integer'),
            pytest.param('hello', 'hello', id='string'),
            pytest.param([1, 2, 3], [1, 2, 3], id='list'),
            pytest.param(None, None, id='None-value'),
            pytest.param(0, 0, id='zero'),
            pytest.param('', '', id='empty-string'),
        ],
    )
    def it_unwraps_various_success_values(self, value: T, expected: T) -> None:
        """unwrap() works with various value types including None and empty values."""
        result = Success(value)
        assert result.unwrap() == expected


class DescribeExpect:
    """Tests for the expect(msg) method on Maybe types."""

    def it_returns_value_for_success(self) -> None:
        """expect() returns the contained value for Success."""
        result = Success(42)
        assert result.expect('should have value') == 42

    def it_raises_unwrap_error_with_custom_message_for_failure(self) -> None:
        """expect() raises UnwrapError with custom message for Failure."""
        from valid8r.core.maybe import UnwrapError

        result: Maybe[int] = Failure('original error')
        with pytest.raises(UnwrapError) as exc_info:
            result.expect('custom error message for user')
        assert str(exc_info.value) == 'custom error message for user'

    def it_uses_custom_message_not_original_error(self) -> None:
        """expect() uses the provided message, not the original Failure error."""
        from valid8r.core.maybe import UnwrapError

        result: Maybe[str] = Failure('internal: database connection lost')
        with pytest.raises(UnwrapError) as exc_info:
            result.expect('Failed to load user profile')
        assert 'database' not in str(exc_info.value)
        assert 'Failed to load user profile' in str(exc_info.value)

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            pytest.param(100, 100, id='integer'),
            pytest.param({'a': 1}, {'a': 1}, id='dict'),
        ],
    )
    def it_returns_various_success_values(self, value: T, expected: T) -> None:
        """expect() works with various value types."""
        result = Success(value)
        assert result.expect('unused message') == expected


class DescribeUnwrapErr:
    """Tests for the unwrap_err() method on Maybe types."""

    def it_returns_error_for_failure(self) -> None:
        """unwrap_err() returns the error message for Failure."""
        result: Maybe[int] = Failure('something went wrong')
        assert result.unwrap_err() == 'something went wrong'

    def it_raises_unwrap_error_for_success(self) -> None:
        """unwrap_err() raises UnwrapError for Success."""
        from valid8r.core.maybe import UnwrapError

        result = Success(42)
        with pytest.raises(UnwrapError) as exc_info:
            result.unwrap_err()
        assert 'Success' in str(exc_info.value) or 'unwrap_err' in str(exc_info.value)

    def it_returns_various_error_messages(self) -> None:
        """unwrap_err() returns the exact error message stored in Failure."""
        result: Maybe[str] = Failure('Error: invalid input format')
        assert result.unwrap_err() == 'Error: invalid input format'

    def it_returns_empty_error_message(self) -> None:
        """unwrap_err() returns empty string for Failure with empty error."""
        result: Maybe[int] = Failure('')
        assert result.unwrap_err() == ''


class DescribeTypeSafetyAfterIsSuccess:
    """Tests verifying type-safe extraction after is_success() check."""

    def it_allows_type_safe_access_after_is_success_check(self) -> None:
        """After is_success() returns True, unwrap() returns T (not T | None)."""
        result: Maybe[int] = Success(42)
        if result.is_success():
            value: int = result.unwrap()
            assert value == 42

    def it_allows_type_safe_access_after_is_failure_check(self) -> None:
        """After is_failure() returns True, unwrap_err() returns str."""
        result: Maybe[int] = Failure('error message')
        if result.is_failure():
            error: str = result.unwrap_err()
            assert error == 'error message'


class DescribeAndThen:
    """Tests for the and_then() method - Python-friendly alias for bind() (#274)."""

    def it_behaves_identically_to_bind_on_success(self) -> None:
        """and_then() returns same result as bind() for Success."""
        initial = Success(5)

        def double(x: int) -> Maybe[int]:
            return Success(x * 2)

        bind_result = initial.bind(double)
        and_then_result = initial.and_then(double)

        assert bind_result.value_or(0) == and_then_result.value_or(0) == 10

    def it_behaves_identically_to_bind_on_failure(self) -> None:
        """and_then() returns same result as bind() for Failure."""
        initial: Maybe[int] = Failure('original error')

        def double(x: int) -> Maybe[int]:
            return Success(x * 2)

        bind_result = initial.bind(double)
        and_then_result = initial.and_then(double)

        assert bind_result.error_or('') == and_then_result.error_or('') == 'original error'

    def it_chains_operations_correctly(self) -> None:
        """and_then() chains multiple operations correctly."""
        result = Maybe.success(5).and_then(lambda x: Maybe.success(x * 2)).and_then(lambda x: Maybe.success(x + 3))

        assert result.is_success()
        assert result.value_or(0) == 13  # (5*2)+3 = 13

    def it_propagates_failure_through_chain(self) -> None:
        """and_then() propagates Failure and skips subsequent operations."""
        result = (
            Maybe.success(5)
            .and_then(lambda _: Maybe.failure('error occurred'))
            .and_then(lambda x: Maybe.success(x * 100))
        )

        assert result.is_failure()
        assert result.error_or('') == 'error occurred'

    @pytest.mark.parametrize(
        ('initial_value', 'transform_func', 'expected'),
        [
            pytest.param(10, lambda x: Success(str(x)), '10', id='int-to-string'),
            pytest.param('hello', lambda s: Success(len(s)), 5, id='string-to-int'),
            pytest.param([1, 2, 3], lambda lst: Success(sum(lst)), 6, id='list-to-sum'),
        ],
    )
    def it_allows_type_transformation(
        self, initial_value: int | str | list[int], transform_func: T, expected: str | int
    ) -> None:
        """and_then() allows changing the type of the contained value."""
        result = Success(initial_value).and_then(transform_func)
        assert result.value_or(None) == expected


class DescribeFromOptional:
    """Tests for the from_optional() class method (#281)."""

    def it_returns_success_with_value(self) -> None:
        """from_optional() returns Success when given a non-None value."""
        result = Maybe.from_optional(42)
        assert result.is_success()
        assert result.value_or(0) == 42

    def it_returns_success_with_zero(self) -> None:
        """from_optional() returns Success for zero (falsy but not None)."""
        result = Maybe.from_optional(0)
        assert result.is_success()
        assert result.value_or(-1) == 0

    def it_returns_success_with_empty_string(self) -> None:
        """from_optional() returns Success for empty string (falsy but not None)."""
        result = Maybe.from_optional('')
        assert result.is_success()
        assert result.value_or('default') == ''

    def it_returns_success_with_false(self) -> None:
        """from_optional() returns Success for False (falsy but not None)."""
        result = Maybe.from_optional(False)
        assert result.is_success()
        assert result.value_or(True) is False

    def it_returns_failure_with_none(self) -> None:
        """from_optional() returns Failure when given None."""
        result = Maybe.from_optional(None)
        assert result.is_failure()

    def it_uses_default_error_message_for_none(self) -> None:
        """from_optional() uses default error message when None is provided."""
        result = Maybe.from_optional(None)
        assert 'None' in result.error_or('')

    def it_uses_custom_error_message_for_none(self) -> None:
        """from_optional() uses custom error message when provided."""
        result = Maybe.from_optional(None, error_msg='Value is required')
        assert result.error_or('') == 'Value is required'

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            pytest.param(42, 42, id='integer'),
            pytest.param('hello', 'hello', id='string'),
            pytest.param([1, 2, 3], [1, 2, 3], id='list'),
            pytest.param({'a': 1}, {'a': 1}, id='dict'),
        ],
    )
    def it_preserves_various_value_types(self, value: T, expected: T) -> None:
        """from_optional() preserves various value types."""
        result = Maybe.from_optional(value)
        assert result.value_or(None) == expected


class DescribeToOptional:
    """Tests for the to_optional() instance method (#282)."""

    def it_returns_value_for_success(self) -> None:
        """to_optional() returns the contained value for Success."""
        result = Success(42)
        assert result.to_optional() == 42

    def it_returns_none_for_failure(self) -> None:
        """to_optional() returns None for Failure."""
        result: Maybe[int] = Failure('error')
        assert result.to_optional() is None

    def it_returns_zero_for_success_with_zero(self) -> None:
        """to_optional() returns zero for Success containing zero."""
        result = Success(0)
        assert result.to_optional() == 0

    def it_returns_empty_string_for_success_with_empty_string(self) -> None:
        """to_optional() returns empty string for Success containing empty string."""
        result = Success('')
        assert result.to_optional() == ''

    def it_returns_false_for_success_with_false(self) -> None:
        """to_optional() returns False for Success containing False."""
        result = Success(False)
        assert result.to_optional() is False

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            pytest.param(42, 42, id='integer'),
            pytest.param('hello', 'hello', id='string'),
            pytest.param([1, 2, 3], [1, 2, 3], id='list'),
            pytest.param({'a': 1}, {'a': 1}, id='dict'),
            pytest.param(None, None, id='None-value'),
        ],
    )
    def it_returns_various_success_values(self, value: T, expected: T) -> None:
        """to_optional() returns the contained value for various types."""
        result = Success(value)
        assert result.to_optional() == expected


class DescribeFromOptionalToOptionalRoundTrip:
    """Tests for round-trip conversion between optional and Maybe (#281, #282)."""

    @pytest.mark.parametrize(
        'value',
        [
            pytest.param(42, id='integer'),
            pytest.param('hello', id='string'),
            pytest.param([1, 2, 3], id='list'),
            pytest.param({'key': 'value'}, id='dict'),
            pytest.param(0, id='zero'),
            pytest.param('', id='empty-string'),
            pytest.param(False, id='false'),
        ],
    )
    def it_preserves_value_through_round_trip(self, value: T) -> None:
        """from_optional -> to_optional round trip preserves the value."""
        maybe = Maybe.from_optional(value)
        result = maybe.to_optional()
        assert result == value

    def it_returns_none_for_none_round_trip(self) -> None:
        """from_optional(None) -> to_optional returns None."""
        maybe = Maybe.from_optional(None)
        result = maybe.to_optional()
        assert result is None
