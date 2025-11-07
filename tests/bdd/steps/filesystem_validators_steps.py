"""BDD step definitions for filesystem metadata validators.

This module defines step definitions for testing filesystem metadata validators
(max_size, min_size, has_extension) on files with various sizes and extensions.
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


@given('the validators max_size, min_size, has_extension are available')
def step_filesystem_metadata_validators_available(context: Context) -> None:
    """Verify filesystem metadata validators module can be imported."""
    ctx = get_custom_context(context)
    # Try to import validators - will fail if not implemented yet
    try:
        from valid8r.core.validators import (
            has_extension,
            max_size,
            min_size,
        )

        ctx.validators_available = True
        ctx.max_size = max_size
        ctx.min_size = min_size
        ctx.has_extension = has_extension
    except ImportError:
        ctx.validators_available = False
        # Store placeholder functions that return Failure
        ctx.max_size = lambda _size: lambda _p: Failure('max_size not implemented yet')
        ctx.min_size = lambda _size: lambda _p: Failure('min_size not implemented yet')
        ctx.has_extension = lambda *_exts: lambda _p: Failure('has_extension not implemented yet')


@given('I have a temporary directory for test files')
def step_have_temporary_directory_for_test_files(context: Context) -> None:
    """Create a temporary test directory for file operations.

    Note: In Behave, we don't have access to pytest fixtures directly,
    so we need to create our own temporary directory.
    """
    ctx = get_custom_context(context)
    ctx.temp_dir = Path(tempfile.mkdtemp())


@given('a temporary file of {size:d} bytes')
def step_temporary_file_of_size(context: Context, size: int) -> None:
    """Create a temporary file with specific size in bytes."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / f'test_file_{size}b.bin'
    # Write exactly 'size' bytes
    temp_file.write_bytes(b'X' * size)
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('an empty temporary file')
def step_empty_temporary_file(context: Context) -> None:
    """Create an empty temporary file (0 bytes)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / 'empty_file.bin'
    temp_file.touch()  # Create empty file
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('a file named "{filename}"')
def step_file_named(context: Context, filename: str) -> None:
    """Create a file with the specified name."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / filename
    temp_file.write_text('test content')
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('a temporary file named "{filename}" of {size:d} bytes')
def step_temporary_file_named_with_size(context: Context, filename: str, size: int) -> None:
    """Create a temporary file with specific name and size."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / filename
    temp_file.write_bytes(b'X' * size)
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('an empty temporary file named "{filename}"')
def step_empty_temporary_file_named(context: Context, filename: str) -> None:
    """Create an empty temporary file with specific name."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / filename
    temp_file.touch()
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('a temporary file named "{filename}" of {size:d} bytes that exists')
def step_temporary_file_named_with_size_that_exists(context: Context, filename: str, size: int) -> None:
    """Create a temporary file with specific name and size (emphasizing it exists)."""
    ctx = get_custom_context(context)
    temp_file = ctx.temp_dir / filename
    temp_file.write_bytes(b'X' * size)
    ctx.temp_file = temp_file
    ctx.path_object = temp_file


@given('a non-existent file path "{filename}"')
def step_non_existent_file_path(context: Context, filename: str) -> None:
    """Create a path to a non-existent file."""
    ctx = get_custom_context(context)
    ctx.temp_file = ctx.temp_dir / filename
    ctx.path_object = ctx.temp_file
    # Ensure it doesn't exist
    if ctx.temp_file.exists():
        ctx.temp_file.unlink()


