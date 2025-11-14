"""Practical examples of filesystem path parsing and validation.

This module demonstrates real-world use cases for filesystem validation
using Valid8r's monadic error handling pattern.
"""

# ruff: noqa: D301, D401, ERA001, C901, S306

from __future__ import annotations

from pathlib import Path

from valid8r import (
    parsers,
    validators,
)
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)


def validate_upload_file(file_path: str) -> Maybe[Path]:
    """Validate uploaded files: PDF/DOCX, readable, under 10MB.

    Args:
        file_path: Path to the uploaded file

    Returns:
        Success(Path) if valid, Failure(error_message) if invalid

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.pdf'))
        >>> temp_file.write_bytes(b'PDF content')
        11
        >>> result = validate_upload_file(str(temp_file))
        >>> result.is_success()
        True
        >>> temp_file.unlink()

    """
    return (
        parsers.parse_path(file_path)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.pdf', '.docx']))
        .bind(validators.max_size(10 * 1024 * 1024))
    )


def validate_config_file(path_str: str) -> Maybe[Path]:
    """Validate configuration file: exists, readable, YAML/JSON.

    Expands user directory (~) and resolves to absolute path.

    Args:
        path_str: Path to configuration file (can include ~)

    Returns:
        Success(Path) if valid config file, Failure(error_message) otherwise

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.yaml'))
        >>> temp_file.write_text('key: value')
        10
        >>> result = validate_config_file(str(temp_file))
        >>> result.is_success()
        True
        >>> temp_file.unlink()

    """
    return (
        parsers.parse_path(path_str, expand_user=True, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.yaml', '.yml', '.json']))
    )


def validate_output_directory(path_str: str) -> Maybe[Path]:
    """Validate output directory: exists, is directory, writable.

    Args:
        path_str: Path to output directory

    Returns:
        Success(Path) if valid writable directory, Failure(error_message) otherwise

    Example:
        >>> import tempfile
        >>> temp_dir = tempfile.mkdtemp()
        >>> result = validate_output_directory(temp_dir)
        >>> result.is_success()
        True
        >>> import shutil
        >>> shutil.rmtree(temp_dir)

    """
    return (
        parsers.parse_path(path_str, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_dir())
        .bind(validators.is_writable())
    )


def validate_image_file(path_str: str) -> Maybe[Path]:
    """Validate image files: exists, readable, correct extension, under 5MB.

    Args:
        path_str: Path to image file

    Returns:
        Success(Path) if valid image file, Failure(error_message) otherwise

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.jpg'))
        >>> temp_file.write_bytes(b'fake image data')
        15
        >>> result = validate_image_file(str(temp_file))
        >>> result.is_success()
        True
        >>> temp_file.unlink()

    """
    return (
        parsers.parse_path(path_str)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.jpg', '.jpeg', '.png', '.gif']))
        .bind(validators.max_size(5 * 1024 * 1024))
    )


def validate_executable(path_str: str) -> Maybe[Path]:
    """Validate executable: exists, is file, executable, under 100MB.

    Args:
        path_str: Path to executable file

    Returns:
        Success(Path) if valid executable, Failure(error_message) otherwise

    Example:
        >>> # Most systems have /bin/sh or /usr/bin/python3
        >>> import shutil
        >>> python_path = shutil.which('python3')
        >>> if python_path:
        ...     result = validate_executable(python_path)
        ...     result.is_success()
        ... else:
        ...     True  # Skip test if python3 not found
        True

    """
    return (
        parsers.parse_path(path_str, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_executable())
        .bind(validators.max_size(100 * 1024 * 1024))
    )


def validate_data_file(path_str: str) -> Maybe[Path]:
    """Validate data file: exists, readable, CSV/JSON/XLSX, not empty.

    Args:
        path_str: Path to data file

    Returns:
        Success(Path) if valid data file, Failure(error_message) otherwise

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.csv'))
        >>> temp_file.write_text('col1,col2\\nval1,val2')
        19
        >>> result = validate_data_file(str(temp_file))
        >>> result.is_success()
        True
        >>> temp_file.unlink()

    """
    return (
        parsers.parse_path(path_str)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.csv', '.json', '.xlsx']))
        .bind(validators.min_size(1))  # Not empty
    )


def validate_log_file(path_str: str, max_size_mb: int = 100) -> Maybe[Path]:
    """Validate log file: exists, is file, writable, under size limit.

    Args:
        path_str: Path to log file
        max_size_mb: Maximum size in megabytes (default: 100MB)

    Returns:
        Success(Path) if valid log file, Failure(error_message) otherwise

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.log'))
        >>> temp_file.write_text('log entry\\n')
        10
        >>> result = validate_log_file(str(temp_file), max_size_mb=1)
        >>> result.is_success()
        True
        >>> temp_file.unlink()

    """
    return (
        parsers.parse_path(path_str, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_writable())
        .bind(validators.max_size(max_size_mb * 1024 * 1024))
    )


def example_file_upload_handler(file_path: str) -> dict[str, str]:
    """Example file upload handler using validation.

    Args:
        file_path: Path to uploaded file

    Returns:
        Dictionary with status and message

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.pdf'))
        >>> temp_file.write_bytes(b'PDF content')
        11
        >>> result = example_file_upload_handler(str(temp_file))
        >>> result['status']
        'success'
        >>> temp_file.unlink()

    """
    match validate_upload_file(file_path):
        case Success(path):
            # Process the validated file
            return {
                'status': 'success',
                'message': f'File uploaded successfully: {path.name}',
                'size': path.stat().st_size,
            }
        case Failure(err):
            return {
                'status': 'error',
                'message': f'Upload rejected: {err}',
            }


def example_config_loader(config_path: str) -> dict[str, str] | None:
    """Example configuration loader with validation.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary or None if invalid

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.yaml'))
        >>> temp_file.write_text('database:\\n  host: localhost\\n')
        29
        >>> result = example_config_loader(str(temp_file))
        >>> result is not None
        True
        >>> temp_file.unlink()

    """
    match validate_config_file(config_path):
        case Success(path):
            # In production, use actual YAML/JSON loader
            # import yaml
            # with open(path) as f:
            #     return yaml.safe_load(f)
            return {'config_loaded': True, 'path': str(path)}
        case Failure(err):
            print(f'Failed to load config: {err}')
            return None


def example_batch_validator(file_paths: list[str]) -> tuple[list[Path], list[str]]:
    """Validate a batch of files, returning valid paths and error messages.

    Args:
        file_paths: List of file paths to validate

    Returns:
        Tuple of (valid_paths, error_messages)

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp1 = Path(tempfile.mktemp(suffix='.pdf'))
        >>> temp1.write_bytes(b'PDF')
        3
        >>> temp2 = Path(tempfile.mktemp(suffix='.txt'))
        >>> temp2.write_bytes(b'Text')
        4
        >>> valid, errors = example_batch_validator([str(temp1), str(temp2)])
        >>> len(valid)
        1
        >>> len(errors)
        1
        >>> temp1.unlink()
        >>> temp2.unlink()

    """
    valid_paths: list[Path] = []
    error_messages: list[str] = []

    for file_path in file_paths:
        match validate_upload_file(file_path):
            case Success(path):
                valid_paths.append(path)
            case Failure(err):
                error_messages.append(f'{file_path}: {err}')

    return valid_paths, error_messages


def example_secure_file_processor(file_path: str) -> bool:
    """Example secure file processor with comprehensive validation.

    Demonstrates defense in depth: multiple validation layers.

    Args:
        file_path: Path to file to process

    Returns:
        True if file was processed successfully, False otherwise

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix='.pdf'))
        >>> temp_file.write_bytes(b'PDF content')
        11
        >>> result = example_secure_file_processor(str(temp_file))
        >>> result
        True
        >>> temp_file.unlink()

    """
    # Layer 1: Basic path validation
    path_result = parsers.parse_path(file_path, resolve=True)
    match path_result:
        case Failure(err):
            print(f'Invalid path: {err}')
            return False
        case Success(path):
            pass

    # Layer 2: Existence and type validation
    existence_result = path_result.bind(validators.exists()).bind(validators.is_file())
    match existence_result:
        case Failure(err):
            print(f'File check failed: {err}')
            return False
        case Success(path):
            pass

    # Layer 3: Permission validation
    permission_result = existence_result.bind(validators.is_readable())
    match permission_result:
        case Failure(err):
            print(f'Permission denied: {err}')
            return False
        case Success(path):
            pass

    # Layer 4: Security validation (not executable)
    security_result = permission_result.bind(~validators.is_executable())
    match security_result:
        case Failure(err):
            print(f'Security check failed: {err}')
            return False
        case Success(path):
            pass

    # Layer 5: Content type validation
    content_result = security_result.bind(validators.has_extension(['.pdf', '.docx', '.txt']))
    match content_result:
        case Failure(err):
            print(f'Invalid file type: {err}')
            return False
        case Success(path):
            pass

    # Layer 6: Size validation
    size_result = content_result.bind(validators.max_size(10 * 1024 * 1024))
    match size_result:
        case Failure(err):
            print(f'File too large: {err}')
            return False
        case Success(path):
            # All validations passed - safe to process
            print(f'Processing file: {path}')
            # In production: actually process the file
            return True


if __name__ == '__main__':
    """Run examples demonstrating filesystem validation."""
    import tempfile
    from pathlib import Path

    print('=== Filesystem Validation Examples ===\n')

    # Example 1: File upload validation
    print('1. File Upload Validation:')
    temp_pdf = Path(tempfile.mktemp(suffix='.pdf'))
    temp_pdf.write_bytes(b'PDF content here')
    result = example_file_upload_handler(str(temp_pdf))
    print(f'   Status: {result["status"]}, Message: {result["message"]}')
    temp_pdf.unlink()

    # Example 2: Invalid file extension
    print('\n2. Invalid Extension:')
    temp_exe = Path(tempfile.mktemp(suffix='.exe'))
    temp_exe.write_bytes(b'executable')
    result = example_file_upload_handler(str(temp_exe))
    print(f'   Status: {result["status"]}, Message: {result["message"]}')
    temp_exe.unlink()

    # Example 3: Config file validation
    print('\n3. Config File Validation:')
    temp_config = Path(tempfile.mktemp(suffix='.yaml'))
    temp_config.write_text('database:\n  host: localhost\n')
    config = example_config_loader(str(temp_config))
    print(f'   Config loaded: {config is not None}')
    temp_config.unlink()

    # Example 4: Batch validation
    print('\n4. Batch Validation:')
    temp_files = [
        Path(tempfile.mktemp(suffix='.pdf')),
        Path(tempfile.mktemp(suffix='.docx')),
        Path(tempfile.mktemp(suffix='.txt')),
    ]
    for f in temp_files:
        f.write_bytes(b'content')

    valid, errors = example_batch_validator([str(f) for f in temp_files])
    print(f'   Valid files: {len(valid)}')
    print(f'   Errors: {len(errors)}')

    for f in temp_files:
        f.unlink()

    # Example 5: Secure file processing
    print('\n5. Secure File Processing:')
    temp_secure = Path(tempfile.mktemp(suffix='.pdf'))
    temp_secure.write_bytes(b'PDF data')
    success = example_secure_file_processor(str(temp_secure))
    print(f'   Processing succeeded: {success}')
    temp_secure.unlink()

    print('\n=== Examples Complete ===')
