from __future__ import annotations

from behave import (
    given,
    then,
    when,
)
from valid8r.core.validators import (
    between,
    length,
    maximum,
    minimum,
    predicate,
)


# Context to store results between steps
class ValidatorContext:
    def __init__(self) -> None:
        self.result = None


# Make sure context has a validator_context
def get_validator_context(context):
    if not hasattr(context, 'validator_context'):
        context.validator_context = ValidatorContext()
    return context.validator_context


@given('the validation module is available')
def step_validation_module_available(context):
    # Check that the validators module is imported correctly
    assert minimum is not None
    assert maximum is not None
    assert between is not None
    assert length is not None
    assert predicate is not None


@when('I validate {value:d} against a minimum of {min_val:d}')
def step_validate_minimum(context, value, min_val):
    vc = get_validator_context(context)
    validator = minimum(min_val)
    vc.result = validator(value)


@when('I validate {value:d} against a maximum of {max_val:d}')
def step_validate_maximum(context, value, max_val):
    vc = get_validator_context(context)
    validator = maximum(max_val)
    vc.result = validator(value)


@when('I validate {value:d} against a range of {min_val:d} to {max_val:d}')
def step_validate_between(context, value, min_val, max_val):
    vc = get_validator_context(context)
    validator = between(min_val, max_val)
    vc.result = validator(value)


@when('I validate "{value}" against a length of {min_len:d} to {max_len:d}')
def step_validate_length(context, value, min_len, max_len):
    vc = get_validator_context(context)
    validator = length(min_len, max_len)
    vc.result = validator(value)


@when('I validate {value:d} with a predicate "{error_msg}" that checks if a value is even')
def step_validate_predicate(context, value, error_msg):
    vc = get_validator_context(context)
    validator = predicate(lambda x: x % 2 == 0, error_msg)
    vc.result = validator(value)


@when('I validate {value:d} against a minimum of {min_val:d} with error message "{error_msg}"')
def step_validate_minimum_with_error(context, value, min_val, error_msg):
    vc = get_validator_context(context)
    validator = minimum(min_val, error_msg)
    vc.result = validator(value)


@then('the validation result should be a successful Maybe with value {expected:d}')
def step_validation_result_is_success_with_int_value(context, expected):
    vc = get_validator_context(context)
    assert vc.result.is_just(), f'Expected success but got failure: {vc.result}'
    assert vc.result.value() == expected, f'Expected {expected} but got {vc.result.value()}'


@then('the validation result should be a successful Maybe with string value "{expected}"')
def step_validation_result_is_success_with_string_value(context, expected):
    vc = get_validator_context(context)
    assert vc.result.is_just(), f'Expected success but got failure: {vc.result}'
    assert vc.result.value() == expected, f'Expected {expected} but got {vc.result.value()}'


@then('the validation result should be a failure Maybe with error "{expected_error}"')
def step_validation_result_is_failure_with_error(context, expected_error):
    vc = get_validator_context(context)
    assert vc.result.is_nothing(), f'Expected failure but got success: {vc.result}'
    assert vc.result.error() == expected_error, f"Expected error '{expected_error}' but got '{vc.result.error()}'"


@then('the validation result should be a failure Maybe')
def step_validation_result_is_failure(context):
    vc = get_validator_context(context)
    assert vc.result.is_nothing(), f'Expected failure but got success: {vc.result}'
