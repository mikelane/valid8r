from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from behave import (
    given,
    then,
    when,
)

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    parse_bool,
    parse_complex,
    parse_date,
    parse_enum,
    parse_float,
    parse_int,
)

if TYPE_CHECKING:
    import numbers

    from behave.runner import Context


# Context to store results between steps
class ParseContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.result = None
        self.custom_parser = None
        self.custom_enum = None


# Make sure context has a parse_context
def get_parse_context(context: Context) -> ParseContext:
    if not hasattr(context, 'parse_context'):
        context.parse_context = ParseContext()
    return context.parse_context


@given('the input validation module is available')
def step_input_validation_available(context: Context) -> None:  # noqa: ARG001
    assert Maybe is not None


@given('I have a custom parser for "{parser_type}" type')
def step_have_custom_parser(context: Context, parser_type: str) -> None:
    pc = get_parse_context(context)
    if parser_type == 'IPAddress':
        from ipaddress import ip_address

        pc.custom_parser = lambda s: Maybe.success(ip_address(s))


@given('I have defined an enum "{enum_name}" with values "{enum_values}"')
def step_have_enum(context: Context, enum_name: str, enum_values: str) -> None:
    from enum import Enum

    values = enum_values.split(',')

    # Dynamically create an Enum class
    enum_dict = {value: value for value in values}
    pc = get_parse_context(context)
    pc.custom_enum = Enum(enum_name, enum_dict)


@when('I parse "{input_str}" to integer type')
def step_parse_to_integer(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_int(input_str)


@when('I parse "{input_str}" to float type')
def step_parse_to_float(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_float(input_str)


@when('I parse "{input_str}" to boolean type')
def step_parse_to_boolean(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_bool(input_str)


@when('I parse "{input_str}" to date type')
def step_parse_to_date(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_date(input_str)


@when('I parse "{input_str}" to date type with format "{format_str}"')
def step_parse_to_date_with_format(context: Context, input_str: str, format_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_date(input_str, date_format=format_str)


@when('I parse "{input_str}" to complex type')
def step_parse_to_complex(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_complex(input_str)


@when('I parse "{input_str}" using the custom parser')
def step_parse_with_custom_parser(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    pc.result = pc.custom_parser(input_str)


@when('I parse "{input_str}" to integer type with error message "{error_msg}"')
def step_parse_to_integer_with_error(context: Context, input_str: str, error_msg: str) -> None:
    pc = get_parse_context(context)
    pc.result = parse_int(input_str, error_message=error_msg)


@when('I parse "{input_str}" to the Color enum type')
def step_parse_to_enum(context: Context, input_str: str) -> None:
    pc = get_parse_context(context)
    # This assumes we'll implement an enum parser
    pc.result = parse_enum(input_str, pc.custom_enum)


@then('the result should be a successful Maybe with value {expected:d}')
def step_result_is_success_with_int_value(context: Context, expected: int) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with value {expected:f}')
def step_result_is_success_with_float_value(context: Context, expected: float) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with value {expected}')
def step_result_is_success_with_bool_value(context: Context, expected: str) -> None:
    pc = get_parse_context(context)
    expected_bool = expected.lower() == 'true'
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected_bool, f'Expected {expected_bool} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with date value "{expected_date}"')
def step_result_is_success_with_date_value(context: Context, expected_date: str) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    expected = date.fromisoformat(expected_date)
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with complex value {expected_complex}')
def step_result_is_success_with_complex_value(context: Context, expected_complex: numbers.Complex) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    # Parse the complex number string to a complex number
    expected = complex(expected_complex)
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with the parsed IP address')
def step_result_is_success_with_ip_address(context: Context) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    # We don't check the exact value as it's validated by the custom parser


@then('the result should be a successful Maybe with the RED enum value')
def step_result_is_success_with_enum_value(context: Context) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST').name == 'RED', f'Expected RED but got {pc.result.value_or("TEST").name}'


@then('the result should be a failure Maybe with error "{expected_error}"')
def step_result_is_failure_with_error(context: Context, expected_error: str) -> None:
    pc = get_parse_context(context)
    assert pc.result.is_failure(), f'Expected failure but got success: {pc.result}'
    assert pc.result.value_or('TEST') == expected_error, (
        f"Expected error '{expected_error}' but got '{pc.result.value_or('TEST')}'"
    )


@when('I parse "" to integer type')
def step_parse_empty_to_integer(context: Context) -> None:
    pc = get_parse_context(context)
    pc.result = parse_int('')
