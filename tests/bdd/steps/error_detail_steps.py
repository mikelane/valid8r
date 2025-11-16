"""Step definitions for structured error information feature."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import (
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
    from behave.runner import Context


# Scenario 1: Access error details from simple validation failure
@given('I validate user input that fails with "{error_message}"')
def step_validate_failing_input(context: Context, error_message: str) -> None:
    """Simulate validation failure with specific error message."""
    # Implementation detail: We use Failure class here, not in Gherkin
    context.validation_failure = Failure(error_message)


@when('I examine the validation error')
def step_examine_error(context: Context) -> None:
    """Access structured error information."""
    # Implementation detail: We call error_detail() here, not in Gherkin
    context.error_info = context.validation_failure.error_detail()


@then('I can access the error code')
def step_verify_error_code_accessible(context: Context) -> None:
    """Verify error code is accessible."""
    # Implementation detail: We check .code attribute here
    assert hasattr(context.error_info, 'code')
    assert context.error_info.code is not None


@then('I can access the error message "{expected_message}"')
def step_verify_error_message(context: Context, expected_message: str) -> None:
    """Verify error message is accessible."""
    assert hasattr(context.error_info, 'message')
    assert context.error_info.message == expected_message


@then('the error path is empty')
def step_verify_error_path_empty(context: Context) -> None:
    """Verify error path is empty."""
    assert hasattr(context.error_info, 'path')
    assert context.error_info.path == ''


@then('no additional context is provided')
def step_verify_no_context(context: Context) -> None:
    """Verify context is None."""
    assert hasattr(context.error_info, 'context')
    assert context.error_info.context is None


# Scenario 2: Access detailed error information with context
@given('I validate a temperature value that is out of range')
def step_validate_temperature_out_of_range(context: Context) -> None:
    """Simulate temperature validation failure with context."""
    # Implementation detail: Create ValidationError with all details
    error = ValidationError(
        code='OUT_OF_RANGE',
        message='Value must be between 0 and 100',
        path='.temperature',
        context={'min': 0, 'max': 100},
    )
    context.validation_failure = Failure(error)


@then('the error code indicates "{expected_code}"')
def step_verify_error_code_value(context: Context, expected_code: str) -> None:
    """Verify error code has expected value."""
    assert context.error_info.code == expected_code


@then('the error message explains the constraint')
def step_verify_error_message_explains(context: Context) -> None:
    """Verify error message is informative."""
    assert hasattr(context.error_info, 'message')
    assert len(context.error_info.message) > 0
    # Check message contains constraint information
    assert 'between' in context.error_info.message.lower() or 'range' in context.error_info.message.lower()


@then('the error path points to the temperature field')
def step_verify_error_path_temperature(context: Context) -> None:
    """Verify error path identifies temperature field."""
    assert context.error_info.path == '.temperature'


@then('the context includes minimum and maximum values')
def step_verify_context_has_min_max(context: Context) -> None:
    """Verify context contains min/max values."""
    assert context.error_info.context is not None
    assert 'min' in context.error_info.context
    assert 'max' in context.error_info.context
    assert context.error_info.context['min'] == 0
    assert context.error_info.context['max'] == 100


# Scenario 3: Backward compatibility with string-based error handling
@given('I have existing code that uses string error messages')
def step_existing_string_code(context: Context) -> None:
    """Create Failure with string-based error."""
    # Create a Failure with string error for backward compatibility test
    context.validation_failure = Failure('Something went wrong')


@when('a validation fails')
def step_validation_fails(context: Context) -> None:
    """Mark that validation failure has occurred."""
    # Failure already created in Given step


@then('I can still access the error as a string')
def step_verify_string_access(context: Context) -> None:
    """Verify error can be accessed as string via error_or()."""
    # Implementation detail: Use error_or() method
    error_string = context.validation_failure.error_or('default')
    assert isinstance(error_string, str)
    assert error_string == 'Something went wrong'


@then('I can optionally access structured error details')
def step_verify_structured_access(context: Context) -> None:
    """Verify error_detail() provides structured information."""
    # Implementation detail: Use error_detail() method
    error_detail = context.validation_failure.error_detail()
    assert isinstance(error_detail, ValidationError)
    assert error_detail.message == 'Something went wrong'


# Scenario 4: Error information persists through transformations
@given('a validation failure occurs')
def step_validation_failure_occurs(context: Context) -> None:
    """Create validation failure."""
    error = ValidationError(code='INITIAL_ERROR', message='Initial error message')
    context.validation_failure = Failure(error)
    # Save original for comparison
    context.original_error = context.validation_failure.error_detail()


@when('I chain additional transformations')
def step_chain_transformations(context: Context) -> None:
    """Apply monadic transformations (bind and map)."""
    # Implementation detail: Use bind and map operations
    context.after_bind = context.validation_failure.bind(lambda x: Maybe.success(x * 2))
    context.after_map = context.validation_failure.map(lambda x: x * 2)


@then('the original error information is preserved')
def step_verify_error_preserved(context: Context) -> None:
    """Verify error information unchanged after transformations."""
    # Check bind result
    assert context.after_bind.is_failure()
    bind_error = context.after_bind.error_detail()
    assert bind_error.code == context.original_error.code
    assert bind_error.message == context.original_error.message

    # Check map result
    assert context.after_map.is_failure()
    map_error = context.after_map.error_detail()
    assert map_error.code == context.original_error.code
    assert map_error.message == context.original_error.message


@then('I can still access the complete error details')
def step_verify_complete_details(context: Context) -> None:
    """Verify all error details still accessible."""
    bind_error = context.after_bind.error_detail()
    map_error = context.after_map.error_detail()

    # All fields preserved
    assert bind_error.code == 'INITIAL_ERROR'
    assert map_error.code == 'INITIAL_ERROR'
    assert isinstance(bind_error, ValidationError)
    assert isinstance(map_error, ValidationError)


# Scenario 5: Multiple validation failures have distinct error details
@given('I have two different validation failures')
def step_two_different_failures(context: Context) -> None:
    """Create two distinct validation failures."""
    error1 = ValidationError(code='ERROR_ONE', message='First error')
    error2 = ValidationError(code='ERROR_TWO', message='Second error')
    context.failure_one = Failure(error1)
    context.failure_two = Failure(error2)


@when('I examine each error')
def step_examine_each_error(context: Context) -> None:
    """Get error details from each failure."""
    context.error_one = context.failure_one.error_detail()
    context.error_two = context.failure_two.error_detail()


@then('each has its own error code')
def step_verify_distinct_codes(context: Context) -> None:
    """Verify error codes are different."""
    assert context.error_one.code == 'ERROR_ONE'
    assert context.error_two.code == 'ERROR_TWO'
    assert context.error_one.code != context.error_two.code


@then('each has its own error message')
def step_verify_distinct_messages(context: Context) -> None:
    """Verify error messages are different."""
    assert context.error_one.message == 'First error'
    assert context.error_two.message == 'Second error'
    assert context.error_one.message != context.error_two.message


@then('the error objects are independent')
def step_verify_independent_objects(context: Context) -> None:
    """Verify error objects are not the same instance."""
    assert context.error_one is not context.error_two


# Scenario 6: Consistent error information from different access methods
@given('a validation failure has occurred')
def step_validation_failure_occurred(context: Context) -> None:
    """Create validation failure."""
    error = ValidationError(code='TEST_ERROR', message='Test error message')
    context.validation_failure = Failure(error)


@when('I access the error information')
def step_access_error_information(context: Context) -> None:
    """Access error via both error_detail() method and validation_error property."""
    # Implementation detail: Use both access methods
    context.via_method = context.validation_failure.error_detail()
    context.via_property = context.validation_failure.validation_error


@then('the structured error details are consistent')
def step_verify_consistent_details(context: Context) -> None:
    """Verify both access methods return same information."""
    # Both should have same code and message
    assert context.via_method.code == context.via_property.code
    assert context.via_method.message == context.via_property.message
    assert context.via_method.path == context.via_property.path
    assert context.via_method.context == context.via_property.context


@then('the same information is available regardless of access method')
def step_verify_same_instance(context: Context) -> None:
    """Verify both methods return the same object instance."""
    # Implementation detail: They should be the same object
    assert context.via_method is context.via_property
