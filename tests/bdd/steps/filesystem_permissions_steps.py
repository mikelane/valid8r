"""BDD step definitions for filesystem permission validators.

This module defines step definitions for testing filesystem permission validators
(is_readable, is_writable, is_executable) on files and directories with various permissions.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
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
# Given Steps - Set up test fixtures
# ==========================================


@given('the filesystem permission validators are available')
def step_filesystem_permission_validators_available(context: Context) -> None:
    """Verify filesystem permission validators module can be imported."""
    ctx = get_custom_context(context)
    # Try to import validators - will fail if not implemented yet
    try:
        from valid8r.core.validators import (
            is_executable,
            is_readable,
            is_writable,
        )

        ctx.validators_available = True
        # Call the factory functions to get Validator instances
        ctx.is_readable = is_readable()
        ctx.is_writable = is_writable()
        ctx.is_executable = is_executable()
    except ImportError:
        ctx.validators_available = False
        # Store placeholder functions that return Failure
        ctx.is_readable = lambda _p: Failure('is_readable not implemented yet')
        ctx.is_writable = lambda _p: Failure('is_writable not implemented yet')
        ctx.is_executable = lambda _p: Failure('is_executable not implemented yet')


@given('I have a temporary test directory')
def step_have_temporary_test_directory(context: Context) -> None:
    """Create a temporary test directory for file operations.

    Note: In Behave, we don't have access to pytest fixtures directly,
    so we need to create our own temporary directory.
    """
    ctx = get_custom_context(context)
    ctx.temp_dir = Path(tempfile.mkdtemp())


@given('a temporary file with read permissions')
def step_temporary_file_with_read_permissions(context: Context) -> None:
    """Create a temporary file with read permissions (0o444)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o444)  # r--r--r--
    ctx.temp_file = temp_file


@given('a temporary file without read permissions')
def step_temporary_file_without_read_permissions(context: Context) -> None:
    """Create a temporary file without read permissions (0o200)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'not_readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o200)  # -w-------
    ctx.temp_file = temp_file


@given('a temporary file with write permissions')
def step_temporary_file_with_write_permissions(context: Context) -> None:
    """Create a temporary file with write permissions (0o644)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'writable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o644)  # rw-r--r--
    ctx.temp_file = temp_file


@given('a temporary file without write permissions')
def step_temporary_file_without_write_permissions(context: Context) -> None:
    """Create a temporary file without write permissions (0o444)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'not_writable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o444)  # r--r--r--
    ctx.temp_file = temp_file


@given('a temporary file with execute permissions')
def step_temporary_file_with_execute_permissions(context: Context) -> None:
    """Create a temporary file with execute permissions (0o755)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'executable_file.sh'
    temp_file.write_text('#!/bin/bash\necho "test"')
    temp_file.chmod(0o755)  # rwxr-xr-x
    ctx.temp_file = temp_file


@given('a temporary file without execute permissions')
def step_temporary_file_without_execute_permissions(context: Context) -> None:
    """Create a temporary file without execute permissions (0o644)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'not_executable_file.sh'
    temp_file.write_text('#!/bin/bash\necho "test"')
    temp_file.chmod(0o644)  # rw-r--r--
    ctx.temp_file = temp_file


@given('I have a Path object for that file')
def step_have_path_object_for_file(context: Context) -> None:
    """Store the file's Path object for validation."""
    ctx = get_custom_context(context)
    ctx.path_object = ctx.temp_file


@given('a temporary directory with read permissions')
def step_temporary_directory_with_read_permissions(context: Context) -> None:
    """Create a temporary directory with read permissions (0o555)."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / 'readable_dir'
    temp_subdir.mkdir()
    temp_subdir.chmod(0o555)  # r-xr-xr-x
    ctx.temp_directory = temp_subdir


@given('I have a Path object for that directory')
def step_have_path_object_for_directory(context: Context) -> None:
    """Store the directory's Path object for validation."""
    ctx = get_custom_context(context)
    ctx.path_object = ctx.temp_directory


@given('a temporary directory with write permissions')
def step_temporary_directory_with_write_permissions(context: Context) -> None:
    """Create a temporary directory with write permissions (0o755)."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / 'writable_dir'
    temp_subdir.mkdir()
    temp_subdir.chmod(0o755)  # rwxr-xr-x
    ctx.temp_directory = temp_subdir


@given('a non-existent file path')
def step_non_existent_file_path(context: Context) -> None:
    """Create a path to a non-existent file."""
    ctx = get_custom_context(context)
    ctx.path_object = ctx.temp_dir / 'non_existent_file.txt'
    # Ensure it doesn't exist
    if ctx.path_object.exists():
        ctx.path_object.unlink()


@given('a temporary file with read and write permissions')
def step_temporary_file_with_read_and_write_permissions(context: Context) -> None:
    """Create a temporary file with read and write permissions (0o644)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'rw_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o644)  # rw-r--r--
    ctx.temp_file = temp_file


