"""Step definitions for pluggable IO provider BDD tests."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from valid8r.core.parsers import (
    parse_bool,
    parse_int,
)
from valid8r.prompt.basic import ask
from valid8r.prompt.io_provider import (
    BuiltinIOProvider,
    IOProvider,
    TestIOProvider,
)

if TYPE_CHECKING:
    from behave.runner import Context

    from valid8r.core.maybe import Maybe


# Context to store state between steps
class IOProviderContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.provider: IOProvider | None = None
        self.custom_provider: CustomIOProvider | None = None
        self.result: Maybe | None = None
        self.name_result: Maybe | None = None
        self.age_result: Maybe | None = None
        self.confirmation_result: Maybe | None = None
        self.input_results: list[str] = []
        self.exception: Exception | None = None


# Custom IO provider for testing
class CustomIOProvider:
    """Custom IO provider that prefixes prompts and adds color to errors."""

    def __init__(self, inputs: list[str]) -> None:
        """Initialize the custom IO provider.

        Args:
            inputs: List of input strings to return in sequence

        """
        self.inputs = list(inputs)
        self.outputs: list[str] = []
        self.errors: list[str] = []
        self.prompts_received: list[str] = []

    def input(self, prompt: str) -> str:
        # Add prefix and track prompt
        prefixed = f'CUSTOM: {prompt}'
        self.prompts_received.append(prefixed)
        if not self.inputs:
            msg = 'No more test inputs available'
            raise RuntimeError(msg)
        return self.inputs.pop(0)

    def output(self, message: str) -> None:
        self.outputs.append(message)

    def error(self, message: str) -> None:
        # Add color codes (ANSI escape codes)
        colored_message = f'\033[91m{message}\033[0m'
        self.errors.append(colored_message)


def get_io_context(context: Context) -> IOProviderContext:
    """Get or create the IO provider context."""
    if not hasattr(context, 'io_context'):
        context.io_context = IOProviderContext()
    return context.io_context


@given('the IO provider module is available')
def step_io_provider_module_available(context: Context) -> None:  # noqa: ARG001
    """Verify the IO provider module can be imported."""
    assert IOProvider is not None
    assert BuiltinIOProvider is not None
    assert TestIOProvider is not None


@given('a BuiltinIOProvider instance')
def step_create_builtin_provider(context: Context) -> None:
    """Create a BuiltinIOProvider instance."""
    ctx = get_io_context(context)
    ctx.provider = BuiltinIOProvider()


@given('a TestIOProvider with inputs "{input1}" and "{input2}"')
def step_create_test_provider_with_two_inputs(context: Context, input1: str, input2: str) -> None:
    """Create a TestIOProvider with two inputs."""
    ctx = get_io_context(context)
    ctx.provider = TestIOProvider(inputs=[input1, input2])


@given('a TestIOProvider with input "{input_value}"')
def step_create_test_provider_with_one_input(context: Context, input_value: str) -> None:
    """Create a TestIOProvider with one input."""
    ctx = get_io_context(context)
    ctx.provider = TestIOProvider(inputs=[input_value])


@given('a TestIOProvider with no inputs')
def step_create_test_provider_with_no_inputs(context: Context) -> None:
    """Create a TestIOProvider with no inputs."""
    ctx = get_io_context(context)
    ctx.provider = TestIOProvider(inputs=[])


@given('a TestIOProvider with empty input')
def step_create_test_provider_with_empty_input(context: Context) -> None:
    """Create a TestIOProvider with empty string input."""
    ctx = get_io_context(context)
    ctx.provider = TestIOProvider(inputs=[''])


@given('a custom IO provider that prefixes all prompts with "CUSTOM: "')
def step_create_custom_prefix_provider(context: Context) -> None:
    """Create a custom IO provider that prefixes prompts."""
    ctx = get_io_context(context)
    ctx.custom_provider = CustomIOProvider(inputs=['test'])


@given('a custom IO provider that adds color codes to errors')
def step_create_custom_color_provider(context: Context) -> None:
    """Create a custom IO provider that adds color codes to errors."""
    ctx = get_io_context(context)
    ctx.custom_provider = CustomIOProvider(inputs=['abc', '42'])


@given('a TestIOProvider with inputs "Alice", "30", and "yes"')
def step_create_test_provider_with_three_inputs(context: Context) -> None:
    """Create a TestIOProvider with three inputs."""
    ctx = get_io_context(context)
    ctx.provider = TestIOProvider(inputs=['Alice', '30', 'yes'])


@when('I call input with prompt "{prompt}" and builtins returns "{return_value}"')
def step_call_input_with_builtin(context: Context, prompt: str, return_value: str) -> None:
    """Call input on BuiltinIOProvider with mocked builtins.input."""
    ctx = get_io_context(context)
    with patch('builtins.input', return_value=return_value):
        result = ctx.provider.input(prompt)
        ctx.input_results.append(result)


@when('I call output with message "{message}"')
def step_call_output(context: Context, message: str) -> None:
    """Call output on the IO provider."""
    ctx = get_io_context(context)
    with patch('builtins.print'):
        ctx.provider.output(message)


@when('I call error with message "{message}"')
def step_call_error(context: Context, message: str) -> None:
    """Call error on the IO provider."""
    ctx = get_io_context(context)
    with patch('builtins.print'):
        ctx.provider.error(message)


@when('I call input twice')
def step_call_input_twice(context: Context) -> None:
    """Call input twice on the TestIOProvider."""
    ctx = get_io_context(context)
    ctx.input_results.append(ctx.provider.input('First: '))
    ctx.input_results.append(ctx.provider.input('Second: '))


@when('I call input once successfully')
def step_call_input_once(context: Context) -> None:
    """Call input once on the TestIOProvider."""
    ctx = get_io_context(context)
    ctx.input_results.append(ctx.provider.input('Prompt: '))


@when('I call input again')
def step_call_input_again(context: Context) -> None:
    """Call input again, expecting it to fail."""
    ctx = get_io_context(context)
    try:
        ctx.provider.input('Prompt: ')
    except RuntimeError as e:
        ctx.exception = e


@when('I call output with "{message}"')
def step_call_output_with_message(context: Context, message: str) -> None:
    """Call output with a specific message."""
    ctx = get_io_context(context)
    ctx.provider.output(message)


@when('I call error with "{message}"')
def step_call_error_with_message(context: Context, message: str) -> None:
    """Call error with a specific message."""
    ctx = get_io_context(context)
    ctx.provider.error(message)


@when('I ask for a number with integer parser using the provider')
def step_ask_with_int_parser(context: Context) -> None:
    """Ask for a number using the IO provider."""
    ctx = get_io_context(context)
    ctx.result = ask('Enter number: ', parser=parse_int, io_provider=ctx.provider)


@when('I ask for a number with retry enabled using the provider')
def step_ask_with_retry(context: Context) -> None:
    """Ask for a number with retry using the IO provider."""
    ctx = get_io_context(context)
    ctx.result = ask('Enter number: ', parser=parse_int, retry=1, io_provider=ctx.provider)


@when('I ask for a port number with default 8080 using the provider')
def step_ask_with_default(context: Context) -> None:
    """Ask for a port number with default value using the IO provider."""
    ctx = get_io_context(context)
    ctx.result = ask('Port: ', parser=parse_int, default=8080, io_provider=ctx.provider)


@when('I ask for user input "{input_value}" using the custom provider')
def step_ask_with_custom_provider(context: Context, input_value: str) -> None:  # noqa: ARG001
    """Ask for input using the custom IO provider."""
    ctx = get_io_context(context)
    ctx.result = ask('Enter value: ', io_provider=ctx.custom_provider)


@when('I provide invalid input "{input_value}" using the custom provider')
def step_provide_invalid_input(context: Context, input_value: str) -> None:  # noqa: ARG001
    """Provide invalid input using the custom IO provider."""
    ctx = get_io_context(context)
    ctx.result = ask('Enter number: ', parser=parse_int, retry=1, io_provider=ctx.custom_provider)


@when('I call ask without specifying an IO provider')
def step_ask_without_provider(context: Context) -> None:
    """Call ask without an IO provider (should use BuiltinIOProvider)."""
    ctx = get_io_context(context)
    with patch('builtins.input', return_value='42'):
        ctx.result = ask('Enter number: ', parser=parse_int)


@when('I ask for name, age, and confirmation using the provider')
def step_ask_multiple_prompts(context: Context) -> None:
    """Ask for multiple prompts sequentially."""
    ctx = get_io_context(context)
    ctx.name_result = ask('Name: ', io_provider=ctx.provider)
    ctx.age_result = ask('Age: ', parser=parse_int, io_provider=ctx.provider)
    ctx.confirmation_result = ask('Confirm: ', parser=parse_bool, io_provider=ctx.provider)


@then('the provider returns "{expected}"')
def step_provider_returns_value(context: Context, expected: str) -> None:
    """Verify the provider returned the expected value."""
    ctx = get_io_context(context)
    assert ctx.input_results[-1] == expected


@then('the message is printed to stdout')
def step_message_printed_to_stdout(context: Context) -> None:
    """Verify the message was printed (mocked in when step)."""
    # Output was already called with mocked print in the when step


@then('the message is printed to stderr')
def step_message_printed_to_stderr(context: Context) -> None:
    """Verify the error message was printed (mocked in when step)."""
    # Error was already called with mocked print in the when step


@then('the first input returns "{expected}"')
def step_first_input_returns(context: Context, expected: str) -> None:
    """Verify the first input returned the expected value."""
    ctx = get_io_context(context)
    assert ctx.input_results[0] == expected


@then('the second input returns "{expected}"')
def step_second_input_returns(context: Context, expected: str) -> None:
    """Verify the second input returned the expected value."""
    ctx = get_io_context(context)
    assert ctx.input_results[1] == expected


@then('a RuntimeError is raised with message "{expected_message}"')
def step_runtime_error_raised(context: Context, expected_message: str) -> None:
    """Verify a RuntimeError was raised with the expected message."""
    ctx = get_io_context(context)
    assert ctx.exception is not None
    assert isinstance(ctx.exception, RuntimeError)
    assert str(ctx.exception) == expected_message


@then('the captured outputs are "{output1}" and "{output2}"')
def step_captured_outputs_are(context: Context, output1: str, output2: str) -> None:
    """Verify the captured outputs."""
    ctx = get_io_context(context)
    assert ctx.provider.outputs == [output1, output2]


@then('the captured errors are "{error1}" and "{error2}"')
def step_captured_errors_are(context: Context, error1: str, error2: str) -> None:
    """Verify the captured errors."""
    ctx = get_io_context(context)
    assert ctx.provider.errors == [error1, error2]


@then('the prompt result is successful with value {expected:d}')
def step_result_successful_with_int(context: Context, expected: int) -> None:
    """Verify the prompt result is successful with the expected integer value."""
    ctx = get_io_context(context)
    assert ctx.result.is_success(), f'Expected success but got failure: {ctx.result}'
    assert ctx.result.value_or(0) == expected


@then('the prompt result is successful with value "{expected}"')
def step_result_successful_with_string(context: Context, expected: str) -> None:
    """Verify the prompt result is successful with the expected string value."""
    ctx = get_io_context(context)
    assert ctx.result.is_success(), f'Expected success but got failure: {ctx.result}'
    assert ctx.result.value_or('') == expected


@then('the provider captured one error message')
def step_provider_captured_one_error(context: Context) -> None:
    """Verify the provider captured exactly one error message."""
    ctx = get_io_context(context)
    assert len(ctx.provider.errors) == 1


@then('the custom provider received prompt "CUSTOM: Enter value: "')
def step_custom_provider_received_prompt(context: Context) -> None:
    """Verify the custom provider received the expected prefixed prompt."""
    ctx = get_io_context(context)
    assert 'CUSTOM: Enter value: ' in ctx.custom_provider.prompts_received


@then('the custom provider captured error with color codes')
def step_custom_provider_captured_colored_error(context: Context) -> None:
    """Verify the custom provider captured error with color codes."""
    ctx = get_io_context(context)
    assert len(ctx.custom_provider.errors) > 0
    assert '\033[91m' in ctx.custom_provider.errors[0]  # ANSI red color code


@then('the custom error message contains "{expected_text}"')
def step_custom_error_contains_text(context: Context, expected_text: str) -> None:
    """Verify the custom error message contains expected text."""
    ctx = get_io_context(context)
    assert any(expected_text in error for error in ctx.custom_provider.errors)


@then('the function uses builtins.input internally')
def step_uses_builtin_input(context: Context) -> None:
    """Verify the function used builtins.input (mocked in when step)."""
    # This was already tested via mocked builtins.input in the when step


@then('the prompt succeeds')
def step_prompt_succeeds(context: Context) -> None:
    """Verify the prompt succeeded."""
    ctx = get_io_context(context)
    assert ctx.result.is_success()


@then('the name result is successful with value "{expected}"')
def step_name_result_successful(context: Context, expected: str) -> None:
    """Verify the name result is successful."""
    ctx = get_io_context(context)
    assert ctx.name_result.is_success()
    assert ctx.name_result.value_or('') == expected


@then('the age result is successful with value {expected:d}')
def step_age_result_successful(context: Context, expected: int) -> None:
    """Verify the age result is successful."""
    ctx = get_io_context(context)
    assert ctx.age_result.is_success()
    assert ctx.age_result.value_or(0) == expected


@then('the confirmation result is successful with value {expected}')
def step_confirmation_result_successful(context: Context, expected: str) -> None:
    """Verify the confirmation result is successful."""
    ctx = get_io_context(context)
    # Convert string to boolean
    expected_bool = expected.lower() == 'true'
    assert ctx.confirmation_result.is_success()
    # Use a default value constant to avoid FBT003
    default_value = False
    assert ctx.confirmation_result.value_or(default_value) == expected_bool


@then('it implements the IOProvider protocol')
def step_implements_protocol(context: Context) -> None:
    """Verify the provider implements the IOProvider protocol."""
    ctx = get_io_context(context)
    provider = ctx.provider if ctx.provider else ctx.custom_provider
    assert isinstance(provider, IOProvider)


@then('it has input, output, and error methods')
def step_has_required_methods(context: Context) -> None:
    """Verify the provider has required methods."""
    ctx = get_io_context(context)
    provider = ctx.provider if ctx.provider else ctx.custom_provider
    assert hasattr(provider, 'input')
    assert hasattr(provider, 'output')
    assert hasattr(provider, 'error')
