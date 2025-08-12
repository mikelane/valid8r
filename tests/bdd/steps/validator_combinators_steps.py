from __future__ import annotations

from typing import TYPE_CHECKING

from behave import (
    given,
    then,
    when,
)

from valid8r.core.combinators import (
    and_then,
    not_validator,
    or_else,
)
from valid8r.core.validators import (
    Validator,
    maximum,
    minimum,
    predicate,
)

if TYPE_CHECKING:
    from behave.runner import Context


# Context to store results between steps
class CombinatorContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.result = None


# Make sure context has a combinator_context
def get_combinator_context(context: Context) -> CombinatorContext:
    if not hasattr(context, 'combinator_context'):
        context.combinator_context = CombinatorContext()
    return context.combinator_context


@given('the combinator module is available')
def step_combinator_module_available(context: Context) -> None:  # noqa: ARG001
    # Check that the combinators module is imported correctly
    assert and_then is not None
    assert or_else is not None
    assert not_validator is not None
    assert Validator is not None


@when('I validate {value:d} against a validator that combines minimum {min_val:d} AND maximum {max_val:d}')
def step_validate_minimum_and_maximum(context: Context, value: int, min_val: int, max_val: int) -> None:
    cc = get_combinator_context(context)
    min_validator = minimum(min_val)
    max_validator = maximum(max_val)
    combined_validator = and_then(min_validator, max_validator)
    cc.result = combined_validator(value)


@when('I validate {value:d} against a validator that combines "is even" OR "is divisible by 5"')
def step_validate_even_or_div5(context: Context, value: int) -> None:
    cc = get_combinator_context(context)
    is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')
    is_div_by_5 = predicate(lambda x: x % 5 == 0, 'Value must be divisible by 5')
    combined_validator = or_else(is_even, is_div_by_5)
    cc.result = combined_validator(value)


@when('I validate {value:d} against a validator that negates "is even"')
def step_validate_not_even(context: Context, value: int) -> None:
    cc = get_combinator_context(context)
    is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')
    not_even = not_validator(is_even, 'Value must be odd')
    cc.result = not_even(value)


@when('I validate {value:d} against a validator that combines minimum {min_val:d} AND (is even OR is divisible by 5)')
def step_validate_complex_combinators(context: Context, value: int, min_val: int) -> None:
    cc = get_combinator_context(context)
    min_validator = minimum(min_val)
    is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')
    is_div_by_5 = predicate(lambda x: x % 5 == 0, 'Value must be divisible by 5')

    # Create complex validator: min_val AND (is_even OR is_div_by_5)
    or_validator = or_else(is_even, is_div_by_5)
    combined_validator = and_then(min_validator, or_validator)

    cc.result = combined_validator(value)


@when('I validate {value:d} against a validator created with operator &')
def step_validate_operator_and(context: Context, value: int) -> None:
    cc = get_combinator_context(context)
    min_validator = minimum(0)
    max_validator = maximum(100)

    # Use the & operator
    combined_validator = min_validator & max_validator

    cc.result = combined_validator(value)


@then('the combinator result should be a successful Maybe with value {expected:d}')
def step_combinator_result_is_success_with_int_value(context: Context, expected: int) -> None:
    cc = get_combinator_context(context)
    assert cc.result.is_success(), f'Expected success but got failure: {cc.result}'
    assert cc.result.value_or('TEST') == expected, f'Expected {expected} but got {cc.result.value_or("TEST")}'


@then('the combinator result should be a failure Maybe with error "{expected_error}"')
def step_combinator_result_is_failure_with_error(context: Context, expected_error: str) -> None:
    cc = get_combinator_context(context)
    assert cc.result.is_failure(), f'Expected failure but got success: {cc.result}'
    assert cc.result.error_or('TEST') == expected_error, (
        f"Expected error '{expected_error}' but got '{cc.result.value_or('TEST')}'"
    )


@then('the combinator result should be a failure Maybe')
def step_combinator_result_is_failure(context: Context) -> None:
    cc = get_combinator_context(context)
    assert cc.result.is_failure(), f'Expected failure but got success: {cc.result}'
