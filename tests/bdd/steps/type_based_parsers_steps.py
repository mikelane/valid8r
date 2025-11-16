from __future__ import annotations

import json
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    Optional,
    Union,
)

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

# Import from_type when it exists
try:
    from valid8r.core.type_adapters import from_type
except ImportError:
    # Stub for RED phase - will fail tests as expected
    def from_type(annotation: type[Any]) -> Any:  # type: ignore[misc]
        msg = 'from_type not implemented yet'
        raise NotImplementedError(msg)


if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# Background step


@given('the type adapter module is available')
def step_type_adapter_available(context: Context) -> None:  # noqa: ARG001
    """Verify the type adapter module is available."""
    assert Maybe is not None


# Given steps - Set up type annotations


@given('the type annotation {type_name}')
def step_set_type_annotation(context: Context, type_name: str) -> None:
    """Set a type annotation from a string representation."""
    # Map string representations to actual types
    type_map: dict[str, type[Any]] = {
        'int': int,
        'str': str,
        'float': float,
        'bool': bool,
    }

    # Handle special typing constructs
    if type_name.startswith('Optional['):
        inner_type = type_name[9:-1]  # Extract "int" from "Optional[int]"
        context.type_annotation = Optional[type_map.get(inner_type, str)]  # type: ignore[misc]
    elif type_name.startswith('list['):
        inner_type = type_name[5:-1]  # Extract "int" from "list[int]"
        context.type_annotation = list[type_map.get(inner_type, str)]  # type: ignore[misc]
    elif type_name.startswith('set['):
        inner_type = type_name[4:-1]  # Extract "str" from "set[str]"
        context.type_annotation = set[type_map.get(inner_type, str)]  # type: ignore[misc]
    elif type_name.startswith('dict['):
        # Extract "str, int" from "dict[str, int]"
        parts = type_name[5:-1].split(', ')
        key_type = type_map.get(parts[0], str)
        value_type = type_map.get(parts[1], str)
        context.type_annotation = dict[key_type, value_type]  # type: ignore[misc]
    elif type_name.startswith('list[list['):
        # Nested list
        inner_type = type_name[10:-2]  # Extract "int" from "list[list[int]]"
        context.type_annotation = list[list[type_map.get(inner_type, int)]]  # type: ignore[misc]
    elif type_name.startswith('list[dict['):
        # list[dict[str, int]]
        dict_spec = type_name[10:-2]  # Extract "str, int" from "list[dict[str, int]]"
        parts = dict_spec.split(', ')
        key_type = type_map.get(parts[0], str)
        value_type = type_map.get(parts[1], str)
        context.type_annotation = list[dict[key_type, value_type]]  # type: ignore[misc]
    elif type_name.startswith('dict[str, list['):
        # dict[str, list[int]]
        inner_type = type_name[15:-2]  # Extract "int" from "dict[str, list[int]]"
        context.type_annotation = dict[str, list[type_map.get(inner_type, int)]]  # type: ignore[misc]
    elif type_name.startswith('Union['):
        # Union[int, str]
        parts = type_name[6:-1].split(', ')
        types = [type_map.get(p, str) for p in parts]
        context.type_annotation = Union[tuple(types)]  # type: ignore[misc, arg-type]
    elif type_name.startswith("Literal['"):
        # Literal['red', 'green', 'blue']
        literal_values = type_name[9:-2].split("', '")
        context.type_annotation = Literal[tuple(literal_values)]  # type: ignore[misc, valid-type]
    elif type_name.startswith('Literal['):
        # Literal[1, 'one', True]
        # This is complex - store raw string for later processing
        context.type_annotation = type_name
    elif type_name.startswith('Annotated['):
        # For now, extract the base type and store full string
        context.type_annotation = type_name
    elif type_name == 'typing.Callable':
        import typing

        context.type_annotation = typing.Callable
    elif type_name == 'Color' or type_name == 'Status':
        # Enum types - will be set separately
        context.type_annotation = type_name
    else:
        context.type_annotation = type_map.get(type_name, type_name)


