from __future__ import annotations

import ipaddress
import json
from typing import TYPE_CHECKING

from behave import (
    given,
    then,
    when,
)

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    ParserRegistry,
    parse_dict,
    parse_dict_with_validation,
    parse_int,
    parse_list,
    parse_list_with_validation,
)

if TYPE_CHECKING:
    from behave.runner import Context


# Context to store results between steps
class CollectionParseContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.result = None


# Make sure context has a collection_parse_context
def get_collection_parse_context(context: Context) -> CollectionParseContext:
    if not hasattr(context, 'collection_parse_context'):
        context.collection_parse_context = CollectionParseContext()
    return context.collection_parse_context


@when('I parse "{input_str}" to a list of integers')
def step_parse_to_list_of_integers(context: Context, input_str: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_list(input_str, element_parser=parse_int)


@when('I parse "{input_str}" to a list of integers with separator "{separator}"')
def step_parse_to_list_with_separator(context: Context, input_str: str, separator: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_list(input_str, element_parser=parse_int, separator=separator)


@when('I parse "{input_str}" to a dictionary with string keys and integer values')
def step_parse_to_dict_with_int_values(context: Context, input_str: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_dict(input_str, key_parser=lambda s: Maybe.success(s), value_parser=parse_int)


@when('I parse "{input_str}" to a dictionary with pair separator "{pair_sep}" and key-value separator "{kv_sep}"')
def step_parse_to_dict_with_separators(context: Context, input_str: str, pair_sep: str, kv_sep: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_dict(
        input_str,
        key_parser=lambda s: Maybe.success(s),
        value_parser=parse_int,
        pair_separator=pair_sep,
        key_value_separator=kv_sep
    )


@when('I parse "{input_str}" to a dictionary')
def step_parse_to_dict(context: Context, input_str: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_dict(input_str)


@when('I parse "{input_str}" to a dictionary with integer values')
def step_parse_to_dict_with_int_values_only(context: Context, input_str: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_dict(input_str, value_parser=parse_int)


@when('I parse "{input_str}" to a list with minimum length {min_length:d}')
def step_parse_to_list_with_min_length(context: Context, input_str: str, min_length: int) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_list_with_validation(input_str, element_parser=parse_int, min_length=min_length)


@when('I parse "{input_str}" to a dictionary with required keys "{required_keys}"')
def step_parse_to_dict_with_required_keys(context: Context, input_str: str, required_keys: str) -> None:
    pc = get_collection_parse_context(context)
    pc.result = parse_dict_with_validation(
        input_str,
        key_parser=lambda s: Maybe.success(s),
        value_parser=parse_int,
        required_keys=required_keys.split(',')
    )


@given('I have registered a custom parser for IP addresses')
def step_register_ip_address_parser(context: Context) -> None:
    # Define a custom parser for IP addresses
    def parse_ip_address(input_value: str) -> Maybe[ipaddress.IPv4Address]:
        try:
            return Maybe.success(ipaddress.IPv4Address(input_value))
        except ValueError:
            return Maybe.failure('Invalid IP address')

    # Register the parser
    ParserRegistry.register(ipaddress.IPv4Address, parse_ip_address)


@when('I parse "{input_str}" using the registry with type "{type_name}"')
def step_parse_with_registry(context: Context, input_str: str, type_name: str) -> None:
    pc = get_collection_parse_context(context)

    # Map type names to actual types
    type_map = {
        'int': int,
        'float': float,
        'bool': bool,
        'str': str,
        'list': list,
        'dict': dict,
        'set': set,
        'IPv4Address': ipaddress.IPv4Address,
    }

    if type_name not in type_map:
        pc.result = Maybe.failure(f'Unknown type: {type_name}')
        return

    target_type = type_map[type_name]
    pc.result = ParserRegistry.parse(input_str, target_type)


@given('the parser registry has default parsers registered')
def step_register_default_parsers(context: Context) -> None:
    ParserRegistry.register_defaults()


@then('the result should be a successful Maybe with list value {expected_list}')
def step_result_is_success_with_list_value(context: Context, expected_list: str) -> None:
    pc = get_collection_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'

    # Parse the expected list from string (using json.loads)
    expected = json.loads(expected_list)
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a successful Maybe with dictionary value {expected_dict}')
def step_result_is_success_with_dict_value(context: Context, expected_dict: str) -> None:
    pc = get_collection_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'

    # Parse the expected dict from string (using json.loads)
    expected = json.loads(expected_dict)
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('the result should be a failure Maybe with error containing "{expected_error}"')
def step_result_is_failure_with_error_containing(context: Context, expected_error: str) -> None:
    pc = get_collection_parse_context(context)
    assert pc.result.is_failure(), f'Expected failure but got success: {pc.result}'
    assert expected_error in pc.result.value_or('TEST'), (
        f"Expected error containing '{expected_error}' but got '{pc.result.value_or('TEST')}'"
    )


@then('the result should be a successful Maybe with IP value "{expected}"')
def step_result_is_success_with_ip_value(context: Context, expected: str) -> None:
    pc = get_collection_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'

    value = pc.result.value_or('TEST')
    # Convert value to string for comparison
    str_value = str(value)
    assert str_value == expected, f'Expected {expected} but got {str_value}'


@then('the result should be a successful Maybe with integer value {expected:d}')
def step_result_is_success_with_registry_int_value(context: Context, expected: int) -> None:
    pc = get_collection_parse_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'
