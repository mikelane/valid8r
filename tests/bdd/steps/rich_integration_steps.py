"""BDD step definitions for Rich integration example."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


@given('I run the example application')
def step_run_example_application(context: Context) -> None:
    """Set up the Rich integration example application for testing.

    This step expects an example application to exist at:
    examples/rich-integration/project_wizard.py

    Until the example is implemented, this step will fail.
    """
    # Try to import the example application
    # This will fail until senior-developer implements it
    try:
        # The actual example should be runnable
        from examples.rich_integration import project_wizard  # noqa: F401

        context.example_exists = True
    except ImportError:
        context.example_exists = False
        msg = (
            'Rich integration example not found at examples/rich-integration/project_wizard.py. '
            'This is expected during RED phase - senior-developer will implement it in Phase 3.'
        )
        raise AssertionError(msg) from None

    context.test_mode = 'success'


@given('I run the example with batch processing')
def step_run_example_batch_processing(context: Context) -> None:
    """Set up the Rich integration example for batch processing.

    This step expects batch processing mode in the example application.
    Until implemented, this will fail.
    """
    try:
        from examples.rich_integration import project_wizard  # noqa: F401

        context.example_exists = True
    except ImportError:
        context.example_exists = False
        msg = (
            'Rich integration example not found. '
            'This is expected during RED phase - senior-developer will implement it in Phase 3.'
        )
        raise AssertionError(msg) from None

    context.test_mode = 'batch'


@given('I run the example in interactive mode')
def step_run_example_interactive_mode(context: Context) -> None:
    """Set up the Rich integration example for interactive prompts.

    This step expects interactive mode in the example application.
    Until implemented, this will fail.
    """
    try:
        from examples.rich_integration import project_wizard  # noqa: F401

        context.example_exists = True
    except ImportError:
        context.example_exists = False
        msg = (
            'Rich integration example not found. '
            'This is expected during RED phase - senior-developer will implement it in Phase 3.'
        )
        raise AssertionError(msg) from None

    context.test_mode = 'interactive'


@given('I run the example')
def step_run_example(context: Context) -> None:
    """Set up a visually impressive Rich integration example.

    This step expects the full visual demo mode.
    Until implemented, this will fail.
    """
    try:
        from examples.rich_integration import project_wizard  # noqa: F401

        context.example_exists = True
    except ImportError:
        context.example_exists = False
        msg = (
            'Rich integration example not found. '
            'This is expected during RED phase - senior-developer will implement it in Phase 3.'
        )
        raise AssertionError(msg) from None

    context.test_mode = 'visual_demo'

    # Run the visual demo scenario
    _run_example_scenario(context, 'visual_demo')


@when('validation succeeds')
def step_validation_succeeds(context: Context) -> None:
    """Run the application expecting successful validation.

    This will call the actual example application once it exists.
    """
    if not context.example_exists:
        msg = 'Cannot run validation - example not implemented yet'
        raise AssertionError(msg)

    # Run the actual example with success scenario
    _run_example_scenario(context, 'success')


@when('Rich validation fails')
def step_validation_fails(context: Context) -> None:
    """Run the application expecting validation failure.

    This will call the actual example application with invalid input.
    """
    if not context.example_exists:
        msg = 'Cannot run validation - example not implemented yet'
        raise AssertionError(msg)

    # Run the actual example with failure scenario
    _run_example_scenario(context, 'failure')


@when('multiple items are validated')
def step_multiple_items_validated(context: Context) -> None:
    """Run batch processing validation.

    This will call the actual example application in batch mode.
    """
    if not context.example_exists:
        msg = 'Cannot run batch validation - example not implemented yet'
        raise AssertionError(msg)

    # Run the actual example in batch mode
    _run_example_scenario(context, 'batch')


@when('I am prompted for input')
def step_prompted_for_input(context: Context) -> None:
    """Run interactive mode with input.

    This will call the actual example application in interactive mode.
    """
    if not context.example_exists:
        msg = 'Cannot run interactive mode - example not implemented yet'
        raise AssertionError(msg)

    # Run the actual example in interactive mode with stdin
    context.stdin_input = 'user@example.com'
    _run_example_scenario(context, 'interactive', stdin=context.stdin_input)


@then('I see success messages in Rich panels')
def step_see_success_panels(context: Context) -> None:
    """Verify Rich panels with success messages."""
    output = _strip_ansi(context.app_stdout)
    assert 'Success' in output or 'successful' in output.lower(), (
        f'Expected success message in output\nstdout: {context.app_stdout}'
    )
    # Check for panel borders (Rich uses box drawing characters)
    assert '─' in context.app_stdout or '│' in context.app_stdout, (
        f'Expected Rich panel borders in output\nstdout: {context.app_stdout}'
    )


@then('I see validated data in Rich tables')
def step_see_data_in_tables(context: Context) -> None:
    """Verify Rich tables with validated data."""
    output = _strip_ansi(context.app_stdout)
    # Check for table structure
    assert 'Field' in output or 'Value' in output or 'Validated Data' in output, (
        f'Expected table headers in output\nstdout: {context.app_stdout}'
    )
    # Check for table borders
    assert '─' in context.app_stdout or '│' in context.app_stdout, (
        f'Expected Rich table borders in output\nstdout: {context.app_stdout}'
    )


@then('I see error messages styled with Rich')
def step_see_styled_errors(context: Context) -> None:
    """Verify Rich-styled error messages."""
    output = _strip_ansi(context.app_stdout)
    assert 'Validation Error' in output or 'error' in output.lower(), (
        f'Expected error message in output\nstdout: {context.app_stdout}'
    )
    # Check for Rich panel/box borders
    assert '─' in context.app_stdout or '│' in context.app_stdout, (
        f'Expected Rich styling (borders) in output\nstdout: {context.app_stdout}'
    )


@then('errors are highlighted with appropriate colors')
def step_errors_highlighted(context: Context) -> None:
    """Verify errors use color codes (ANSI escape sequences)."""
    # Check for ANSI color codes (Rich uses these for styling)
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    matches = ansi_pattern.findall(context.app_stdout)
    assert len(matches) > 0, f'Expected ANSI color codes in output\nstdout: {context.app_stdout}'


@then('errors include helpful suggestions')
def step_errors_include_suggestions(context: Context) -> None:
    """Verify error output includes suggestions."""
    output = _strip_ansi(context.app_stdout)
    assert 'Suggestion' in output or 'suggestion' in output.lower() or 'format' in output.lower(), (
        f'Expected helpful suggestion in output\nstdout: {context.app_stdout}'
    )


@then('I see a Rich progress bar')
def step_see_progress_bar(context: Context) -> None:
    """Verify Rich progress bar output."""
    output = _strip_ansi(context.app_stdout)
    # Progress bars typically have descriptions and percentages
    assert 'Validating' in output or 'Processing' in output or '%' in output, (
        f'Expected progress bar indicators in output\nstdout: {context.app_stdout}'
    )


@then('progress updates reflect validation status')
def step_progress_reflects_status(context: Context) -> None:
    """Verify progress bar reflects validation completion."""
    output = _strip_ansi(context.app_stdout)
    # Check for completion indicators
    assert 'Validated' in output or 'complete' in output.lower() or '100%' in output, (
        f'Expected completion status in output\nstdout: {context.app_stdout}'
    )


@then('prompts use Rich styling')
def step_prompts_use_styling(context: Context) -> None:
    """Verify prompts use Rich styling."""
    # Check for ANSI color codes
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    matches = ansi_pattern.findall(context.app_stdout)
    assert len(matches) > 0, f'Expected styled prompts (ANSI codes) in output\nstdout: {context.app_stdout}'


@then('invalid input shows styled error messages')
def step_invalid_input_styled_errors(context: Context) -> None:
    """Verify invalid input triggers styled error messages."""
    # Run with invalid input
    context.stdin_input = 'invalid-email'
    _run_example_scenario(context, 'interactive', stdin=context.stdin_input)

    output = _strip_ansi(context.app_stdout)
    # Check for error indicators
    assert '✗' in context.app_stdout or 'error' in output.lower() or 'invalid' in output.lower(), (
        f'Expected error message for invalid input\nstdout: {context.app_stdout}'
    )


@then('I see professional-quality terminal output')
def step_see_professional_output(context: Context) -> None:
    """Verify output meets professional quality standards."""
    output = _strip_ansi(context.app_stdout)

    # Check for multiple Rich UI elements
    has_panels = '─' in context.app_stdout and '│' in context.app_stdout
    has_colors = re.search(r'\x1b\[[0-9;]*m', context.app_stdout) is not None
    has_content = len(output.strip()) > 0

    assert has_panels, f'Expected panel/table borders in output\nstdout: {context.app_stdout}'
    assert has_colors, f'Expected colored output (ANSI codes)\nstdout: {context.app_stdout}'
    assert has_content, f'Expected non-empty output\nstdout: {context.app_stdout}'


@then('I want to share screenshots on social media')
def step_want_to_share_screenshots(context: Context) -> None:
    """Verify output is visually impressive enough to share.

    This is a subjective criterion, so we verify objective quality markers:
    - Multiple visual elements (panels, tables, progress bars)
    - Rich styling (colors, borders, unicode characters)
    - Clear structure and formatting
    """
    output = _strip_ansi(context.app_stdout)

    # Check for multiple Rich elements
    element_count = 0
    if '─' in context.app_stdout and '│' in context.app_stdout:
        element_count += 1  # Panels/tables
    if '✓' in context.app_stdout or '✗' in context.app_stdout:
        element_count += 1  # Status icons
    if re.search(r'\x1b\[[0-9;]*m', context.app_stdout):
        element_count += 1  # Colors
    if any(keyword in output for keyword in ['Valid8r', 'Demo', 'Results', 'Table']):
        element_count += 1  # Titles/headers

    assert element_count >= 3, (
        f'Expected at least 3 visual elements for share-worthy output, got {element_count}\n'
        f'stdout: {context.app_stdout}'
    )


def _run_example_scenario(context: Context, scenario: str, stdin: str | None = None) -> None:
    """Run the Rich integration example application in a specific scenario.

    This function will be implemented to run the actual example once it exists.
    During RED phase, this placeholder ensures tests fail as expected.

    Args:
        context: The Behave context
        scenario: The scenario to run ('success', 'failure', 'batch', 'interactive', 'visual_demo')
        stdin: Optional stdin input for interactive mode

    """
    # The example should be at: examples/rich-integration/project_wizard.py
    # It should accept command-line arguments to specify scenario:
    #   python project_wizard.py --scenario=success
    #   python project_wizard.py --scenario=failure
    #   python project_wizard.py --scenario=batch
    #   python project_wizard.py --scenario=interactive

    example_path = Path('examples/rich_integration/project_wizard.py')
    if not example_path.exists():
        msg = f'Example not found at {example_path} - implementation needed'
        raise AssertionError(msg)

    # Run the example
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(example_path), f'--scenario={scenario}'],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
        input=stdin,
    )

    # Store results for assertions
    context.app_exit_code = result.returncode
    context.app_stdout = result.stdout
    context.app_stderr = result.stderr


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text.

    Args:
        text: Text containing ANSI escape codes

    Returns:
        Text with ANSI codes removed

    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)
