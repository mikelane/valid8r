from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from behave import (
    given,
    then,
    when,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.validators import (
    maximum,
    minimum,
)
from valid8r.prompt.basic import ask
from valid8r.testing import (
    MockInputContext,
    assert_maybe_success,
    configure_mock_input,
    generate_random_inputs,
    generate_test_cases,
    test_validator_composition,
)

if TYPE_CHECKING:
    from behave.runner import Context


# Context class to store testing data between steps
class TestingContext:
    def __init__(self) -> None:
        """Initialize the testing context."""
        self.mock_inputs: list[str] = []
        self.prompt_result: Maybe[Any] | None = None
        self.maybe_result: Maybe[Any] | None = None
        self.assertion_result: bool | None = None
        self.test_cases: dict | None = None
        self.composed_validator = None
        self.random_inputs: list[Any] | None = None


# Helper to get or create testing context
def get_testing_context(context: Context) -> TestingContext:
    if not hasattr(context, 'testing_context'):
        context.testing_context = TestingContext()
    return context.testing_context


@given('the testing utilities module is available')
def step_testing_module_available(context: Context) -> None:  # noqa: ARG001
    """Check that the testing utilities module is available."""
    # This will fail until we create the module
    assert MockInputContext is not None
    assert configure_mock_input is not None
    assert assert_maybe_success is not None


@when('I configure the mock input to return a single value "{input_value}"')
def step_configure_mock_input(context: Context, input_value: str) -> None:
    """Configure mock input to return the specified value."""
    tc = get_testing_context(context)
    tc.mock_inputs = [input_value]
    configure_mock_input(tc.mock_inputs)


@when('I configure the mock input to return a sequence "{input1}" then "{input2}"')
def step_configure_mock_input_sequence(context: Context, input1: str, input2: str) -> None:
    """Configure mock input to return a sequence of values."""
    tc = get_testing_context(context)
    tc.mock_inputs = [input1, input2]
    configure_mock_input(tc.mock_inputs)


@when('I use the testing utility to test a prompt for an integer')
def step_test_prompt_for_integer(context: Context) -> None:
    """Test a prompt for an integer using the mock input."""
    tc = get_testing_context(context)
    with MockInputContext(tc.mock_inputs):
        tc.prompt_result = ask('Enter a number: ', parser=lambda s: Maybe.success(int(s)))


@when('I use the testing utility to test a prompt with retry')
def step_test_prompt_with_retry(context: Context) -> None:
    """Test a prompt with retry using the mock input."""
    tc = get_testing_context(context)
    with MockInputContext(tc.mock_inputs):
        tc.prompt_result = ask(
            'Enter a number: ',
            parser=lambda s: Maybe.success(int(s)) if s.isdigit() else Maybe.failure('Not a number'),
            retry=True,
        )


@when('I use the testing utility to test a prompt with minimum {min_val:d} validation')
def step_test_prompt_with_validation(context: Context, min_val: int) -> None:
    """Test a prompt with validation using the mock input."""
    tc = get_testing_context(context)
    with MockInputContext(tc.mock_inputs):
        # First parse the input to an integer, then apply the minimum validator
        tc.prompt_result = ask(
            'Enter a number: ',
            parser=lambda s: Maybe.success(int(s))
            if s.isdigit() or (s.startswith('-') and s[1:].isdigit())
            else Maybe.failure('Not a number'),
            validator=minimum(min_val),
        )


@when('I have a Maybe result from a validation')
def step_have_maybe_result(context: Context) -> None:
    """Set up a Maybe result for testing."""
    tc = get_testing_context(context)
    tc.maybe_result = Maybe.success(42)


@when('I use the assertion helper to verify it succeeded with value {value:d}')
def step_use_assertion_helper(context: Context, value: int) -> None:
    """Use the assertion helper to verify a success result."""
    tc = get_testing_context(context)
    tc.assertion_result = assert_maybe_success(tc.maybe_result, value)


@when('I request test data for the minimum validator with value {min_val:d}')
def step_request_test_data(context: Context, min_val: int) -> None:
    """Request test data for a specific validator."""
    tc = get_testing_context(context)
    tc.test_cases = generate_test_cases(minimum(min_val))


@when('I compose a validator using minimum {min_val:d} AND maximum {max_val:d}')
def step_compose_validator(context: Context, min_val: int, max_val: int) -> None:
    """Compose a validator using logical operators."""
    tc = get_testing_context(context)
    tc.composed_validator = minimum(min_val) & maximum(max_val)


@when('I use the testing utility to verify the composition')
def step_verify_composition(context: Context) -> None:
    """Use the testing utility to verify validator composition."""
    tc = get_testing_context(context)
    tc.assertion_result = test_validator_composition(tc.composed_validator)


@when('I request random test inputs for a specific validator')
def step_request_random_inputs(context: Context) -> None:
    """Request random test inputs for a validator."""
    tc = get_testing_context(context)
    min_validator = minimum(0)
    tc.random_inputs = generate_random_inputs(min_validator)


@when('I use the test context manager with input "{input_value}"')
def step_use_context_manager(context: Context, input_value: str) -> None:
    """Set up the test context manager."""
    tc = get_testing_context(context)
    tc.mock_inputs = [input_value]


@when('I call a function that prompts for input')
def step_call_function_with_prompt(context: Context) -> None:
    """Call a function that prompts for input within the context manager."""
    tc = get_testing_context(context)

    def function_with_prompt() -> Maybe[str]:
        with MockInputContext(tc.mock_inputs):
            return ask('Enter something: ')

    tc.prompt_result = function_with_prompt()


@then('the prompt should return a successful Maybe with value {value:d}')
def step_prompt_returns_success(context: Context, value: int) -> None:
    """Verify that the prompt returned a successful Maybe with the expected value."""
    tc = get_testing_context(context)
    assert tc.prompt_result is not None

    match tc.prompt_result:
        case Success(val):
            assert val == value, f'Expected {value}, got {val}'
        case _:
            msg = f'Expected Success, got {tc.prompt_result}'
            raise AssertionError(msg)


@then('the prompt should return a failure Maybe with error "{error_msg}"')
def step_prompt_returns_failure(context: Context, error_msg: str) -> None:
    """Verify that the prompt returned a failure Maybe with the expected error."""
    tc = get_testing_context(context)
    assert tc.prompt_result is not None

    match tc.prompt_result:
        case Failure(error):
            assert error == error_msg, f"Expected error '{error_msg}', got '{error}'"
        case _:
            msg = f'Expected Failure, got {tc.prompt_result}'
            raise AssertionError(msg)


@then('the assertion should pass')
def step_assertion_passes(context: Context) -> None:
    """Verify that the assertion passed."""
    tc = get_testing_context(context)
    assert tc.assertion_result is True, 'Assertion should have passed'


@then('I should receive valid and invalid test cases')
def step_receive_test_cases(context: Context) -> None:
    """Verify that we received both valid and invalid test cases."""
    tc = get_testing_context(context)
    assert tc.test_cases is not None
    assert 'valid' in tc.test_cases, 'Should have valid test cases'
    assert 'invalid' in tc.test_cases, 'Should have invalid test cases'
    assert len(tc.test_cases['valid']) > 0, 'Should have at least one valid test case'
    assert len(tc.test_cases['invalid']) > 0, 'Should have at least one invalid test case'


@then('the valid cases should be greater than or equal to {value:d}')
def step_valid_cases_greater_than(context: Context, value: int) -> None:
    """Verify that all valid test cases meet the criterion."""
    tc = get_testing_context(context)
    for case in tc.test_cases['valid']:
        assert case >= value, f'Valid case {case} should be >= {value}'


@then('the invalid cases should be less than {value:d}')
def step_invalid_cases_less_than(context: Context, value: int) -> None:
    """Verify that all invalid test cases meet the criterion."""
    tc = get_testing_context(context)
    for case in tc.test_cases['invalid']:
        assert case < value, f'Invalid case {case} should be < {value}'


@then('it should verify behavior for multiple test cases')
def step_verify_multiple_test_cases(context: Context) -> None:
    """Verify that the composition testing checks multiple test cases."""
    tc = get_testing_context(context)
    assert tc.assertion_result is True, 'Composition testing should pass'


@then('I should receive inputs that both pass and fail the validation')
def step_receive_mixed_inputs(context: Context) -> None:
    """Verify that we received a mix of passing and failing inputs."""
    tc = get_testing_context(context)
    assert tc.random_inputs is not None
    assert len(tc.random_inputs) > 0, 'Should have received some inputs'

    # There should be a mix of passing and failing inputs
    min_validator = minimum(0)
    passing = [i for i in tc.random_inputs if min_validator(i).is_success()]
    failing = [i for i in tc.random_inputs if min_validator(i).is_failure()]

    assert len(passing) > 0, 'Should have at least one passing input'
    assert len(failing) > 0, 'Should have at least one failing input'


@then('the function should receive "{expected}" as input')
def step_function_receives_input(context: Context, expected: str) -> None:
    """Verify that the function received the expected input."""
    tc = get_testing_context(context)
    assert tc.prompt_result is not None

    match tc.prompt_result:
        case Success(val):
            assert val == expected, f"Expected '{expected}', got '{val}'"
        case _:
            msg = f"Expected Success with '{expected}', got {tc.prompt_result}"
            raise AssertionError(msg)
