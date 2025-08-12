from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from valid8r.core.parsers import parse_int
from valid8r.core.validators import minimum
from valid8r.prompt.basic import ask

if TYPE_CHECKING:
    from behave.runner import Context

    from valid8r.core.maybe import Maybe


# Context to store results between steps
class PromptContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.result = None
        self.prompt_message = None
        self.input_values = None


# Make sure context has a prompt_context
def get_prompt_context(context: Context) -> PromptContext:
    if not hasattr(context, 'prompt_context'):
        context.prompt_context = PromptContext()
    return context.prompt_context


@given('the prompt module is available')
def step_prompt_module_available(context: Context) -> None:  # noqa: ARG001
    # Check that the prompt module is imported correctly
    assert ask is not None


@when('basic prompt "{message}" receives "{input_value}"')
def step_prompt_basic(context: Context, message: str, input_value: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message)


@when('int parser prompt "{message}" receives "{input_value}"')
def step_prompt_with_parser(context: Context, message: str, input_value: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, parser=parse_int)


@when('prompt "{message}" with minimum {min_val:d} validation receives "{input_value}"')
def step_prompt_with_parser_and_validator(context: Context, message: str, min_val: int, input_value: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, parser=parse_int, validator=minimum(min_val))


@when('prompt "{message}" with default {default:d} receives ""')
def step_prompt_with_empty_input(context: Context, message: str, default: int) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = ['']

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, default=default)


@when('prompt "{message}" with default {default:d} receives "{input_value}"')
def step_prompt_with_default(context: Context, message: str, default: int, input_value: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, default=default)


@when('retry prompt "{message}" receives inputs "{input1}" then "{input2}"')
def step_prompt_with_retry(context: Context, message: str, input1: str, input2: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input1, input2]

    with (
        patch('builtins.input', side_effect=pc.input_values),
        patch('builtins.print'),
    ):  # Suppress error messages during test
        pc.result = ask(pc.prompt_message, parser=parse_int, retry=True)


@when('custom error prompt "{message}" with message "{error_msg}" receives "{input_value}"')
def step_prompt_with_custom_error(context: Context, message: str, error_msg: str, input_value: str) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    # Create a parser with the custom error message
    def custom_parser(s: str) -> Maybe[int]:
        return parse_int(s, error_message=error_msg)

    with patch('builtins.input', side_effect=pc.input_values):
        # Pass the custom parser instead of the generic one
        pc.result = ask(
            pc.prompt_message,
            parser=custom_parser,
            retry=False,  # Don't retry automatically
        )


@when('limited retry prompt "{message}" with {retries:d} attempts receives "{input1}", "{input2}", "{input3}"')
def step_prompt_with_limited_retries(
    context: Context, message: str, retries: int, input1: str, input2: str, input3: str
) -> None:
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input1, input2, input3]

    with (
        patch('builtins.input', side_effect=pc.input_values),
        patch('builtins.print'),
    ):  # Suppress error messages during test
        pc.result = ask(pc.prompt_message, parser=parse_int, retry=retries)


@then('prompt result is successful with value {expected:d}')
def step_prompt_result_is_success_with_int_value(context: Context, expected: int) -> None:
    pc = get_prompt_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('prompt result is successful with value "{expected}"')
def step_prompt_result_is_success_with_string_value(context: Context, expected: str) -> None:
    pc = get_prompt_context(context)
    assert pc.result.is_success(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value_or('TEST') == expected, f'Expected {expected} but got {pc.result.value_or("TEST")}'


@then('prompt result is failure with error "{expected_error}"')
def step_prompt_result_is_failure_with_error(context: Context, expected_error: str) -> None:
    pc = get_prompt_context(context)
    assert pc.result.is_failure(), f'Expected failure but got success: {pc.result}'
    assert pc.result.error_or('TEST') == expected_error, (
        f"Expected error '{expected_error}' but got '{pc.result.value_or('TEST')}'"
    )


@then('prompt result is failure')
def step_prompt_result_is_failure(context: Context) -> None:
    pc = get_prompt_context(context)
    assert pc.result.is_failure(), f'Expected failure but got success: {pc.result}'
