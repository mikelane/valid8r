"""BDD step definitions for web parsers (slug, JSON, base64, JWT).

This module defines step definitions specific to web parsers.
Common steps like 'the result is a Success' are defined in other step files
and are automatically shared across all features.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from tests.bdd.steps import get_custom_context
from valid8r.core.maybe import (
    Failure,
    Success,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# ==========================================
# Given Steps - Set up test data
# ==========================================


@given('I have the slug string "{slug_string}"')
def step_have_slug_string(context: Context, slug_string: str) -> None:
    """Store the slug string for parsing."""
    ctx = get_custom_context(context)
    ctx.slug_input = slug_string


@given('I have the slug string ""')
def step_have_empty_slug_string(context: Context) -> None:
    """Store an empty slug string for parsing."""
    ctx = get_custom_context(context)
    ctx.slug_input = ''


@given('I have the JSON string {json_string}')
def step_have_json_string(context: Context, json_string: str) -> None:
    """Store the JSON string for parsing.

    Note: json_string is NOT quoted in the step definition because Gherkin
    includes the quotes in the captured string (e.g., '{"key": "value"}').
    Handles empty strings when json_string is ''.
    """
    ctx = get_custom_context(context)
    # Handle empty string case
    if json_string == "''":
        ctx.json_input = ''
    else:
        # Remove outer quotes (either single or double) if present
        if (json_string.startswith("'") and json_string.endswith("'")) or (
            json_string.startswith('"') and json_string.endswith('"')
        ):
            json_string = json_string[1:-1]
        ctx.json_input = json_string


@given('I have the base64 string "{b64_string}"')
def step_have_base64_string(context: Context, b64_string: str) -> None:
    r"""Store the base64 string for parsing.

    Decodes escape sequences like \n to actual newlines.
    """
    ctx = get_custom_context(context)
    # Decode escape sequences (e.g., \n -> newline)
    ctx.base64_input = b64_string.encode().decode('unicode_escape')


@given('I have the base64 string ""')
def step_have_empty_base64_string(context: Context) -> None:
    """Store an empty base64 string for parsing."""
    ctx = get_custom_context(context)
    ctx.base64_input = ''


@given('I have the JWT string "{jwt_string}"')
def step_have_jwt_string(context: Context, jwt_string: str) -> None:
    """Store the JWT string for parsing."""
    ctx = get_custom_context(context)
    ctx.jwt_input = jwt_string


@given('I have the JWT string ""')
def step_have_empty_jwt_string(context: Context) -> None:
    """Store an empty JWT string for parsing."""
    ctx = get_custom_context(context)
    ctx.jwt_input = ''


# ==========================================
# When Steps - Execute parsers
# ==========================================


@when('I parse it with parse_slug')
def step_parse_slug(context: Context) -> None:
    """Parse the slug string without constraints."""
    ctx = get_custom_context(context)
    # Import inside step to avoid import errors before implementation
    try:
        from valid8r.core.parsers import parse_slug

        ctx.result = parse_slug(ctx.slug_input)
    except ImportError:
        ctx.result = Failure('parse_slug not implemented yet')


@when('I parse it with parse_slug with min_length {min_len:d}')
def step_parse_slug_with_min_length(context: Context, min_len: int) -> None:
    """Parse the slug string with minimum length constraint."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_slug

        ctx.result = parse_slug(ctx.slug_input, min_length=min_len)
    except ImportError:
        ctx.result = Failure('parse_slug not implemented yet')


@when('I parse it with parse_slug with max_length {max_len:d}')
def step_parse_slug_with_max_length(context: Context, max_len: int) -> None:
    """Parse the slug string with maximum length constraint."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_slug

        ctx.result = parse_slug(ctx.slug_input, max_length=max_len)
    except ImportError:
        ctx.result = Failure('parse_slug not implemented yet')


@when('I parse it with parse_json')
def step_parse_json(context: Context) -> None:
    """Parse the JSON string."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_json

        ctx.result = parse_json(ctx.json_input)
    except ImportError:
        ctx.result = Failure('parse_json not implemented yet')


@when('I parse it with parse_base64')
def step_parse_base64(context: Context) -> None:
    """Parse the base64 string."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_base64

        ctx.result = parse_base64(ctx.base64_input)
    except ImportError:
        ctx.result = Failure('parse_base64 not implemented yet')


@when('I parse it with parse_jwt')
def step_parse_jwt(context: Context) -> None:
    """Parse the JWT string."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_jwt

        ctx.result = parse_jwt(ctx.jwt_input)
    except ImportError:
        ctx.result = Failure('parse_jwt not implemented yet')


# ==========================================
# Then Steps - Verify results
# ==========================================
# Note: Common steps like 'the result is a Success' and 'the result is a Failure'
# are already defined in url_email_parsing_steps.py and shared across all features.
# We only define web-parser-specific assertions here.


@then('the parsed value is "{expected_value}"')
def step_parsed_value_is_string(context: Context, expected_value: str) -> None:
    """Verify the parsed value matches expected string."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == expected_value, f'Expected "{expected_value}" but got "{value}"'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed value is {expected_value:d}')
def step_parsed_value_is_int(context: Context, expected_value: int) -> None:
    """Verify the parsed value matches expected integer."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == expected_value, f'Expected {expected_value} but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed value is True')
def step_parsed_value_is_true(context: Context) -> None:
    """Verify the parsed value is True."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value is True, f'Expected True but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed value is False')
def step_parsed_value_is_false(context: Context) -> None:
    """Verify the parsed value is False."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value is False, f'Expected False but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed value is None')
def step_parsed_value_is_none(context: Context) -> None:
    """Verify the parsed value is None."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value is None, f'Expected None but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed value is the original JWT string')
def step_parsed_value_is_original_jwt(context: Context) -> None:
    """Verify the parsed JWT matches the original input."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert value == ctx.jwt_input.strip(), f'Expected "{ctx.jwt_input.strip()}" but got "{value}"'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed JSON is a dict')
def step_parsed_json_is_dict(context: Context) -> None:
    """Verify the parsed JSON is a dictionary."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, dict), f'Expected dict but got {type(value).__name__}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the parsed JSON is a list')
def step_parsed_json_is_list(context: Context) -> None:
    """Verify the parsed JSON is a list."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, list), f'Expected list but got {type(value).__name__}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the decoded bytes represent "{expected_text}"')
def step_decoded_bytes_represent(context: Context, expected_text: str) -> None:
    """Verify the decoded base64 bytes represent expected text."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, bytes), f'Expected bytes but got {type(value).__name__}'
            decoded_text = value.decode('utf-8')
            assert decoded_text == expected_text, f'Expected "{expected_text}" but got "{decoded_text}"'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


# Note: 'the error message contains' step is already defined in url_email_parsing_steps.py