@given('an enum {enum_name} with members {members}')
def step_create_enum(context: Context, enum_name: str, members: str) -> None:
    """Create an enum with specified members."""
    member_list = [m.strip() for m in members.split(',')]
    context.test_enum = Enum(enum_name, {m: m for m in member_list})  # type: ignore[misc]
    # Store for later use when type annotation is set to this enum
    if not hasattr(context, 'enums'):
        context.enums = {}
    context.enums[enum_name] = context.test_enum


@given('a None type annotation')
def step_none_type_annotation(context: Context) -> None:
    """Set a None type annotation."""
    context.type_annotation = None


# When steps - Generate parser and process input


@when('a parser is generated from the type')
def step_generate_parser(context: Context) -> None:
    """Generate a parser from the stored type annotation."""
    # If type annotation is an enum name, get the actual enum
    if isinstance(context.type_annotation, str) and hasattr(context, 'enums'):
        type_ann = context.enums.get(context.type_annotation, context.type_annotation)
    else:
        type_ann = context.type_annotation

    # Handle Annotated types specially
    if isinstance(type_ann, str) and type_ann.startswith('Annotated['):
        # For testing purposes, we'll need to construct the actual Annotated type
        # This is a simplification - real implementation will handle this properly
        if 'validators.minimum' in type_ann:
            from valid8r.core import validators

            if 'validators.maximum' in type_ann:
                # Both minimum and maximum
                context.generated_parser = from_type(Annotated[int, validators.minimum(0), validators.maximum(100)])
            else:
                # Just minimum
                context.generated_parser = from_type(Annotated[int, validators.minimum(0)])
        else:
            # Just a description, no validator
            context.generated_parser = from_type(Annotated[int, 'must be positive'])
    else:
        context.generated_parser = from_type(type_ann)


@when('a parser generation is attempted from the type')
def step_attempt_generate_parser(context: Context) -> None:
    """Attempt to generate a parser, capturing any errors."""
    try:
        if isinstance(context.type_annotation, str) and hasattr(context, 'enums'):
            type_ann = context.enums.get(context.type_annotation, context.type_annotation)
        else:
            type_ann = context.type_annotation

        context.generated_parser = from_type(type_ann)
        context.generation_error = None
    except (ValueError, TypeError, NotImplementedError) as e:
        context.generation_error = str(e)
        context.generated_parser = None


@when('the generated parser processes "{input_text}"')
def step_parse_input(context: Context, input_text: str) -> None:
    """Apply the generated parser to an input string."""
    context.parse_result = context.generated_parser(input_text)


@when('the generated parser processes an empty string')
def step_parse_empty(context: Context) -> None:
    """Apply the generated parser to an empty string."""
    context.parse_result = context.generated_parser('')


# Then steps - Verify results


@then('the result is a successful Maybe with value {expected}')
def step_verify_success_value(context: Context, expected: str) -> None:
    """Verify the parse result is a Success with expected value."""
    assert isinstance(context.parse_result, Success), f'Expected Success, got {type(context.parse_result).__name__}'

    # Convert expected string to appropriate type
    if expected == 'True':
        expected_value = True
    elif expected == 'False':
        expected_value = False
    elif expected.isdigit() or (expected.startswith('-') and expected[1:].isdigit()):
        expected_value = int(expected)
    elif expected.replace('.', '', 1).isdigit():
        expected_value = float(expected)
    else:
        expected_value = expected

    assert context.parse_result.value_or(None) == expected_value


@then('the result is a successful Maybe with None value')
def step_verify_success_none(context: Context) -> None:
    """Verify the parse result is a Success with None value."""
    assert isinstance(context.parse_result, Success)
    assert context.parse_result.value_or('NOT_NONE') is None


@then('the result is a successful Maybe with list {values}')
def step_verify_success_list(context: Context, values: str) -> None:
    """Verify the parse result is a Success with expected list."""
    assert isinstance(context.parse_result, Success)
    expected_list = json.loads(values)
    assert context.parse_result.value_or(None) == expected_list


