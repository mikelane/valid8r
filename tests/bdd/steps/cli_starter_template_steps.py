from __future__ import annotations

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
    from behave.runner import Context


# Context to store template-related state
class CliTemplateContext:
    def __init__(self) -> None:
        """Initialize the CLI template context."""
        self.template_path: Path | None = None
        self.cli_result: subprocess.CompletedProcess | None = None
        self.config_file_path: Path | None = None
        self.validation_errors: list[str] = []


def get_cli_template_context(context: Context) -> CliTemplateContext:
    """Get or create the CLI template context."""
    if not hasattr(context, 'cli_template_context'):
        context.cli_template_context = CliTemplateContext()
    return context.cli_template_context


# Scenario: Template validates command arguments


@given('I clone the starter template')
def step_clone_starter_template(context: Context) -> None:
    """Verify the CLI starter template exists in examples directory."""
    ctx = get_cli_template_context(context)

    # The template should exist at examples/cli-starter-template/
    template_dir = Path(__file__).parent.parent.parent.parent / 'examples' / 'cli-starter-template'

    assert template_dir.exists(), f'CLI starter template not found at {template_dir}'
    assert template_dir.is_dir(), f'{template_dir} is not a directory'

    ctx.template_path = template_dir

    # Verify the template has a main CLI script
    cli_script = template_dir / 'cli.py'
    assert cli_script.exists(), f'CLI script not found at {cli_script}'


@when('I run the CLI with invalid arguments')
def step_run_cli_with_invalid_arguments(context: Context) -> None:
    """Run the CLI with invalid arguments and capture the result."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    cli_script = ctx.template_path / 'cli.py'

    # Run the CLI with invalid arguments (e.g., invalid user age)
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(cli_script), 'add-user', '--name', 'John', '--age', 'not-a-number'],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ctx.template_path),
    )

    ctx.cli_result = result


@then('I see clear error messages explaining what went wrong')
def step_see_clear_error_messages(context: Context) -> None:
    """Verify the error message is clear and informative."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    # Error message should appear in stderr or stdout
    output = ctx.cli_result.stderr + ctx.cli_result.stdout

    # Verify the error message is present and explains the issue
    assert len(output) > 0, 'No error message provided'
    assert 'age' in output.lower(), 'Error message does not mention the problematic field'

    # Store error messages for further checks
    ctx.validation_errors = [line for line in output.split('\n') if line.strip()]


@then('the program exits cleanly')
def step_program_exits_cleanly(context: Context) -> None:
    """Verify the program exits with a non-zero error code."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    # Should exit with error code 1 (user error) not 0 (success)
    assert ctx.cli_result.returncode != 0, 'Program should exit with error code for invalid input'
    assert ctx.cli_result.returncode == 1, f'Expected exit code 1, got {ctx.cli_result.returncode}'


@then('I understand how to fix the error')
def step_understand_how_to_fix_error(context: Context) -> None:
    """Verify the error message provides actionable guidance."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'
    assert len(ctx.validation_errors) > 0, 'No validation errors captured'

    output = ctx.cli_result.stderr + ctx.cli_result.stdout

    # Error message should indicate what type of value is expected
    assert any(keyword in output.lower() for keyword in ['integer', 'number', 'numeric', 'expected']), (
        'Error message does not explain expected input type'
    )


# Scenario: Template provides interactive prompts


@when('I run the CLI in interactive mode')
def step_run_cli_in_interactive_mode(context: Context) -> None:
    """Run the CLI in interactive mode and provide inputs."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    cli_script = ctx.template_path / 'cli.py'

    # Run the CLI in interactive mode with invalid then valid inputs
    # Simulating: invalid age "twenty", then valid age "25"
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(cli_script), 'add-user', '--interactive'],
        check=False,
        input='John Doe\ntwenty\n25\njohn@example.com\n',
        capture_output=True,
        text=True,
        cwd=str(ctx.template_path),
    )

    ctx.cli_result = result


@then('I am prompted for required information')
def step_prompted_for_required_information(context: Context) -> None:
    """Verify the CLI prompts for required fields."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    output = ctx.cli_result.stdout

    # Verify prompts appear for required fields
    assert 'name' in output.lower(), 'No prompt for name field'
    assert 'age' in output.lower(), 'No prompt for age field'
    assert 'email' in output.lower(), 'No prompt for email field'