@given('a combined validator with is_readable and is_writable')
def step_combined_validator_readable_writable(context: Context) -> None:
    """Create a combined validator using is_readable and is_writable."""
    ctx = get_custom_context(context)
    from valid8r.core.maybe import Maybe

    # Create a combined validator function
    def combined_validator(path: Path) -> Maybe[Path]:
        return ctx.is_readable(path).bind(ctx.is_writable)

    ctx.combined_validator = combined_validator


@given('a temporary file with read-only permissions')
def step_temporary_file_with_read_only_permissions(context: Context) -> None:
    """Create a temporary file with read-only permissions (0o444)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'readonly_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o444)  # r--r--r--
    ctx.temp_file = temp_file


@given('a symbolic link pointing to that file')
def step_symbolic_link_to_file(context: Context) -> None:
    """Create a symbolic link pointing to the temporary file."""
    ctx = get_custom_context(context)
    symlink_path = ctx.temp_dir / 'symlink_to_file'
    symlink_path.symlink_to(ctx.temp_file)
    ctx.temp_symlink = symlink_path


@given('I have a Path object for the symlink')
def step_have_path_object_for_symlink(context: Context) -> None:
    """Store the symlink's Path object for validation."""
    ctx = get_custom_context(context)
    ctx.path_object = ctx.temp_symlink


@given('a symbolic link pointing to a non-existent file')
def step_broken_symbolic_link(context: Context) -> None:
    """Create a broken symbolic link (pointing to non-existent file)."""
    ctx = get_custom_context(context)
    non_existent_target = ctx.temp_dir / 'non_existent_target.txt'
    symlink_path = ctx.temp_dir / 'broken_symlink'
    # Ensure target doesn't exist
    if non_existent_target.exists():
        non_existent_target.unlink()
    # Create symlink to non-existent target
    symlink_path.symlink_to(non_existent_target)
    ctx.temp_symlink = symlink_path


@given('a readable file at a known path')
def step_readable_file_at_known_path(context: Context) -> None:
    """Create a readable file and store its string path."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o644)  # rw-r--r--
    ctx.temp_file = temp_file
    ctx.path_string = str(temp_file)


@given('a non-readable file at a known path')
def step_non_readable_file_at_known_path(context: Context) -> None:
    """Create a non-readable file and store its string path."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'not_readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o200)  # -w-------
    ctx.temp_file = temp_file
    ctx.path_string = str(temp_file)


@given('a readable regular file at a known path')
def step_readable_regular_file_at_known_path(context: Context) -> None:
    """Create a readable regular file (not directory) and store its string path."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o644)  # rw-r--r--
    ctx.temp_file = temp_file
    ctx.path_string = str(temp_file)


@given('a readable directory at a known path')
def step_readable_directory_at_known_path(context: Context) -> None:
    """Create a readable directory and store its string path."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / 'readable_dir'
    temp_subdir.mkdir()
    temp_subdir.chmod(0o755)  # rwxr-xr-x
    ctx.temp_directory = temp_subdir
    ctx.path_string = str(temp_subdir)


@given('a non-readable regular file at a known path')
def step_non_readable_regular_file_at_known_path(context: Context) -> None:
    """Create a non-readable regular file and store its string path."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'not_readable_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o200)  # -w-------
    ctx.temp_file = temp_file
    ctx.path_string = str(temp_file)


@given('a writable directory for output')
def step_writable_directory_for_output(context: Context) -> None:
    """Create a writable directory and store its string path."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / 'output_dir'
    temp_subdir.mkdir()
    temp_subdir.chmod(0o755)  # rwxr-xr-x
    ctx.temp_directory = temp_subdir
    ctx.path_string = str(temp_subdir)


@given('a temporary file with read, write, and execute permissions')
def step_temporary_file_with_all_permissions(context: Context) -> None:
    """Create a temporary file with all permissions (0o777)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'all_perms_file.sh'
    temp_file.write_text('#!/bin/bash\necho "test"')
    temp_file.chmod(0o777)  # rwxrwxrwx
    ctx.temp_file = temp_file


@given('a combined validator with is_readable, is_writable, and is_executable')
def step_combined_validator_all_permissions(context: Context) -> None:
    """Create a combined validator using is_readable, is_writable, and is_executable."""
    ctx = get_custom_context(context)
    from valid8r.core.maybe import Maybe

    # Create a combined validator function
    def combined_validator(path: Path) -> Maybe[Path]:
        return ctx.is_readable(path).bind(ctx.is_writable).bind(ctx.is_executable)

    ctx.combined_validator = combined_validator


@given('a temporary file with write-only permissions')
def step_temporary_file_with_write_only_permissions(context: Context) -> None:
    """Create a temporary file with write-only permissions (0o200)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'writeonly_file.txt'
    temp_file.write_text('test content')
    temp_file.chmod(0o200)  # -w-------
    ctx.temp_file = temp_file


