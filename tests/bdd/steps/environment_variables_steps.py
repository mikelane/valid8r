from __future__ import annotations

import json
from typing import TYPE_CHECKING

import parse  # type: ignore[import-untyped]
from behave import (  # type: ignore[import-untyped]
    given,
    register_type,
    then,
    when,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.parsers import (
    parse_bool,
    parse_int,
    parse_list,
)
from valid8r.core.validators import minimum

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# Register custom type for dictionary strings (must start with '{')
@parse.with_pattern(r'\{.+\}')
def parse_dict_string(text: str) -> str:
    """Parse a dictionary string that starts and ends with braces."""
    return text


register_type(DictString=parse_dict_string)


def parse_str(text: str | None) -> Maybe[str]:
    """Parse a string value."""
    if text is None or not isinstance(text, str):
        return Maybe.failure('Value must be a string')
    return Maybe.success(text)


@given('the valid8r.integrations.env module exists')
def step_env_module_exists(context: Context) -> None:  # noqa: ARG001
    """Verify that the env integration module can be imported."""
    try:
        from valid8r.integrations import env  # noqa: F401
    except ImportError:
        msg = 'valid8r.integrations.env module does not exist'
        raise ImportError(msg) from None


@given('I have imported load_env_config')
def step_import_load_env_config(context: Context) -> None:
    """Import load_env_config function."""
    from valid8r.integrations.env import load_env_config

    context.load_env_config = load_env_config


@given('environment variables:')
def step_given_environment_variables(context: Context) -> None:
    """Set up environment variables from a table."""
    if not hasattr(context, 'test_environ'):
        context.test_environ = {}

    for row in context.table:
        context.test_environ[row['name']] = row['value']


@given('a schema:')
def step_given_schema(context: Context) -> None:
    """Create a schema from a table."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    fields = {}
    for row in context.table:
        field_name = row['field']
        parser_name = row['parser']

        # Map parser names to actual parser functions
        parser = {
            'parse_int': parse_int,
            'parse_bool': parse_bool,
            'parse_str': parse_str,
        }[parser_name]

        fields[field_name] = EnvField(parser=parser)

    context.schema = EnvSchema(fields=fields)


@given('environment variable {var_name} is not set')
def step_env_var_not_set(context: Context, var_name: str) -> None:
    """Ensure an environment variable is not set."""
    if not hasattr(context, 'test_environ'):
        context.test_environ = {}

    # Remove the variable if it exists
    context.test_environ.pop(var_name, None)


@given('a schema with field "{field_name}" using {parser_name} and default {default_value}')
def step_schema_with_default(context: Context, field_name: str, parser_name: str, default_value: str) -> None:
    """Create a schema with a field that has a default value."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    # Map parser names to actual parser functions
    parser = {'parse_int': parse_int, 'parse_bool': parse_bool}[parser_name]

    # Parse the default value
    if parser_name == 'parse_int':
        default = int(default_value)
    elif parser_name == 'parse_bool':
        default = default_value.lower() in ('true', '1', 'yes')
    else:
        default = default_value

    context.schema = EnvSchema(fields={field_name: EnvField(parser=parser, default=default)})


@given('environment variable {var_name}="{value}"')
def step_env_var_equals(context: Context, var_name: str, value: str) -> None:
    """Set a specific environment variable."""
    if not hasattr(context, 'test_environ'):
        context.test_environ = {}

    context.test_environ[var_name] = value


@given('a schema with field "{field_name}" using {parser_name}')
def step_schema_with_field(context: Context, field_name: str, parser_name: str) -> None:
    """Create a schema with a single field."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    # Map parser names to actual parser functions
    parser = {'parse_int': parse_int, 'parse_bool': parse_bool}[parser_name]

    context.schema = EnvSchema(fields={field_name: EnvField(parser=parser)})


@given('a nested schema for "{parent_field}" with host, port, name')
def step_nested_schema(context: Context, parent_field: str) -> None:
    """Create a nested schema for database configuration."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    context.schema = EnvSchema(
        fields={
            parent_field: EnvField(
                parser=None,  # Nested schema will be handled differently
                nested=EnvSchema(
                    fields={
                        'host': EnvField(parser=parse_str),
                        'port': EnvField(parser=parse_int),
                        'name': EnvField(parser=parse_str),
                    }
                ),
            )
        }
    )


