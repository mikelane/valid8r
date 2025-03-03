from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    ip_address,
)
from typing import (
    TYPE_CHECKING,
)

import pytest
from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from tests.bdd.steps import get_custom_context
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.parsers import (
    create_parser,
    make_parser,
    parse_bool,
    parse_complex,
    parse_date,
    parse_enum,
    parse_float,
    parse_int,
)

if TYPE_CHECKING:
    import numbers

    from behave.runner import Context  # type: ignore[import-untyped]


@given('the input validation module is available')
def step_input_validation_available(context: Context) -> None:  # noqa: ARG001
    assert Maybe is not None


@given('I have a custom parser for "{parser_type}" type')
def step_have_custom_parser(context: Context, parser_type: str) -> None:
    ctx = get_custom_context(context)
    if parser_type == 'IPAddress':
        ctx.custom_parser = lambda s: Maybe.success(ip_address(s))
    assert ctx.custom_parser is not None, 'Custom parser has not been defined'


@given('I have created a custom parser for "IPAddress" type using create_parser')
def step_have_custom_parser_using_create_parser(context: Context) -> None:
    ctx = get_custom_context(context)
    ctx.custom_parser = create_parser(ip_address, error_message='Invalid IP address format')
    assert ctx.custom_parser is not None, 'Custom parser has not been created'


@given('I have defined a parser using the make_parser decorator for "Decimal" values')
def step_have_parser_using_make_parser_decorator(context: Context) -> None:
    ctx = get_custom_context(context)

    @make_parser
    def parse_decimal(s: str) -> Decimal:
        return Decimal(s)

    ctx.custom_parser = parse_decimal
    assert ctx.custom_parser is not None, 'Custom parser has not been defined'


@given('I have defined an enum "{enum_name}" with values "{enum_values}"')
def step_have_enum(context: Context, enum_name: str, enum_values: str) -> None:
    values = [v.strip() for v in enum_values.split(',')]

    enum_dict = {value: value for value in values}
    ctx = get_custom_context(context)
    ctx.custom_enum = Enum(enum_name, enum_dict)  # type: ignore[misc]
    assert ctx.custom_enum is not None, 'Custom enum has not been defined'


@when('I parse "{input_str}" to integer type')
def step_parse_to_integer(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_int(input_str)
    # Since this parsing step is used in multiple passing and failing scenarios, we don't check the result here, but
    # we do need to make sure the right kind of result is stored in the context.
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "" to integer type')
def step_parse_empty_to_integer(context: Context) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_int('')
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to float type')
def step_parse_to_float(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_float(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to boolean type')
def step_parse_to_boolean(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_bool(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to date type')
def step_parse_to_date(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_date(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to date type with format "{format_str}"')
def step_parse_to_date_with_format(context: Context, input_str: str, format_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_date(input_str, date_format=format_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to complex type')
def step_parse_to_complex(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_complex(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" using the custom parser')
def step_parse_with_custom_parser(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    if ctx.custom_parser is None:
        raise RuntimeError('No custom parser has been defined')
    ctx.result = ctx.custom_parser(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to integer type with error message "{error_msg}"')
def step_parse_to_integer_with_error(context: Context, input_str: str, error_msg: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_int(input_str, error_message=error_msg)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" to the Color enum type')
def step_parse_to_enum(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    # This assumes we'll implement an enum parser
    ctx.result = parse_enum(input_str, ctx.custom_enum)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "{input_str}" using the decorated parser')
def step_parse_with_decorated_parser(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = ctx.custom_parser(input_str)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@when('I parse "" using the decorated parser')
def step_parse_empty_with_decorated_parser(context: Context) -> None:
    ctx = get_custom_context(context)
    ctx.result = ctx.custom_parser('')
    match ctx.result:
        case Success(_):
            assert True
        case Failure(_):
            assert True
        case _:
            pytest.fail('Unexpected result type')


@then('the result should be a successful Maybe with value {expected:d}')
def step_result_is_success_with_int_value(context: Context, expected: int) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == expected, f'Expected {expected} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with value {expected:f}')
def step_result_is_success_with_float_value(context: Context, expected: float) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == expected, f'Expected {expected} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with value {expected}')
def step_result_is_success_with_bool_value(context: Context, expected: str) -> None:
    ctx = get_custom_context(context)
    expected_bool = expected.lower() == 'true'
    match ctx.result:
        case Success(value):
            assert value == expected_bool, f'Expected {expected_bool} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with date value "{expected_date}"')
def step_result_is_success_with_date_value(context: Context, expected_date: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            expected = date.fromisoformat(expected_date)
            assert value == expected, f'Expected {expected} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with complex value {expected_complex}')
def step_result_is_success_with_complex_value(context: Context, expected_complex: numbers.Complex) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == complex(expected_complex), f'Expected {expected_complex} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with the parsed IP address')
def step_result_is_success_with_ip_address(context: Context) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, IPv4Address), f'Expected ip_address but got {type(value)}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a successful Maybe with the RED enum value')
def step_result_is_success_with_enum_value(context: Context) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == ctx.custom_enum.RED, f'Expected {ctx.custom_enum.RED} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')


@then('the result should be a failure Maybe with error "{expected_error}"')
def step_result_is_failure_with_error(context: Context, expected_error: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            pytest.fail(f'Expected failure but got success: {value}')
        case Failure(error):
            assert error == expected_error


@then('the result should be a successful Maybe with decimal value {expected}')
def step_result_is_success_with_decimal_value(context: Context, expected: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            expected_decimal = Decimal(expected)
            assert value == Decimal(expected_decimal), f'Expected {expected_decimal} but got {value}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
