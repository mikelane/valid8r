"""Tests for type_adapters module - automatic parser generation from type annotations.

Following TDD: These tests are written FIRST and will FAIL until implementation exists.
"""

from __future__ import annotations

from enum import Enum
from typing import (
    Annotated,
    Any,
    Literal,
    Optional,
    Union,
)

import pytest

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.validators import (
    maximum,
    minimum,
)

# This import will fail initially - that's the RED phase
try:
    from valid8r.core.type_adapters import from_type
except ImportError:
    # Stub for RED phase
    def from_type(annotation: type[Any]) -> Any:  # type: ignore[misc]  # noqa: ANN401
        msg = 'from_type not implemented yet'
        raise NotImplementedError(msg)


# Test helper
def expect_success_with_value(result: Maybe[Any], expected: Any) -> None:  # noqa: ANN401
    """Assert that result is Success with expected value."""
    match result:
        case Success(value):
            assert value == expected, f'Expected {expected}, got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success({expected}) but got Failure({err})')


def expect_failure_containing(result: Maybe[Any], text: str) -> None:
    """Assert that result is Failure with error containing text."""
    match result:
        case Failure(err):
            assert text.lower() in err.lower(), f'Expected error containing "{text}", got "{err}"'
        case Success(value):
            pytest.fail(f'Expected Failure containing "{text}" but got Success({value})')


# Test fixtures


class Color(Enum):
    """Test enum for color values."""

    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


class Status(Enum):
    """Test enum for status values."""

    ACTIVE = 1
    INACTIVE = 0


# =============================================================================
# Test Suite: Basic Type Parsers
# =============================================================================


class DescribeFromTypeBasicTypes:
    """Test from_type() with basic Python types."""

    def it_generates_parser_for_int(self) -> None:
        """Generate parser for int type."""
        parser = from_type(int)
        result = parser('42')
        expect_success_with_value(result, 42)

    def it_generates_parser_for_int_rejects_invalid(self) -> None:
        """Generated int parser rejects non-integer input."""
        parser = from_type(int)
        result = parser('not_a_number')
        expect_failure_containing(result, 'valid integer')

    def it_generates_parser_for_str(self) -> None:
        """Generate parser for str type."""
        parser = from_type(str)
        result = parser('hello')
        expect_success_with_value(result, 'hello')

    def it_generates_parser_for_float(self) -> None:
        """Generate parser for float type."""
        parser = from_type(float)
        result = parser('3.14')
        expect_success_with_value(result, 3.14)

    def it_generates_parser_for_float_rejects_invalid(self) -> None:
        """Generated float parser rejects non-float input."""
        parser = from_type(float)
        result = parser('xyz')
        expect_failure_containing(result, 'valid number')

    def it_generates_parser_for_bool(self) -> None:
        """Generate parser for bool type."""
        parser = from_type(bool)
        result = parser('true')
        expect_success_with_value(result, True)

    @pytest.mark.parametrize(
        ('input_val', 'expected'),
        [
            pytest.param('true', True, id='true'),
            pytest.param('false', False, id='false'),
            pytest.param('1', True, id='one'),
            pytest.param('0', False, id='zero'),
        ],
    )
    def it_generates_parser_for_bool_handles_variants(self, input_val: str, expected: bool) -> None:
        """Generated bool parser handles various boolean representations."""
        parser = from_type(bool)
        result = parser(input_val)
        expect_success_with_value(result, expected)


# =============================================================================
# Test Suite: Optional Types
# =============================================================================


class DescribeFromTypeOptional:
    """Test from_type() with Optional types."""

    def it_generates_parser_for_optional_int(self) -> None:
        """Generate parser for Optional[int]."""
        parser = from_type(Optional[int])
        result = parser('42')
        expect_success_with_value(result, 42)

    def it_generates_parser_for_optional_accepts_empty(self) -> None:
        """Generated Optional parser accepts empty string as None."""
        parser = from_type(Optional[int])
        result = parser('')
        expect_success_with_value(result, None)

    def it_generates_parser_for_optional_rejects_invalid(self) -> None:
        """Generated Optional parser rejects invalid non-None input."""
        parser = from_type(Optional[int])
        result = parser('invalid')
        expect_failure_containing(result, 'valid integer')

    def it_generates_parser_for_optional_str(self) -> None:
        """Generate parser for Optional[str]."""
        parser = from_type(Optional[str])
        result_some = parser('hello')
        result_none = parser('')
        expect_success_with_value(result_some, 'hello')
        expect_success_with_value(result_none, None)