@then('invalid inputs are rejected with helpful feedback')
def step_invalid_inputs_rejected_with_feedback(context: Context) -> None:
    """Verify invalid inputs are rejected with helpful messages."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    output = ctx.cli_result.stdout + ctx.cli_result.stderr

    # Should show rejection of invalid age input "twenty"
    assert 'invalid' in output.lower() or 'error' in output.lower(), 'No indication of invalid input rejection'


@then('I can successfully complete the workflow')
def step_successfully_complete_workflow(context: Context) -> None:
    """Verify the workflow completes successfully after valid input."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    # After providing valid inputs, the command should succeed
    assert ctx.cli_result.returncode == 0, f'Expected success (exit code 0), got {ctx.cli_result.returncode}'

    output = ctx.cli_result.stdout

    # Should show success message
    assert 'success' in output.lower() or 'added' in output.lower(), 'No success confirmation message'


# Scenario: Template validates configuration files


@given('I provide a configuration file')
def step_provide_configuration_file(context: Context) -> None:
    """Create a test configuration file with invalid content."""
    import uuid

    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Create a temporary config file with unique name to avoid race conditions
    unique_id = uuid.uuid4().hex[:8]
    config_file = ctx.template_path / f'test_config_{unique_id}.yaml'
    config_content = """
users:
  - name: Alice
    age: "not-a-number"  # Invalid: age should be integer
    email: alice@example.com
  - name: Bob
    age: 30
    email: "invalid-email"  # Invalid: malformed email
"""

    config_file.write_text(config_content)
    ctx.config_file_path = config_file


@when('the CLI loads the configuration')
def step_cli_loads_configuration(context: Context) -> None:
    """Run the CLI to load and validate the configuration file."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'
    assert ctx.config_file_path is not None, 'Config file not set'

    cli_script = ctx.template_path / 'cli.py'

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(cli_script), 'load-config', '--file', str(ctx.config_file_path)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ctx.template_path),
    )

    ctx.cli_result = result

    # Clean up the test config file
    if ctx.config_file_path.exists():
        ctx.config_file_path.unlink()


@then('invalid configuration is rejected')
def step_invalid_configuration_rejected(context: Context) -> None:
    """Verify invalid configuration is rejected."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    # Should exit with error code
    assert ctx.cli_result.returncode != 0, 'Invalid configuration should be rejected'


@then('I see which configuration values are wrong')
def step_see_which_values_are_wrong(context: Context) -> None:
    """Verify error messages identify the invalid fields."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    output = ctx.cli_result.stderr + ctx.cli_result.stdout

    # Should identify both invalid fields
    assert 'age' in output.lower(), 'Error message does not mention invalid age field'
    assert 'email' in output.lower(), 'Error message does not mention invalid email field'


@then('I see the file location and line number')
def step_see_file_location_and_line_number(context: Context) -> None:
    """Verify error messages include file location and line numbers."""
    ctx = get_cli_template_context(context)

    assert ctx.cli_result is not None, 'CLI result not set'

    output = ctx.cli_result.stderr + ctx.cli_result.stdout

    # Should reference the config file
    assert 'config' in output.lower() or '.yaml' in output.lower(), (
        'Error message does not reference configuration file'
    )

    # Should include line number or position information
    assert any(indicator in output.lower() for indicator in ['line', 'row', 'position', 'at']), (
        'Error message does not include line number or position'
    )


# Scenario: Template is easy to customize


@when('I want to add my own validation logic')
def step_want_to_add_validation_logic(context: Context) -> None:
    """Check that the template code is organized for easy extension."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Verify the template has a validators module
    validators_file = ctx.template_path / 'validators.py'
    assert validators_file.exists(), 'Template does not have a validators module'

    # Read the validators file to check for examples
    validators_content = validators_file.read_text()
    ctx.validation_errors = []  # Reuse for storing file content
    ctx.validation_errors.append(validators_content)


