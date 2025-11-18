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

    def it_generates_parser_for_optional_accepts_none_string(self) -> None:
        """Generated Optional parser accepts 'none' string as None."""
        parser = from_type(Optional[int])
        result_lower = parser('none')
        result_upper = parser('NONE')
        result_mixed = parser('NoNe')
        expect_success_with_value(result_lower, None)
        expect_success_with_value(result_upper, None)
        expect_success_with_value(result_mixed, None)

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
        expect_failure_containing(result, 'valid Color')

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
        expect_failure_containing(result_invalid, 'at least')

    def it_generates_parser_for_annotated_chains_validators(self) -> None:
        """Generate parser for Annotated with multiple validators - chains them."""
        parser = from_type(Annotated[int, minimum(0), maximum(100)])
        result_valid = parser('50')
        result_too_low = parser('-5')
        result_too_high = parser('150')

        expect_success_with_value(result_valid, 50)
        expect_failure_containing(result_too_low, 'at least')
        expect_failure_containing(result_too_high, 'at most')

    def it_generates_parser_for_annotated_with_no_metadata(self) -> None:
        """Generate parser for Annotated with empty metadata list."""
        # This tests the edge case where Annotated has no metadata at all
        # which would raise ValueError: Annotated type requires at least a base type
        from valid8r.core.type_adapters import _handle_annotated_type

        # Can't create Annotated[] with no args, but we can test error handling
        with pytest.raises(ValueError, match='.*base type.*'):
            _handle_annotated_type(())  # Empty args tuple

    def it_generates_parser_for_annotated_with_non_callable_metadata(self) -> None:
        """Generate parser for Annotated with non-callable metadata - ignores it."""
        # Annotated with string and int metadata (non-callable)
        parser = from_type(Annotated[str, 'description', 42])
        result = parser('hello')
        expect_success_with_value(result, 'hello')


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

        # Should raise TypeError with message about forward reference
        assert 'forward reference' in str(exc_info.value).lower()

    def it_rejects_function_type(self) -> None:
        """Reject function types."""
        import types

        def dummy_function() -> None:
            pass

        with pytest.raises(TypeError) as exc_info:
            from_type(types.FunctionType)

        assert 'unsupported' in str(exc_info.value).lower()

    def it_rejects_unsupported_class_type(self) -> None:
        """Reject unsupported class types."""

        class CustomClass:
            pass

        with pytest.raises(TypeError) as exc_info:
            from_type(CustomClass)

        assert 'unsupported' in str(exc_info.value).lower()


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
# Test Suite: DoS Protection
# =============================================================================


class DescribeFromTypeDoSProtection:
    """Test DoS protection through input length validation."""

    def it_rejects_excessively_long_list_input(self) -> None:
        """Reject extremely long JSON list input to prevent DoS attacks."""
        import time

        malicious_input = '[' + ','.join(['1'] * 10000) + ']'  # ~50KB input

        start = time.perf_counter()
        parser = from_type(list[int])
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too long' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_rejects_excessively_long_dict_input(self) -> None:
        """Reject extremely long JSON dict input to prevent DoS attacks."""
        import time

        # Create a very large JSON object
        items = ','.join([f'"key{i}": {i}' for i in range(1000)])
        malicious_input = '{' + items + '}'  # ~15KB input

        start = time.perf_counter()
        parser = from_type(dict[str, int])
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too long' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'


# Note: Bare collections (list, dict, set without type parameters) are not tested
# because they would require parse_json which doesn't have DoS protection yet.
# This is tracked in issue #196 (test coverage improvement).


# =============================================================================
# Test Suite: Union Pipe Operator
# =============================================================================


class DescribeFromTypeUnionPipe:
    """Test from_type() with Union pipe operator (X | Y)."""

    def it_generates_parser_for_pipe_union(self) -> None:
        """Generate parser for X | Y union syntax (skipped - requires Python 3.11+ types.UnionType support)."""
        pytest.skip('X | Y union syntax requires types.UnionType support which varies across Python versions')

    def it_returns_last_failure_when_all_union_types_fail(self) -> None:
        """Return last failure when all union alternatives fail."""
        parser = from_type(Union[int, float])
        result = parser('not_a_number')

        # Should return failure from last parser (float)
        assert result.is_failure()
        assert 'number' in result.error_or('').lower()


