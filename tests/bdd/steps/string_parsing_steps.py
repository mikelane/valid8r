"""BDD step definitions for string parser feature.

This module implements black-box tests for the parse_str parser through
step definitions that exercise the public interface.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest
from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from valid8r.core.maybe import (
    Failure,
    Success,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


class StringParsingContext:
    """Extended context for string parsing scenarios."""

    def __init__(self) -> None:
        """Initialize the string parsing context."""
        self.input_value: Any = None
        self.custom_error_message: str | None = None
        self.result: Any = None
        self.schema: Any = None
        self.validation_data: dict[str, Any] = {}
        self.validation_result: Any = None
        self.validator: Any = None


def get_string_context(context: Context) -> StringParsingContext:
    """Get or create the string parsing context for the current test."""
    if not hasattr(context, 'string_parsing_context'):
        context.string_parsing_context = StringParsingContext()
    return context.string_parsing_context


# Given steps - Setup test inputs


@given('the input "{input_value}"')
def step_given_string_input(context: Context, input_value: str) -> None:
    """Store string input value."""
    ctx = get_string_context(context)
    ctx.input_value = input_value


@given('the input ""')
def step_given_empty_string(context: Context) -> None:
    """Store empty string input."""
    ctx = get_string_context(context)
    ctx.input_value = ''


@given('the input is a string with {length:d} characters')
def step_given_long_string(context: Context, length: int) -> None:
    """Generate a long string of specified length."""
    ctx = get_string_context(context)
    ctx.input_value = 'a' * length


@given('the input None')
def step_given_none_input(context: Context) -> None:
    """Store None as input value."""
    ctx = get_string_context(context)
    ctx.input_value = None


@given('the input {number:d}')
def step_given_integer_input(context: Context, number: int) -> None:
    """Store integer input value."""
    ctx = get_string_context(context)
    ctx.input_value = number


@given('the input {number:f}')
def step_given_float_input(context: Context, number: float) -> None:
    """Store float input value."""
    ctx = get_string_context(context)
    ctx.input_value = number


@given('the input True')
def step_given_true_input(context: Context) -> None:
    """Store boolean True input value."""
    ctx = get_string_context(context)
    ctx.input_value = True


@given('the input {"key": "value"}')
def step_given_dict_input(context: Context) -> None:
    """Store dict input value."""
    ctx = get_string_context(context)
    ctx.input_value = {'key': 'value'}


@given('the input ["a", "b", "c"]')
def step_given_list_input(context: Context) -> None:
    """Store list input value."""
    ctx = get_string_context(context)
    ctx.input_value = ['a', 'b', 'c']


@given('the error message "{error_message}"')
def step_given_custom_error_message(context: Context, error_message: str) -> None:
    """Store custom error message."""
    ctx = get_string_context(context)
    ctx.custom_error_message = error_message


@given('a schema with a required "{field_name}" field using parse_str')
def step_given_schema_with_parse_str(context: Context, field_name: str) -> None:
    """Create a schema with a required string field using parse_str."""
    from valid8r.core.parsers import parse_str
    from valid8r.core.schema import (
        Field,
        Schema,
    )

    ctx = get_string_context(context)
    ctx.schema = Schema(fields={field_name: Field(parser=parse_str, required=True)})


@given('parse_str to validate type')
def step_given_parse_str_parser(context: Context) -> None:
    """Store parse_str parser for later use."""
    ctx = get_string_context(context)
    # Store parse_str for use in validation chains
    ctx.result = None  # Will be set by when step


@given('non_empty_string validator for content')
def step_given_non_empty_validator(context: Context) -> None:
    """Store non_empty_string validator."""
    from valid8r.core.validators import non_empty_string

    ctx = get_string_context(context)
    ctx.validator = non_empty_string()


@given('parse_str parser')
def step_given_parse_str_only(context: Context) -> None:
    """Store parse_str parser."""
    # Parser will be used in when step - no setup needed


@given('a custom validator checking string length')
def step_given_custom_length_validator(context: Context) -> None:
    """Create a custom validator checking string length."""
    from valid8r.core.maybe import Maybe

    def length_validator(s: str) -> Maybe[str]:
        if len(s) >= 3:
            return Maybe.success(s)
        return Maybe.failure('String must be at least 3 characters')

    ctx = get_string_context(context)
    ctx.validator = length_validator


# When steps - Perform actions


@when('I call parse_str with the input')
def step_when_call_parse_str(context: Context) -> None:
    """Call parse_str with stored input value."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    ctx.result = parse_str(ctx.input_value)


@when('I call parse_str with the input and custom error message')
def step_when_call_parse_str_with_error_message(context: Context) -> None:
    """Call parse_str with custom error message."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    ctx.result = parse_str(ctx.input_value, error_message=ctx.custom_error_message)


@when('I validate data {"name": "Alice"}')
def step_when_validate_data_alice(context: Context) -> None:
    """Validate data with schema."""
    ctx = get_string_context(context)
    ctx.validation_data = {'name': 'Alice'}
    ctx.validation_result = ctx.schema.validate(ctx.validation_data)


@when('I validate data {"name": 42}')
def step_when_validate_data_number(context: Context) -> None:
    """Validate data with integer in string field."""
    ctx = get_string_context(context)
    ctx.validation_data = {'name': 42}
    ctx.validation_result = ctx.schema.validate(ctx.validation_data)


@when('I parse and validate ""')
def step_when_parse_and_validate_empty(context: Context) -> None:
    """Parse empty string and validate with non_empty_string."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    ctx.input_value = ''
    # First parse (should succeed - empty string is valid type)
    parse_result = parse_str(ctx.input_value)
    # Then validate content (should fail - empty string invalid content)
    if parse_result.is_success():
        ctx.result = parse_result.bind(ctx.validator)
    else:
        ctx.result = parse_result