@then('I can understand the code structure')
def step_understand_code_structure(context: Context) -> None:
    """Verify the code has clear structure and organization."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Check for standard Python project structure
    required_files = ['cli.py', 'validators.py', 'README.md', 'tests']

    for file_name in required_files:
        file_path = ctx.template_path / file_name
        assert file_path.exists(), f'Template missing {file_name}'


@then('I can find clear examples to follow')
def step_find_clear_examples(context: Context) -> None:
    """Verify the template includes example validation logic."""
    ctx = get_cli_template_context(context)

    assert len(ctx.validation_errors) > 0, 'Validators content not loaded'

    validators_content = ctx.validation_errors[0]

    # Should contain example validator functions
    assert 'def ' in validators_content, 'No example functions found'
    assert 'valid8r' in validators_content, 'Does not import valid8r'


@then('I can extend the template for my use case')
def step_extend_template_for_use_case(context: Context) -> None:
    """Verify the template is designed for extension."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Check README includes customization guidance
    readme_file = ctx.template_path / 'README.md'
    readme_content = readme_file.read_text()

    # README should mention customization
    assert any(keyword in readme_content.lower() for keyword in ['customize', 'extend', 'modify', 'add your own']), (
        'README does not explain how to customize the template'
    )


# Scenario: Template demonstrates quality standards


@then('the code is well-documented')
def step_code_is_well_documented(context: Context) -> None:
    """Verify the code includes comprehensive documentation."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Check main CLI file for docstrings
    cli_file = ctx.template_path / 'cli.py'
    cli_content = cli_file.read_text()

    # Should have module docstring and function docstrings
    assert '"""' in cli_content or "'''" in cli_content, 'No docstrings found in CLI code'

    # Count docstrings (should have at least 3: module + functions)
    docstring_count = cli_content.count('"""') + cli_content.count("'''")
    assert docstring_count >= 4, f'Insufficient docstrings: found {docstring_count // 2} docstrings'


@then('the project structure is clear')
def step_project_structure_is_clear(context: Context) -> None:
    """Verify the project follows standard Python conventions."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Verify standard project files exist
    essential_files = [
        'cli.py',  # Main CLI script
        'validators.py',  # Validation logic
        'README.md',  # Documentation
        'requirements.txt',  # Dependencies
        'tests',  # Test directory
    ]

    for file_name in essential_files:
        file_path = ctx.template_path / file_name
        assert file_path.exists(), f'Missing essential file: {file_name}'


@then('I can run tests successfully')
def step_run_tests_successfully(context: Context) -> None:
    """Verify the template includes a working test suite."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    tests_dir = ctx.template_path / 'tests'
    assert tests_dir.exists(), 'Tests directory does not exist'

    # Verify at least one test file exists
    test_files = list(tests_dir.glob('test_*.py'))
    assert len(test_files) > 0, 'No test files found in tests directory'

    # Run the tests
    result = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'pytest', 'tests', '-v'],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ctx.template_path),
    )

    ctx.cli_result = result

    # Tests should pass
    assert result.returncode == 0, f'Tests failed: {result.stderr}'


@then('I can build the project without errors')
def step_build_project_without_errors(context: Context) -> None:
    """Verify the project can be imported and has no syntax errors."""
    ctx = get_cli_template_context(context)

    assert ctx.template_path is not None, 'Template path not set'

    # Try to import the main CLI module (syntax check)
    cli_file = ctx.template_path / 'cli.py'

    result = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'py_compile', str(cli_file)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f'CLI file has syntax errors: {result.stderr}'

    # Try to compile validators module
    validators_file = ctx.template_path / 'validators.py'

    result = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'py_compile', str(validators_file)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f'Validators file has syntax errors: {result.stderr}'