# ==========================================
# When Steps - Execute validators
# ==========================================


@when('I validate the path with is_readable')
def step_validate_with_is_readable(context: Context) -> None:
    """Validate the path with is_readable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.is_readable(ctx.path_object)


@when('I validate the path with is_writable')
def step_validate_with_is_writable(context: Context) -> None:
    """Validate the path with is_writable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.is_writable(ctx.path_object)


@when('I validate the path with is_executable')
def step_validate_with_is_executable(context: Context) -> None:
    """Validate the path with is_executable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.is_executable(ctx.path_object)


@when('I validate the path with the combined validator')
def step_validate_with_combined_validator(context: Context) -> None:
    """Validate the path with the combined validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.combined_validator(ctx.path_object)


@when('I parse the path string with parse_path')
def step_parse_path_string(context: Context) -> None:
    """Parse the path string with parse_path parser."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_path
    except ImportError:
        ctx.result = Failure('parse_path not implemented yet')
        return

    ctx.result = parse_path(ctx.path_string)


@when('bind the result with is_readable validator')
def step_bind_with_is_readable(context: Context) -> None:
    """Bind the current result with is_readable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.result.bind(ctx.is_readable)


@when('bind with is_readable validator')
def step_bind_with_is_readable_validator(context: Context) -> None:
    """Bind the current result with is_readable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.result.bind(ctx.is_readable)


@when('bind with is_writable validator')
def step_bind_with_is_writable_validator(context: Context) -> None:
    """Bind the current result with is_writable validator."""
    ctx = get_custom_context(context)
    ctx.result = ctx.result.bind(ctx.is_writable)


@when('bind with exists validator')
def step_bind_with_exists(context: Context) -> None:
    """Bind the current result with exists validator."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.validators import exists
    except ImportError:
        ctx.result = Failure('exists validator not implemented yet')
        return

    ctx.result = ctx.result.bind(exists())


@when('bind with is_file validator')
def step_bind_with_is_file(context: Context) -> None:
    """Bind the current result with is_file validator."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.validators import is_file
    except ImportError:
        ctx.result = Failure('is_file validator not implemented yet')
        return

    ctx.result = ctx.result.bind(is_file())


@when('bind with is_dir validator')
def step_bind_with_is_dir(context: Context) -> None:
    """Bind the current result with is_dir validator."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.validators import is_dir
    except ImportError:
        ctx.result = Failure('is_dir validator not implemented yet')
        return

    ctx.result = ctx.result.bind(is_dir())


# ==========================================
# Then Steps - Verify results
# ==========================================


@then('the validation result is a Success')
def step_validation_result_is_success(context: Context) -> None:
    """Verify the validation result is Success."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(_):
            pass  # Test passes
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the result contains the same Path')
def step_result_contains_same_path(context: Context) -> None:
    """Verify the result contains the same Path object."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, Path), f'Expected Path but got {type(value).__name__}'
            assert value == ctx.path_object, f'Expected {ctx.path_object} but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success with Path but got Failure: {err}')


@then('the validation result is a Failure')
def step_validation_result_is_failure(context: Context) -> None:
    """Verify the validation result is Failure."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Failure(_):
            pass  # Test passes
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')


# Note: step 'the error message contains "{substring}"' already defined in url_email_parsing_steps.py


@then('the result contains the symlink Path')
def step_result_contains_symlink_path(context: Context) -> None:
    """Verify the result contains the symlink Path object."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, Path), f'Expected Path but got {type(value).__name__}'
            assert value == ctx.temp_symlink, f'Expected {ctx.temp_symlink} but got {value}'
        case Failure(err):
            pytest.fail(f'Expected Success with symlink Path but got Failure: {err}')


@then('the final result is a Success')
def step_final_result_is_success(context: Context) -> None:
    """Verify the final result is Success."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(_):
            pass  # Test passes
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the result contains the parsed Path')
def step_result_contains_parsed_path(context: Context) -> None:
    """Verify the result contains a parsed Path object."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            assert isinstance(value, Path), f'Expected Path but got {type(value).__name__}'
        case Failure(err):
            pytest.fail(f'Expected Success with parsed Path but got Failure: {err}')


@then('the final result is a Failure')
def step_final_result_is_failure(context: Context) -> None:
    """Verify the final result is Failure."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Failure(_):
            pass  # Test passes
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')