@given('a schema with "{field_name}" using {parser_name} & minimum({min_value})')
def step_schema_with_chained_validators(context: Context, field_name: str, parser_name: str, min_value: str) -> None:
    """Create a schema with chained validators."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    # Map parser names to actual parser functions
    parser = {'parse_int': parse_int}[parser_name]

    # Create chained validator
    min_val = int(min_value)
    validator = minimum(min_val)

    def chained_parser(text: str | None) -> Maybe:
        return parser(text).bind(validator)

    context.schema = EnvSchema(fields={field_name: EnvField(parser=chained_parser)})


@given('a schema with required field "{required_field}" and optional field "{optional_field}"')
def step_schema_required_optional(context: Context, required_field: str, optional_field: str) -> None:
    """Create a schema with both required and optional fields."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    context.schema = EnvSchema(
        fields={
            required_field: EnvField(parser=parse_str, required=True),
            optional_field: EnvField(parser=parse_str, required=False, default='INFO'),
        }
    )


@given('a schema with "{field_name}" using parse_list(parse_str)')
def step_schema_with_list_parser(context: Context, field_name: str) -> None:
    """Create a schema with a list parser."""
    from valid8r.integrations.env import (
        EnvField,
        EnvSchema,
    )

    # Create a list parser using parse_list
    def list_parser(text: str | None) -> Maybe:
        return parse_list(text, element_parser=parse_str, separator=',')

    context.schema = EnvSchema(fields={field_name: EnvField(parser=list_parser)})


@when('I call load_env_config(schema, prefix="{prefix}")')
def step_call_load_env_config_basic(context: Context, prefix: str) -> None:
    """Call load_env_config with basic parameters."""
    context.result = context.load_env_config(
        schema=context.schema, prefix=prefix, environ=getattr(context, 'test_environ', {})
    )


@when('I call load_env_config with prefix "{prefix}" and delimiter "{delimiter}"')
def step_call_load_env_config_delimiter(context: Context, prefix: str, delimiter: str) -> None:
    """Call load_env_config with prefix and delimiter."""
    context.result = context.load_env_config(
        schema=context.schema, prefix=prefix, delimiter=delimiter, environ=getattr(context, 'test_environ', {})
    )


@then('I get Success with {expected_dict:DictString}')
def step_assert_success_with_dict(context: Context, expected_dict: str) -> None:
    """Assert that the result is a Success with the expected dictionary.

    Uses custom DictString type that only matches strings starting with '{',
    preventing ambiguity with other 'I get Success with X' steps.
    """
    import ast

    # Check if we have multiline text (JSON) - used for nested dicts
    expected = json.loads(context.text) if context.text else ast.literal_eval(expected_dict)

    assert isinstance(context.result, Success), f'Expected Success but got {type(context.result).__name__}'
    assert context.result.value == expected, f'Expected {expected} but got {context.result.value}'


@then('I get Success with {{}}:')
def step_assert_success_with_json_block(context: Context) -> None:
    """Assert that the result is a Success with JSON from a docstring block.

    This step matches the literal text 'I get Success with {}:' where the '{}:'
    indicates that a multiline JSON document follows in context.text.
    The double braces {{}} are used to escape the literal curly braces.
    """
    assert context.text, 'Expected multiline JSON block but none was provided'
    expected = json.loads(context.text)

    assert isinstance(context.result, Success), f'Expected Success but got {type(context.result).__name__}'
    assert context.result.value == expected, f'Expected {expected} but got {context.result.value}'


@then('I get Failure mentioning "{error_substring1}" and "{error_substring2}"')
def step_assert_failure_mentioning_two(context: Context, error_substring1: str, error_substring2: str) -> None:
    """Assert that the result is a Failure containing two specific substrings."""
    assert isinstance(context.result, Failure), f'Expected Failure but got {type(context.result).__name__}'
    error_msg = context.result.error.lower()
    assert error_substring1.lower() in error_msg, f'Expected "{error_substring1}" in error: {context.result.error}'
    assert error_substring2.lower() in error_msg, f'Expected "{error_substring2}" in error: {context.result.error}'


@then('I get Failure mentioning "{error_substring}"')
def step_assert_failure_mentioning_one(context: Context, error_substring: str) -> None:
    """Assert that the result is a Failure containing a specific substring."""
    assert isinstance(context.result, Failure), f'Expected Failure but got {type(context.result).__name__}'
    error_msg = context.result.error.lower()
    assert error_substring.lower() in error_msg, f'Expected "{error_substring}" in error: {context.result.error}'