# =============================================================================
# Test Suite: Additional Literal Edge Cases
# =============================================================================


class DescribeFromTypeLiteralEdgeCases:
    """Test from_type() with Literal edge cases."""

    def it_handles_literal_with_integer_zero(self) -> None:
        """Handle Literal with integer zero (not confused with False)."""
        parser = from_type(Literal[0, 1, 2])
        result = parser('0')
        expect_success_with_value(result, 0)

    def it_handles_literal_with_false_boolean(self) -> None:
        """Handle Literal with False boolean."""
        parser = from_type(Literal[False, True])
        result = parser('false')
        expect_success_with_value(result, False)


# =============================================================================
# Test Suite: Collection Edge Cases
# =============================================================================


class DescribeFromTypeCollectionEdgeCases:
    """Test from_type() with collection edge cases."""

    def it_handles_dict_with_nested_dict_keys(self) -> None:
        """Handle dict where keys require conversion."""
        parser = from_type(dict[int, str])
        result = parser('{"1": "one", "2": "two"}')
        expect_success_with_value(result, {1: 'one', 2: 'two'})

    def it_handles_dict_with_nested_dict_values(self) -> None:
        """Handle dict where values are nested structures."""
        parser = from_type(dict[str, dict[str, int]])
        result = parser('{"a": {"x": 1}, "b": {"y": 2}}')
        expect_success_with_value(result, {'a': {'x': 1}, 'b': {'y': 2}})

    def it_handles_list_with_nested_dicts(self) -> None:
        """Handle list where elements are dicts."""
        parser = from_type(list[dict[str, str]])
        result = parser('[{"a": "1"}, {"b": "2"}]')
        expect_success_with_value(result, [{'a': '1'}, {'b': '2'}])

    def it_handles_set_with_nested_elements(self) -> None:
        """Handle set where elements require parsing."""
        parser = from_type(set[int])
        result = parser('[1, 2, 3, 2, 1]')  # Duplicates should be removed
        expect_success_with_value(result, {1, 2, 3})


# =============================================================================
# Test Suite: Security - DoS Protection
# =============================================================================


class DescribeFromTypeSecurityDoSProtection:
    """Test from_type() DoS protection via input length validation.

    Following OWASP best practices and the security pattern from parse_phone (v0.9.1).
    Critical: Reject oversized inputs BEFORE expensive operations (parse_json).
    """

    def it_rejects_excessively_long_json_array_input_quickly(self) -> None:
        """Reject extremely long JSON array input to prevent DoS attacks.

        Security pattern: Validate input length BEFORE expensive operations.
        Performance requirement: Rejection must complete in < 10ms.
        """
        import time

        # Malicious input: 1MB JSON array
        malicious_input = '[' + ', '.join(['1'] * 100000) + ']'
        parser = from_type(list[int])

        start = time.perf_counter()
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        expect_failure_containing(result, 'too long')
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms (DoS vulnerability)'

    def it_rejects_excessively_long_json_dict_input_quickly(self) -> None:
        """Reject extremely long JSON dict input to prevent DoS attacks."""
        import time

        # Malicious input: Large JSON object
        malicious_input = '{' + ', '.join([f'"key{i}": {i}' for i in range(10000)]) + '}'
        parser = from_type(dict[str, int])

        start = time.perf_counter()
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        expect_failure_containing(result, 'too long')
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms (DoS vulnerability)'

    def it_rejects_excessively_long_json_set_input_quickly(self) -> None:
        """Reject extremely long JSON set input to prevent DoS attacks."""
        import time

        # Malicious input: 1MB JSON array (parsed as set)
        malicious_input = '[' + ', '.join([str(i) for i in range(100000)]) + ']'
        parser = from_type(set[int])

        start = time.perf_counter()
        result = parser(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        expect_failure_containing(result, 'too long')
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms (DoS vulnerability)'

    def it_accepts_reasonable_length_json_input(self) -> None:
        """Accept JSON input within reasonable length limits."""
        # 5KB JSON array - well within 10KB limit
        reasonable_input = '[' + ', '.join([str(i) for i in range(500)]) + ']'
        parser = from_type(list[int])

        result = parser(reasonable_input)

        # Should succeed
        match result:
            case Success(value):
                assert len(value) == 500
            case Failure(err):
                pytest.fail(f'Expected success for reasonable input, got: {err}')