@when('I parse "{input_str}" and validate')
def step_when_parse_and_validate(context: Context, input_str: str) -> None:
    """Parse string and apply custom validator."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    ctx.input_value = input_str
    # Parse then validate
    parse_result = parse_str(ctx.input_value)
    if parse_result.is_success():
        ctx.result = parse_result.bind(ctx.validator)
    else:
        ctx.result = parse_result


# Then steps - Verify results


@then('it returns Success with value "{expected_value}"')
def step_then_success_with_value(context: Context, expected_value: str) -> None:
    """Verify result is Success with expected string value."""
    ctx = get_string_context(context)
    match ctx.result:
        case Success(value):
            assert value == expected_value, f'Expected {expected_value!r} but got {value!r}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('it returns Success with value ""')
def step_then_success_with_empty_string(context: Context) -> None:
    """Verify result is Success with empty string."""
    ctx = get_string_context(context)
    match ctx.result:
        case Success(value):
            assert value == '', f'Expected empty string but got {value!r}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('it returns Success with the {length:d} character string')
def step_then_success_with_long_string(context: Context, length: int) -> None:
    """Verify result is Success with long string of expected length."""
    ctx = get_string_context(context)
    match ctx.result:
        case Success(value):
            assert len(value) == length, f'Expected string of length {length} but got {len(value)}'
            assert value == 'a' * length, 'String content does not match expected'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('it returns Failure with message containing "{error_substring}"')
def step_then_failure_with_message_containing(context: Context, error_substring: str) -> None:
    """Verify result is Failure with message containing substring."""
    ctx = get_string_context(context)
    match ctx.result:
        case Failure(error):
            assert error_substring.lower() in error.lower(), (
                f'Expected error containing {error_substring!r} but got {error!r}'
            )
        case Success(value):
            pytest.fail(f'Expected failure but got success: {value}')
        case _:
            pytest.fail('Unexpected result type')


@then('it returns Failure with message "{expected_message}"')
def step_then_failure_with_exact_message(context: Context, expected_message: str) -> None:
    """Verify result is Failure with exact message."""
    ctx = get_string_context(context)
    match ctx.result:
        case Failure(error):
            assert error == expected_message, f'Expected {expected_message!r} but got {error!r}'
        case Success(value):
            pytest.fail(f'Expected failure but got success: {value}')
        case _:
            pytest.fail('Unexpected result type')


@then('validation succeeds with name "{expected_name}"')
def step_then_schema_validation_succeeds(context: Context, expected_name: str) -> None:
    """Verify schema validation succeeded with expected name value."""
    ctx = get_string_context(context)
    match ctx.validation_result:
        case Success(data):
            assert 'name' in data, 'Expected "name" field in validated data'
            assert data['name'] == expected_name, f'Expected name {expected_name!r} but got {data["name"]!r}'
        case Failure(error):
            pytest.fail(f'Expected validation success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('validation fails with error at path "{field_path}" containing "{error_substring}"')
def step_then_schema_validation_fails(context: Context, field_path: str, error_substring: str) -> None:
    """Verify schema validation failed with error at expected path."""
    ctx = get_string_context(context)
    if ctx.validation_result is None:
        pytest.fail('validation_result is None - schema validation was not executed')

    # Use is_failure() method instead of pattern matching for reliability
    if ctx.validation_result.is_success():
        pytest.fail(f'Expected validation failure but got success: {ctx.validation_result.value_or(None)}')

    if not ctx.validation_result.is_failure():
        pytest.fail(f'Unexpected result type: {type(ctx.validation_result)}, value: {ctx.validation_result}')

    # Extract errors from Failure using public validation_error property
    errors = ctx.validation_result.validation_error
    error_list = errors if isinstance(errors, list) else [errors]

    # Find error matching field path
    # ValidationError uses 'path' attribute, not 'field_path'
    matching_errors = [e for e in error_list if hasattr(e, 'path') and e.path == field_path]
    assert matching_errors, f'No error found at path {field_path!r}. Errors: {error_list}'
    error_msg = str(matching_errors[0])
    assert error_substring.lower() in error_msg.lower(), (
        f'Expected error containing {error_substring!r} but got {error_msg!r}'
    )


@then('type validation succeeds but content validation fails')
def step_then_type_succeeds_content_fails(context: Context) -> None:
    """Verify type validation passed but content validation failed."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    # Verify parse_str succeeded
    parse_result = parse_str(ctx.input_value)
    assert parse_result.is_success(), 'Expected type validation (parse_str) to succeed'

    # Verify final result (after validator) failed
    match ctx.result:
        case Failure(error):
            # Content validation should fail with appropriate message
            assert 'empty' in error.lower() or 'required' in error.lower(), (
                f'Expected content validation error but got: {error}'
            )
        case Success(_):
            pytest.fail('Expected content validation to fail')
        case _:
            pytest.fail('Unexpected result type')


@then('parsing succeeds and validation applies to the string value')
def step_then_parsing_succeeds_and_validation_applies(context: Context) -> None:
    """Verify parsing succeeded and validator was applied to string value."""
    from valid8r.core.parsers import parse_str

    ctx = get_string_context(context)
    # Verify parse_str succeeded
    parse_result = parse_str(ctx.input_value)
    assert parse_result.is_success(), 'Expected parsing to succeed'

    # Verify validation was applied (final result should be Success for "hello" with length >= 3)
    match ctx.result:
        case Success(value):
            assert value == ctx.input_value, f'Expected {ctx.input_value!r} but got {value!r}'
        case Failure(error):
            pytest.fail(f'Expected validation to succeed for "hello" but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')
