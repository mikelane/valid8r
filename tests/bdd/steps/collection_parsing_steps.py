from __future__ import annotations

import json
from typing import (
    TYPE_CHECKING,
)

import pytest
from behave import (  # type: ignore[import-untyped]
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
    parse_dict,
    parse_dict_with_validation,
    parse_int,
    parse_list,
    parse_list_with_validation,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


@when('I parse "{input_str}" to a list of integers')
def step_parse_to_list_of_integers(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_list(input_str, element_parser=parse_int)


@when('I parse "{input_str}" to a list of integers with separator "{separator}"')
def step_parse_to_list_with_separator(context: Context, input_str: str, separator: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_list(input_str, element_parser=parse_int, separator=separator)


@when('I parse "{input_str}" to a dictionary with string keys and integer values')
def step_parse_to_dict_with_int_values(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_dict(input_str, key_parser=lambda s: Maybe.success(s), value_parser=parse_int)


@when('I parse "{input_str}" to a dictionary with pair separator "{pair_sep}" and key-value separator "{kv_sep}"')
def step_parse_to_dict_with_separators(context: Context, input_str: str, pair_sep: str, kv_sep: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_dict(
        input_str,
        key_parser=lambda s: Maybe.success(s),
        value_parser=parse_int,
        pair_separator=pair_sep,
        key_value_separator=kv_sep,
    )


@when('I parse "{input_str}" to a dictionary')
def step_parse_to_dict(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_dict(input_str)


@when('I parse "{input_str}" to a dictionary with integer values')
def step_parse_to_dict_with_int_values_only(context: Context, input_str: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_dict(input_str, value_parser=parse_int)


@when('I parse "{input_str}" to a list with minimum length {min_length:d}')
def step_parse_to_list_with_min_length(context: Context, input_str: str, min_length: int) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_list_with_validation(input_str, element_parser=parse_int, min_length=min_length)


@when('I parse "{input_str}" to a dictionary with required keys "{required_keys}"')
def step_parse_to_dict_with_required_keys(context: Context, input_str: str, required_keys: str) -> None:
    ctx = get_custom_context(context)
    ctx.result = parse_dict_with_validation(
        input_str, key_parser=lambda s: Maybe.success(s), value_parser=parse_int, required_keys=required_keys.split(',')
    )


@then('the result should be a successful Maybe with list value {expected_list}')
def step_result_is_success_with_list_value(context: Context, expected_list: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(result):
            expected = json.loads(expected_list)
            assert result == expected, f'Expected {expected} but got {result}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('the result should be a successful Maybe with dictionary value {expected_dict}')
def step_result_is_success_with_dict_value(context: Context, expected_dict: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(result):
            expected = json.loads(expected_dict)
            assert result == expected, f'Expected {expected} but got {result}'
        case Failure(error):
            pytest.fail(f'Expected success but got failure: {error}')
        case _:
            pytest.fail('Unexpected result type')


@then('the result should be a failure Maybe with error containing "{expected_error}"')
def step_result_is_failure_with_error_containing(context: Context, expected_error: str) -> None:
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(result):
            pytest.fail(f'Expected failure but got success: {result}')
        case Failure(error):
            assert error == expected_error, f'Expected "{expected_error}" but got "{error}"'
        case _:
            pytest.fail('Unexpected result type')