@given('a temporary directory named "{dirname}"')
def step_temporary_directory_named(context: Context, dirname: str) -> None:
    """Create a temporary directory with specific name."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / dirname
    temp_subdir.mkdir()
    ctx.temp_directory = temp_subdir
    ctx.path_object = temp_subdir


@given('a temporary directory')
def step_temporary_directory(context: Context) -> None:
    """Create a temporary directory."""
    ctx = get_custom_context(context)
    temp_subdir = ctx.temp_dir / 'test_directory'
    temp_subdir.mkdir()
    ctx.temp_directory = temp_subdir
    ctx.path_object = temp_subdir


@given('a symbolic link to a file of {size:d} bytes')
def step_symbolic_link_to_file_of_size(context: Context, size: int) -> None:
    """Create a symbolic link pointing to a file with specific size."""
    ctx = get_custom_context(context)
    # Create target file
    target_file = ctx.temp_dir / f'target_file_{size}b.bin'
    target_file.write_bytes(b'X' * size)
    # Create symlink
    symlink_path = ctx.temp_dir / 'symlink_to_file'
    symlink_path.symlink_to(target_file)
    ctx.temp_symlink = symlink_path
    ctx.path_object = symlink_path


# ==========================================
# When Steps - Execute validators
# ==========================================


@when('I validate with max_size({max_bytes:d})')
def step_validate_with_max_size(context: Context, max_bytes: int) -> None:
    """Validate the path with max_size validator."""
    ctx = get_custom_context(context)
    validator = ctx.max_size(max_bytes)
    ctx.result = validator(ctx.path_object)


@when('I validate with min_size({min_bytes:d})')
def step_validate_with_min_size(context: Context, min_bytes: int) -> None:
    """Validate the path with min_size validator."""
    ctx = get_custom_context(context)
    validator = ctx.min_size(min_bytes)
    ctx.result = validator(ctx.path_object)


@when('I validate with has_extension({extensions})')
def step_validate_with_has_extension(context: Context, extensions: str) -> None:
    """Validate the path with has_extension validator (any number of extensions)."""
    ctx = get_custom_context(context)
    # Parse extensions from string like "'.pdf'" or "'.pdf', '.doc', '.docx'"
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    validator = ctx.has_extension(*ext_list)
    ctx.result = validator(ctx.path_object)


@when('I validate with min_size({min_bytes:d}) and has_extension({extensions})')
def step_validate_with_min_size_and_extension(context: Context, min_bytes: int, extensions: str) -> None:
    """Validate with both min_size and has_extension validators."""
    ctx = get_custom_context(context)
    # Parse extensions
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    min_size_validator = ctx.min_size(min_bytes)
    ext_validator = ctx.has_extension(*ext_list)
    # Chain validators
    ctx.result = min_size_validator(ctx.path_object).bind(ext_validator)


@when('I validate with max_size({max_bytes:d}) and has_extension({extensions})')
def step_validate_with_max_size_and_extension(context: Context, max_bytes: int, extensions: str) -> None:
    """Validate with both max_size and has_extension validators."""
    ctx = get_custom_context(context)
    # Parse extensions from string like "'.pdf'" or "'.pdf', '.docx'"
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    max_size_validator = ctx.max_size(max_bytes)
    ext_validator = ctx.has_extension(*ext_list)
    # Chain validators
    ctx.result = max_size_validator(ctx.path_object).bind(ext_validator)


@when('I validate with min_size({min_bytes:d}) and max_size({max_bytes:d}) and has_extension({extensions})')
def step_validate_with_min_max_size_and_extension(
    context: Context, min_bytes: int, max_bytes: int, extensions: str
) -> None:
    """Validate with min_size, max_size, and has_extension validators."""
    ctx = get_custom_context(context)
    # Parse extensions
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    min_size_validator = ctx.min_size(min_bytes)
    max_size_validator = ctx.max_size(max_bytes)
    ext_validator = ctx.has_extension(*ext_list)
    # Chain validators
    ctx.result = min_size_validator(ctx.path_object).bind(max_size_validator).bind(ext_validator)


@when('I validate with parse_path and is_file and max_size({max_bytes:d}) and has_extension({extensions})')
def step_validate_with_full_pipeline(context: Context, max_bytes: int, extensions: str) -> None:
    """Validate with full pipeline: parse_path -> is_file -> max_size -> has_extension."""
    ctx = get_custom_context(context)
    # Import parsers and validators
    try:
        from valid8r.core.parsers import parse_path
        from valid8r.core.validators import is_file
    except ImportError:
        ctx.result = Failure('parse_path or is_file not implemented yet')
        return

    # Parse extensions
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    max_size_validator = ctx.max_size(max_bytes)
    ext_validator = ctx.has_extension(*ext_list)

    # Execute pipeline
    path_str = str(ctx.path_object)
    ctx.result = parse_path(path_str).bind(is_file()).bind(max_size_validator).bind(ext_validator)


@when('I validate with parse_path and exists and max_size({max_bytes:d}) and has_extension({extensions})')
def step_validate_with_parse_path_exists_pipeline(context: Context, max_bytes: int, extensions: str) -> None:
    """Validate with pipeline: parse_path -> exists -> max_size -> has_extension."""
    ctx = get_custom_context(context)
    # Import parsers and validators
    try:
        from valid8r.core.parsers import parse_path
        from valid8r.core.validators import exists
    except ImportError:
        ctx.result = Failure('parse_path or exists not implemented yet')
        return

    # Parse extensions
    ext_list = [ext.strip().strip('\'"') for ext in extensions.split(',')]
    max_size_validator = ctx.max_size(max_bytes)
    ext_validator = ctx.has_extension(*ext_list)

    # Execute pipeline
    path_str = str(ctx.path_object)
    ctx.result = parse_path(path_str).bind(exists()).bind(max_size_validator).bind(ext_validator)


@when('I validate with parse_path and is_file and max_size({max_bytes:d})')
def step_validate_with_parse_path_is_file_max_size(context: Context, max_bytes: int) -> None:
    """Validate with pipeline: parse_path -> is_file -> max_size."""
    ctx = get_custom_context(context)
    # Import parsers and validators
    try:
        from valid8r.core.parsers import parse_path
        from valid8r.core.validators import is_file
    except ImportError:
        ctx.result = Failure('parse_path or is_file not implemented yet')
        return

    max_size_validator = ctx.max_size(max_bytes)

    # Execute pipeline
    path_str = str(ctx.path_object)
    ctx.result = parse_path(path_str).bind(is_file()).bind(max_size_validator)


@when('I validate as an upload with 10MB limit and PDF extension')
def step_validate_as_upload_10mb_pdf(context: Context) -> None:
    """Validate file as upload with 10MB limit and PDF extension."""
    ctx = get_custom_context(context)
    max_size_validator = ctx.max_size(10 * 1024 * 1024)  # 10MB
    ext_validator = ctx.has_extension('.pdf')
    ctx.result = max_size_validator(ctx.path_object).bind(ext_validator)


@when('I validate as an upload with 10MB limit and office extensions')
def step_validate_as_upload_10mb_office(context: Context) -> None:
    """Validate file as upload with 10MB limit and office extensions."""
    ctx = get_custom_context(context)
    max_size_validator = ctx.max_size(10 * 1024 * 1024)  # 10MB
    ext_validator = ctx.has_extension('.pdf', '.doc', '.docx', '.ppt', '.pptx')
    ctx.result = max_size_validator(ctx.path_object).bind(ext_validator)


# ==========================================
# Then Steps - Verify results
# ==========================================


@then('I get Success with the Path')
def step_filesystem_result_is_success_with_path(context: Context) -> None:
    """Verify the validation result is Success containing a Path object.

    Note: Uses 'the Path' to avoid ambiguity with environment_variables_steps.py
    which has a parameterized step @then('I get Success with {expected_dict}').
    """
    ctx = get_custom_context(context)
    assert ctx.result is not None, 'No result found in context'
    match ctx.result:
        case Success(value):
            assert isinstance(value, Path), f'Expected Path but got {type(value).__name__}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


# Alias for consistency with Gherkin phrasing variations
@then('the result is Success with a Path')
def step_filesystem_result_is_success_with_path_alias(context: Context) -> None:
    """Alias for 'I get Success with the Path'."""
    step_filesystem_result_is_success_with_path(context)


# Note: "I get Failure mentioning" step is already defined in environment_variables_steps.py
# and works for all features. No need to duplicate it here.


# Alias for And steps - "the failure message mentions"
@then('the failure message mentions "{substring}"')
def step_and_failure_message_mentions(context: Context, substring: str) -> None:
    """Verify the failure message also contains the specified substring (for And steps)."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Failure(err):
            assert substring in err, f'Expected error to contain "{substring}" but got: {err}'
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')