# =============================================================================
# Test Suite: Collection Types
# =============================================================================


class DescribeFromTypeCollections:
    """Test from_type() with collection types."""

    def it_generates_parser_for_list_of_int(self) -> None:
        """Generate parser for list[int]."""
        parser = from_type(list[int])
        result = parser('[1, 2, 3]')
        expect_success_with_value(result, [1, 2, 3])

    def it_generates_parser_for_list_rejects_invalid_element(self) -> None:
        """Generated list parser rejects list with invalid element."""
        parser = from_type(list[int])
        result = parser('[1, "not_int", 3]')
        expect_failure_containing(result, 'valid integer')

    def it_generates_parser_for_set_of_str(self) -> None:
        """Generate parser for set[str]."""
        parser = from_type(set[str])
        result = parser('["a", "b", "c"]')
        expect_success_with_value(result, {'a', 'b', 'c'})

    def it_generates_parser_for_dict_str_int(self) -> None:
        """Generate parser for dict[str, int]."""
        parser = from_type(dict[str, int])
        result = parser('{"age": 30, "count": 5}')
        expect_success_with_value(result, {'age': 30, 'count': 5})

    def it_generates_parser_for_dict_rejects_invalid_value(self) -> None:
        """Generated dict parser rejects dict with invalid value type."""
        parser = from_type(dict[str, int])
        result = parser('{"age": "thirty"}')
        expect_failure_containing(result, 'valid integer')


# =============================================================================
# Test Suite: Nested Types
# =============================================================================


class DescribeFromTypeNested:
    """Test from_type() with nested type structures."""

    def it_generates_parser_for_nested_list(self) -> None:
        """Generate parser for list[list[int]]."""
        parser = from_type(list[list[int]])
        result = parser('[[1, 2], [3, 4]]')
        expect_success_with_value(result, [[1, 2], [3, 4]])

    def it_generates_parser_for_list_of_dicts(self) -> None:
        """Generate parser for list[dict[str, int]]."""
        parser = from_type(list[dict[str, int]])
        result = parser('[{"a": 1}, {"b": 2}]')
        expect_success_with_value(result, [{'a': 1}, {'b': 2}])

    def it_generates_parser_for_dict_with_list_values(self) -> None:
        """Generate parser for dict[str, list[int]]."""
        parser = from_type(dict[str, list[int]])
        result = parser('{"scores": [95, 87, 92]}')
        expect_success_with_value(result, {'scores': [95, 87, 92]})


# =============================================================================
# Test Suite: Union Types
# =============================================================================


class DescribeFromTypeUnion:
    """Test from_type() with Union types."""

    def it_generates_parser_for_union_int_str(self) -> None:
        """Generate parser for Union[int, str]."""
        parser = from_type(Union[int, str])
        result_int = parser('42')
        result_str = parser('hello')
        # Union tries int first, then str
        expect_success_with_value(result_int, 42)
        expect_success_with_value(result_str, 'hello')

    def it_generates_parser_for_union_tries_all_types(self) -> None:
        """Generated Union parser tries all alternatives in order."""
        parser = from_type(Union[int, float, str])
        result_int = parser('42')
        result_float = parser('3.14')
        result_str = parser('not_a_number')

        expect_success_with_value(result_int, 42)
        expect_success_with_value(result_float, 3.14)
        expect_success_with_value(result_str, 'not_a_number')


# =============================================================================
# Test Suite: Literal Types
# =============================================================================


class DescribeFromTypeLiteral:
    """Test from_type() with Literal types."""

    def it_generates_parser_for_literal_strings(self) -> None:
        """Generate parser for Literal['red', 'green', 'blue']."""
        parser = from_type(Literal['red', 'green', 'blue'])
        result = parser('red')
        expect_success_with_value(result, 'red')

    def it_generates_parser_for_literal_rejects_invalid(self) -> None:
        """Generated Literal parser rejects value not in literal set."""
        parser = from_type(Literal['red', 'green', 'blue'])
        result = parser('yellow')
        expect_failure_containing(result, 'must be one of')

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            pytest.param('red', 'red', id='red'),
            pytest.param('green', 'green', id='green'),
            pytest.param('blue', 'blue', id='blue'),
        ],
    )
    def it_generates_parser_for_literal_accepts_valid_values(self, value: str, expected: str) -> None:
        """Generated Literal parser accepts all valid literal values."""
        parser = from_type(Literal['red', 'green', 'blue'])
        result = parser(value)
        expect_success_with_value(result, expected)

    def it_generates_parser_for_literal_mixed_types(self) -> None:
        """Generate parser for Literal with mixed types."""
        parser = from_type(Literal[1, 'one', True])
        result_int = parser('1')
        result_str = parser('one')
        result_bool = parser('true')

        expect_success_with_value(result_int, 1)
        expect_success_with_value(result_str, 'one')
        expect_success_with_value(result_bool, True)


