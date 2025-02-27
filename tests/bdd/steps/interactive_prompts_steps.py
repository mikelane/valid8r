from __future__ import annotations

from unittest.mock import patch

from behave import (
    given,
    then,
    when,
)
from valid8r.core.parsers import parse_int
from valid8r.core.validators import minimum
from valid8r.prompt.basic import ask


# Context to store results between steps
class PromptContext:
    def __init__(self) -> None:
        self.result = None
        self.prompt_message = None
        self.input_values = None


# Make sure context has a prompt_context
def get_prompt_context(context):
    if not hasattr(context, 'prompt_context'):
        context.prompt_context = PromptContext()
    return context.prompt_context


@given('the prompt module is available')
def step_prompt_module_available(context):
    # Check that the prompt module is imported correctly
    assert ask is not None


@when('basic prompt "{message}" receives "{input_value}"')
def step_prompt_basic(context, message, input_value):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message)


@when('int parser prompt "{message}" receives "{input_value}"')
def step_prompt_with_parser(context, message, input_value):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, parser=parse_int)


@when('prompt "{message}" with minimum {min_val:d} validation receives "{input_value}"')
def step_prompt_with_parser_and_validator(context, message, min_val, input_value):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, parser=parse_int, validator=minimum(min_val))


@when('prompt "{message}" with default {default:d} receives ""')
def step_prompt_with_empty_input(context, message, default):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = ['']

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, default=default)


@when('prompt "{message}" with default {default:d} receives "{input_value}"')
def step_prompt_with_default(context, message, default, input_value):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    with patch('builtins.input', side_effect=pc.input_values):
        pc.result = ask(pc.prompt_message, default=default)


@when('retry prompt "{message}" receives inputs "{input1}" then "{input2}"')
def step_prompt_with_retry(context, message, input1, input2):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input1, input2]

    with patch('builtins.input', side_effect=pc.input_values):
        with patch('builtins.print'):  # Suppress error messages during test
            pc.result = ask(pc.prompt_message, parser=parse_int, retry=True)


@when('custom error prompt "{message}" with message "{error_msg}" receives "{input_value}"')
def step_prompt_with_custom_error(context, message, error_msg, input_value):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input_value]

    # Create a parser with the custom error message
    custom_parser = lambda s: parse_int(s, error_message=error_msg)

    with patch('builtins.input', side_effect=pc.input_values):
        # Pass the custom parser instead of the generic one
        pc.result = ask(
            pc.prompt_message,
            parser=custom_parser,
            retry=False,  # Don't retry automatically
        )


@when('limited retry prompt "{message}" with {retries:d} attempts receives "{input1}", "{input2}", "{input3}"')
def step_prompt_with_limited_retries(context, message, retries, input1, input2, input3):
    pc = get_prompt_context(context)
    pc.prompt_message = message
    pc.input_values = [input1, input2, input3]

    with patch('builtins.input', side_effect=pc.input_values):
        with patch('builtins.print'):  # Suppress error messages during test
            pc.result = ask(pc.prompt_message, parser=parse_int, retry=retries)


@then('prompt result is successful with value {expected:d}')
def step_prompt_result_is_success_with_int_value(context, expected):
    pc = get_prompt_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('prompt result is successful with value "{expected}"')
def step_prompt_result_is_success_with_string_value(context, expected):
    pc = get_prompt_context(context)
    assert pc.result.is_just(), f'Expected success but got failure: {pc.result}'
    assert pc.result.value() == expected, f'Expected {expected} but got {pc.result.value()}'


@then('prompt result is failure with error "{expected_error}"')
def step_prompt_result_is_failure_with_error(context, expected_error):
    pc = get_prompt_context(context)
    assert pc.result.is_nothing(), f'Expected failure but got success: {pc.result}'
    assert pc.result.error() == expected_error, f"Expected error '{expected_error}' but got '{pc.result.error()}'"


@then('prompt result is failure')
def step_prompt_result_is_failure(context):
    pc = get_prompt_context(context)
    assert pc.result.is_nothing(), f'Expected failure but got success: {pc.result}'
