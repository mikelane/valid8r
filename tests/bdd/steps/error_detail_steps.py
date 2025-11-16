"""Step definitions for error_detail() method feature."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from valid8r.core.errors import ValidationError
from valid8r.core.maybe import (
    Failure,
    Maybe,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# Given steps
@given('the Valid8r library is imported')
def step_valid8r_imported(context: Context) -> None:
    """Valid8r library is available."""
    # Library is already imported at top of file


@given('ValidationError is available from valid8r.core.errors')
def step_validation_error_available(context: Context) -> None:
    """ValidationError is available."""
    # Already imported at top of file


@given('I create a Failure with a string error "{error_message}"')
def step_create_failure_with_string(context: Context, error_message: str) -> None:
    """Create Failure with string error."""
    context.failure = Failure(error_message)


@given('I create a ValidationError with:')
def step_create_validation_error_from_table(context: Context) -> None:
    """Create ValidationError from table data."""
    # Convert table to dict
    data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Handle special values
        if field == 'context':
            value = json.loads(value)
        data[field] = value

    context.validation_error = ValidationError(
        code=data.get('code', 'VALIDATION_ERROR'),
        message=data.get('message', ''),
        path=data.get('path', ''),
        context=data.get('context'),
    )


@given('I create a Failure with that ValidationError')
def step_create_failure_with_validation_error(context: Context) -> None:
    """Create Failure with stored ValidationError."""
    context.failure = Failure(context.validation_error)


@given('I create a ValidationError with code "{code}"')
def step_create_simple_validation_error(context: Context, code: str) -> None:
    """Create simple ValidationError with just code."""
    context.validation_error = ValidationError(code=code, message=f'Error {code}')


@given('I create a Failure with code "{code}" and message "{message}"')
def step_create_failure_with_code_and_message(context: Context, code: str, message: str) -> None:
    """Create Failure with specific code and message."""
    if not hasattr(context, 'failures'):
        context.failures = []
    error = ValidationError(code=code, message=message)
    context.failures.append(Failure(error))


@given('I create a Failure with code "{code}"')
def step_create_failure_with_code(context: Context, code: str) -> None:
    """Create Failure with specific code."""
    error = ValidationError(code=code, message=f'Error message for {code}')
    context.failure = Failure(error)


# When steps
@when('I call error_detail() on the Failure')
def step_call_error_detail(context: Context) -> None:
    """Call error_detail() method."""
    context.error_detail_result = context.failure.error_detail()


@when('I access the validation_error property')
def step_access_validation_error_property(context: Context) -> None:
    """Access validation_error property."""
    context.property_result = context.failure.validation_error


@when('I call error_or("{default}") on the Failure')
def step_call_error_or(context: Context, default: str) -> None:
    """Call error_or() method."""
    context.error_or_result = context.failure.error_or(default)


@when('I pattern match on the Failure')
def step_pattern_match_failure(context: Context) -> None:
    """Pattern match on Failure."""
    match context.failure:
        case Failure(error):
            context.matched_error = error
        case _:
            pytest.fail('Pattern match failed')


@when('I bind the Failure to a transformation function')
def step_bind_failure(context: Context) -> None:
    """Bind Failure to transformation."""
    context.bind_result = context.failure.bind(lambda x: Maybe.success(x * 2))


@when('I map the Failure with a transformation function')
def step_map_failure(context: Context) -> None:
    """Map Failure with transformation."""
    context.map_result = context.failure.map(lambda x: x * 2)


@when('I call error_detail() on each Failure')
def step_call_error_detail_on_each(context: Context) -> None:
    """Call error_detail() on each Failure in list."""
    context.error_details = [f.error_detail() for f in context.failures]


# Then steps
@then('I receive a ValidationError instance')
def step_verify_validation_error_instance(context: Context) -> None:
    """Verify result is ValidationError instance."""
    assert isinstance(context.error_detail_result, ValidationError)


@then('the ValidationError code is "{expected_code}"')
def step_verify_error_code(context: Context, expected_code: str) -> None:
    """Verify ValidationError code."""
    assert context.error_detail_result.code == expected_code


@then('the ValidationError message is "{expected_message}"')
def step_verify_error_message(context: Context, expected_message: str) -> None:
    """Verify ValidationError message."""
    assert context.error_detail_result.message == expected_message


@then('the ValidationError path is "{expected_path}"')
def step_verify_error_path(context: Context, expected_path: str) -> None:
    """Verify ValidationError path."""
    assert context.error_detail_result.path == expected_path


@then('the ValidationError path is ""')
def step_verify_error_path_empty(context: Context) -> None:
    """Verify ValidationError path is empty string."""
    assert context.error_detail_result.path == ''


@then('the ValidationError context is None')
def step_verify_context_none(context: Context) -> None:
    """Verify context is None."""
    assert context.error_detail_result.context is None


@then('both references point to the same ValidationError instance')
def step_verify_same_instance(context: Context) -> None:
    """Verify both references are same object."""
    assert context.error_detail_result is context.property_result


@then('I receive the string "{expected_string}"')
def step_verify_string_result(context: Context, expected_string: str) -> None:
    """Verify string result."""
    assert context.error_or_result == expected_string


@then('I can still call error_detail() to get structured information')
def step_verify_can_call_error_detail(context: Context) -> None:
    """Verify error_detail() can still be called."""
    result = context.failure.error_detail()
    assert isinstance(result, ValidationError)


@then('I can access the context dictionary')
def step_verify_can_access_context(context: Context) -> None:
    """Verify context is accessible."""
    assert context.error_detail_result.context is not None


@then('the context contains "{key}" with value {value:d}')
def step_verify_context_contains(context: Context, key: str, value: int) -> None:
    """Verify context contains key-value pair."""
    assert context.error_detail_result.context[key] == value


@then('the matched error message is "{expected_message}"')
def step_verify_matched_message(context: Context, expected_message: str) -> None:
    """Verify matched error message."""
    assert context.matched_error == expected_message


@then('I can call error_detail() to get the full ValidationError')
def step_verify_error_detail_after_match(context: Context) -> None:
    """Verify error_detail() works after pattern match."""
    result = context.failure.error_detail()
    assert isinstance(result, ValidationError)


@then('the first error_detail() has code "{expected_code}"')
def step_verify_first_error_code(context: Context, expected_code: str) -> None:
    """Verify first error detail code."""
    assert context.error_details[0].code == expected_code


@then('the second error_detail() has code "{expected_code}"')
def step_verify_second_error_code(context: Context, expected_code: str) -> None:
    """Verify second error detail code."""
    assert context.error_details[1].code == expected_code


@then('both are distinct ValidationError instances')
def step_verify_distinct_instances(context: Context) -> None:
    """Verify errors are distinct objects."""
    assert context.error_details[0] is not context.error_details[1]


@then('the result is still a Failure')
def step_verify_result_is_failure(context: Context) -> None:
    """Verify result is Failure."""
    result = getattr(context, 'bind_result', None) or getattr(context, 'map_result', None)
    assert result.is_failure()


@then('calling error_detail() returns the original ValidationError')
def step_verify_original_validation_error(context: Context) -> None:
    """Verify error_detail() returns original error."""
    result = getattr(context, 'bind_result', None) or getattr(context, 'map_result', None)
    original = context.failure.error_detail()
    result_error = result.error_detail()
    # Check same code/message (objects may differ but content same)
    assert result_error.code == original.code
    assert result_error.message == original.message


@then('the error code is still "{expected_code}"')
def step_verify_error_code_unchanged(context: Context, expected_code: str) -> None:
    """Verify error code unchanged."""
    result = getattr(context, 'bind_result', None) or getattr(context, 'map_result', None)
    assert result.error_detail().code == expected_code