# =============================================================================
# Test Suite: Enum Types
# =============================================================================


class DescribeFromTypeEnum:
    """Test from_type() with Enum types."""

    def it_generates_parser_for_enum(self) -> None:
        """Generate parser for Enum type."""
        parser = from_type(Color)
        result = parser('RED')
        expect_success_with_value(result, Color.RED)

    def it_generates_parser_for_enum_rejects_invalid(self) -> None:
        """Generated Enum parser rejects invalid enum member."""
        parser = from_type(Color)
        result = parser('YELLOW')
        expect_failure_containing(result, 'valid enumeration')

    def it_generates_parser_for_enum_case_insensitive(self) -> None:
        """Generated Enum parser handles case-insensitive matching."""
        parser = from_type(Color)
        result = parser('red')
        expect_success_with_value(result, Color.RED)

    @pytest.mark.parametrize(
        ('input_val', 'expected'),
        [
            pytest.param('RED', Color.RED, id='RED'),
            pytest.param('GREEN', Color.GREEN, id='GREEN'),
            pytest.param('BLUE', Color.BLUE, id='BLUE'),
            pytest.param('red', Color.RED, id='red-lowercase'),
        ],
    )
    def it_generates_parser_for_enum_handles_variants(self, input_val: str, expected: Color) -> None:
        """Generated Enum parser handles various input formats."""
        parser = from_type(Color)
        result = parser(input_val)
        expect_success_with_value(result, expected)


# =============================================================================
# Test Suite: Annotated Types
# =============================================================================


class DescribeFromTypeAnnotated:
    """Test from_type() with Annotated types."""

    def it_generates_parser_for_annotated_without_validators(self) -> None:
        """Generate parser for Annotated[int, 'description'] - ignores metadata."""
        parser = from_type(Annotated[int, 'must be positive'])
        result = parser('42')
        expect_success_with_value(result, 42)

    def it_generates_parser_for_annotated_with_validator(self) -> None:
        """Generate parser for Annotated[int, validator] - applies validator."""
        parser = from_type(Annotated[int, minimum(0)])
        result_valid = parser('42')
        result_invalid = parser('-5')

        expect_success_with_value(result_valid, 42)
        expect_failure_containing(result_invalid, 'at least 0')

    def it_generates_parser_for_annotated_chains_validators(self) -> None:
        """Generate parser for Annotated with multiple validators - chains them."""
        parser = from_type(Annotated[int, minimum(0), maximum(100)])
        result_valid = parser('50')
        result_too_low = parser('-5')
        result_too_high = parser('150')

        expect_success_with_value(result_valid, 50)
        expect_failure_containing(result_too_low, 'at least 0')
        expect_failure_containing(result_too_high, 'at most 100')


# =============================================================================
# Test Suite: Error Handling
# =============================================================================


class DescribeFromTypeErrors:
    """Test from_type() error handling for unsupported types."""

    def it_rejects_unsupported_callable_type(self) -> None:
        """Reject unsupported Callable type."""
        import typing

        with pytest.raises((ValueError, TypeError, NotImplementedError)) as exc_info:
            from_type(typing.Callable)

        assert 'unsupported' in str(exc_info.value).lower()

    def it_rejects_none_type_annotation(self) -> None:
        """Reject None as type annotation."""
        with pytest.raises((ValueError, TypeError)) as exc_info:
            from_type(None)  # type: ignore[arg-type]

        assert (
            'type annotation required' in str(exc_info.value).lower() or 'cannot be none' in str(exc_info.value).lower()
        )

    def it_rejects_invalid_type_object(self) -> None:
        """Reject invalid type object."""
        with pytest.raises((ValueError, TypeError)) as exc_info:
            from_type('not_a_type')  # type: ignore[arg-type]

        # Should raise some kind of error for invalid input
        assert exc_info.value is not None


