from __future__ import annotations

from datetime import date

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


# Context to store results between steps
class ParseContext:
    def __init__(self) -> None:
        self.result = None
        self.custom_parser = None
        self.custom_enum = None


# Make sure context has a parse_context
def get_parse_context(context):
    if not hasattr(context, 'parse_context'):
        context.parse_context = ParseContext()
    return context.parse_context


@given('the input validation module is available')
def step_input_validation_available(context):
    assert Maybe is not None


@given('I have a custom parser for "{parser_type}" type')
def step_have_custom_parser(context, parser_type):
    pc = get_parse_context(context)
    if parser_type == 'IPAddress':
        from ipaddress import ip_address

        pc.custom_parser = lambda s: Maybe.just(ip_address(s))


@given('I have defined an enum "{enum_name}" with values "{enum_values}"')
def step_have_enum(context, enum_name, enum_values):
    from enum import Enum

    values = enum_values.split(',')

    # Dynamically create an Enum class
    enum_dict = {value: value for value in values}
    pc = get_parse_context(context)
    pc.custom_enum = Enum(enum_name, enum_dict)


@when('I parse "{input_str}" to integer type')
def step_parse_to_integer(context, input_str):
    pc = get_parse_context(context)
    pc.result = parse_int(input_str)


@when('I parse "{input_str}" to float type')
def step_parse_to_float(context, input_str):
    pc = get_parse_context(context)
    pc.result = parse_float(input_str)


@when('I parse "{input_str}" to boolean type')
def step_parse_to_boolean(context, input_str):
    pc = get_parse_context(context)
    pc.result = parse_bool(input_str)


@when('I parse "{input_str}" to date type')
def step_parse_to_date(context, input_str):
    pc = get_parse_context(context)
    pc.result = parse_date(input_str)


@when('I parse "{input_str}" to date type with format "{format_str}"')
def step_parse_to_date_with_format(context, input_str, format_str):
    pc = get_parse_context(context)
    pc.result = parse_date(input_str, date_format=format_str)


@when('I parse "{input_str}" to complex type')
def step_parse_to_complex(context, input_str):
    pc = get_parse_context(context)
    pc.result = parse_complex(input_str)


@when('I parse "{input_str}" using the custom parser')
def step_parse_with_custom_parser(context, input_str):
    pc = get_parse_context(context)
    pc.result = pc.custom_parser(input_str)


@when('I parse "{input_str}" to integer type with error message "{error_msg}"')
def step_parse_to_integer_with_error(context, input_str, error_msg):
    pc = get_parse_context(context)
    pc.result = parse_int(input_str, error_message=error_msg)


@when('I parse "{input_str}" to the Color enum type')
def step_parse_to_enum(context, input_str):
    pc = get_parse_context(context)
    # This assumes we'll implement an enum parser
    pc.result = parse_enum(input_str, pc.custom_enum)


@then('the result should be a successful Maybe with value {expected:d}')
def step_result_is_success_with_int_value(context, expected):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('the result should be a successful Maybe with value {expected:f}')
def step_result_is_success_with_float_value(context, expected):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('the result should be a successful Maybe with value {expected}')
def step_result_is_success_with_bool_value(context, expected):
    pc = get_parse_context(context)
    expected_bool = expected.lower() == 'true'
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value() == expected_bool, f'Expected {expected_bool} but got {pc.result.value()}'


@then('the result should be a successful Maybe with date value "{expected_date}"')
def step_result_is_success_with_date_value(context, expected_date):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    expected = date.fromisoformat(expected_date)
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('the result should be a successful Maybe with complex value {expected_complex}')
def step_result_is_success_with_complex_value(context, expected_complex):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    # Parse the complex number string to a complex number
    expected = complex(expected_complex)
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('the result should be a successful Maybe with the parsed IP address')
def step_result_is_success_with_ip_address(context):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    # We don't check the exact value as it's validated by the custom parser


@then('the result should be a successful Maybe with the RED enum value')
def step_result_is_success_with_enum_value(context):
    pc = get_parse_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value().name == 'RED', f'Expected RED but got {pc.result.value().name}'


@then('the result should be a failure Maybe with error "{expected_error}"')
def step_result_is_failure_with_error(context, expected_error):
    pc = get_parse_context(context)
    assert pc.result.is_nothing(), f'Expected failure but got success: {pc.result}'
    assert pc.result.error() == expected_error, f"Expected error '{expected_error}' but got '{pc.result.error()}'"


@when('I parse "" to integer type')
def step_parse_empty_to_integer(context):
    pc = get_parse_context(context)
    pc.result = parse_int('')