@then('the result is a successful Maybe with set containing {values}')
def step_verify_success_set(context: Context, values: str) -> None:
    """Verify the parse result is a Success with expected set."""
    assert isinstance(context.parse_result, Success)
    expected_values = {v.strip() for v in values.split(',')}
    assert context.parse_result.value_or(None) == expected_values


@then('the result is a successful Maybe with dict containing {key_values}')
def step_verify_success_dict(context: Context, key_values: str) -> None:
    """Verify the parse result is a Success with expected dict entries."""
    assert isinstance(context.parse_result, Success)
    result_dict = context.parse_result.value_or({})
    # Parse "age=30 and count=5"
    pairs = key_values.replace(' and ', ',').split(',')
    for pair in pairs:
        key, value = pair.split('=')
        assert key.strip() in result_dict
        assert result_dict[key.strip()] == int(value.strip())


@then('the result is a successful Maybe with nested list {values}')
def step_verify_success_nested_list(context: Context, values: str) -> None:
    """Verify the parse result is a Success with expected nested list."""
    assert isinstance(context.parse_result, Success)
    expected_list = json.loads(values)
    assert context.parse_result.value_or(None) == expected_list


@then('the result is a successful Maybe with list of dictionaries')
def step_verify_success_list_of_dicts(context: Context) -> None:
    """Verify the parse result is a Success with a list of dictionaries."""
    assert isinstance(context.parse_result, Success)
    result = context.parse_result.value_or(None)
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


@then('the result is a successful Maybe with nested structure')
def step_verify_success_nested(context: Context) -> None:
    """Verify the parse result is a Success with nested structure."""
    assert isinstance(context.parse_result, Success)
    result = context.parse_result.value_or(None)
    assert isinstance(result, dict)


@then('the result is a successful Maybe with value {value}')
def step_verify_success_generic(context: Context, value: str) -> None:
    """Verify the parse result is a Success with expected value (generic)."""
    assert isinstance(context.parse_result, Success)
    # Handle different value types
    if value.isdigit():
        expected = int(value) if '.' not in value else float(value)
    else:
        expected = value
    assert context.parse_result.value_or(None) == expected


@then('the result is a successful Maybe with enum member {member}')
def step_verify_success_enum(context: Context, member: str) -> None:
    """Verify the parse result is a Success with expected enum member."""
    assert isinstance(context.parse_result, Success)
    # Parse "Color.RED" to get enum and member name
    enum_name, member_name = member.split('.')
    expected_enum = context.enums[enum_name]
    assert context.parse_result.value_or(None) == expected_enum[member_name]


@then('the result is a failed Maybe')
def step_verify_failure(context: Context) -> None:
    """Verify the parse result is a Failure."""
    assert isinstance(context.parse_result, Failure), f'Expected Failure, got {type(context.parse_result).__name__}'


@then('the error contains "{error_fragment}"')
def step_verify_error_contains(context: Context, error_fragment: str) -> None:
    """Verify the error message contains expected fragment."""
    assert isinstance(context.parse_result, Failure)
    error_message = context.parse_result.error_or('')
    assert error_fragment.lower() in error_message.lower(), f'Expected "{error_fragment}" in "{error_message}"'


@then('the generation fails with error "{error_message}"')
def step_verify_generation_error(context: Context, error_message: str) -> None:
    """Verify parser generation failed with expected error."""
    assert context.generation_error is not None, 'Expected generation to fail, but it succeeded'
    assert error_message.lower() in context.generation_error.lower(), (
        f'Expected "{error_message}" in "{context.generation_error}"'
    )


@then('the result value has Python type {type_name}')
def step_verify_python_type(context: Context, type_name: str) -> None:
    """Verify the result value has expected Python type."""
    assert isinstance(context.parse_result, Success)
    value = context.parse_result.value_or(None)
    type_map = {
        'int': int,
        'str': str,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'set': set,
    }
    expected_type = type_map.get(type_name, str)
    assert isinstance(value, expected_type), f'Expected {expected_type}, got {type(value)}'


@then('the result value is Python None')
def step_verify_python_none(context: Context) -> None:
    """Verify the result value is Python None."""
    assert isinstance(context.parse_result, Success)
    assert context.parse_result.value_or('NOT_NONE') is None