# =============================================================================
# Test Suite: Type Preservation
# =============================================================================


class DescribeFromTypePreservation:
    """Test that from_type() generates parsers that return correct Python types."""

    def it_preserves_int_type(self) -> None:
        """Generated parser returns actual int, not string."""
        parser = from_type(int)
        result = parser('42')
        match result:
            case Success(value):
                assert isinstance(value, int)
                assert type(value) is int
            case Failure(err):
                pytest.fail(f'Expected Success but got Failure({err})')

    def it_preserves_list_type(self) -> None:
        """Generated parser returns actual list."""
        parser = from_type(list[int])
        result = parser('[1, 2, 3]')
        match result:
            case Success(value):
                assert isinstance(value, list)
                assert all(isinstance(x, int) for x in value)
            case Failure(err):
                pytest.fail(f'Expected Success but got Failure({err})')

    def it_preserves_none_in_optional(self) -> None:
        """Generated Optional parser returns actual None."""
        parser = from_type(Optional[str])
        result = parser('')
        match result:
            case Success(value):
                assert value is None
            case Failure(err):
                pytest.fail(f'Expected Success(None) but got Failure({err})')


# =============================================================================
# Test Suite: Security - DoS Protection
# =============================================================================


class DescribeFromTypeSecurityDoS:
    """Test DoS protection for from_type() generated parsers.

    Following security best practices from CLAUDE.md:
    - Always validate input length BEFORE expensive operations
    - Test both correctness (error message) AND performance (< 10ms)
    - Use reasonable limits (100KB = 100,000 chars for JSON)
    """

    def it_rejects_excessively_long_json_list(self) -> None:
        """Reject extremely long JSON list input to prevent DoS attacks."""
        import time

        # Create malicious input: ~600KB JSON array
        malicious_input = '[' + '1,' * 100_000 + '1]'

        start = time.perf_counter()
        parser = from_type(list[int])
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_json_dict(self) -> None:
        """Reject extremely long JSON dict input to prevent DoS attacks."""
        import time

        # Create malicious input: ~600KB JSON object
        malicious_input = '{' + '"k": 1,' * 100_000 + '"x": 1}'

        start = time.perf_counter()
        parser = from_type(dict[str, int])
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_json_set(self) -> None:
        """Reject extremely long JSON set input to prevent DoS attacks."""
        import time

        # Create malicious input: ~600KB JSON array for set
        malicious_input = '[' + '1,' * 100_000 + '1]'

        start = time.perf_counter()
        parser = from_type(set[int])
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_bare_list(self) -> None:
        """Reject extremely long bare list input (list without type parameter)."""
        import time

        malicious_input = '[' + '1,' * 100_000 + '1]'

        start = time.perf_counter()
        parser = from_type(list)  # type: ignore[type-abstract]
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_bare_dict(self) -> None:
        """Reject extremely long bare dict input (dict without type parameters)."""
        import time

        malicious_input = '{' + '"k": 1,' * 100_000 + '"x": 1}'

        start = time.perf_counter()
        parser = from_type(dict)  # type: ignore[type-abstract]
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_bare_set(self) -> None:
        """Reject extremely long bare set input (set without type parameter)."""
        import time

        malicious_input = '[' + '1,' * 100_000 + '1]'

        start = time.perf_counter()
        parser = from_type(set)  # type: ignore[type-abstract]
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.is_failure()
        assert 'too large' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_accepts_normal_sized_inputs(self) -> None:
        """Accept inputs within reasonable size limits."""
        # Normal sized inputs (~1KB) should work fine
        parser_list = from_type(list[int])
        parser_dict = from_type(dict[str, int])
        parser_set = from_type(set[str])

        # Create normal inputs
        list_input = '[' + ','.join(str(i) for i in range(100)) + ']'
        dict_input = '{' + ','.join(f'"k{i}": {i}' for i in range(100)) + '}'
        set_input = '[' + ','.join(f'"v{i}"' for i in range(100)) + ']'

        # All should succeed
        list_result = parser_list(list_input)
        dict_result = parser_dict(dict_input)
        set_result = parser_set(set_input)

        assert list_result.is_success()
        assert dict_result.is_success()
        assert set_result.is_success()
