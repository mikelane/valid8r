# Filesystem Parsing and Validation

This guide covers parsing and validating filesystem paths using Valid8r's monadic error handling.

## Overview

Valid8r provides comprehensive filesystem support through:

- **`parse_path`**: Parse strings to `pathlib.Path` objects
- **Filesystem Validators**: `exists`, `is_file`, `is_dir`, `is_readable`, `is_writable`, `is_executable`
- **File Property Validators**: `max_size`, `min_size`, `has_extension`
- **Monadic Composition**: Chain parsing and validation using `bind()`

All operations return `Maybe[Path]` for composable error handling without exceptions.

## Basic Path Parsing

### parse_path

Parse a string to a `pathlib.Path` object:

```python
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

# Parse absolute path
match parsers.parse_path("/etc/hosts"):
    case Success(path):
        print(f"Path: {path}")
    case Failure(err):
        print(f"Error: {err}")

# Parse relative path
match parsers.parse_path("data/file.txt"):
    case Success(path):
        print(f"Path: {path}")
    case Failure(err):
        print(f"Error: {err}")
```

### Path Expansion

Expand home directory (`~`) and resolve to absolute paths:

```python
# Expand user directory
match parsers.parse_path("~/Documents", expand_user=True):
    case Success(path):
        print(f"Expanded: {path}")  # /Users/username/Documents

# Resolve to absolute path
match parsers.parse_path("./data", resolve=True):
    case Success(path):
        print(f"Resolved: {path}")  # /full/path/to/data

# Combine both
match parsers.parse_path("~/data", expand_user=True, resolve=True):
    case Success(path):
        print(f"Full path: {path}")
```

### Custom Error Messages

Provide user-friendly error messages:

```python
result = parsers.parse_path(
    None,
    error_message="Please provide a configuration file path"
)
match result:
    case Failure(err):
        print(err)  # "Please provide a configuration file path"
```

## Filesystem Validators

### exists

Verify that a path exists in the filesystem:

```python
from valid8r import parsers, validators

# Validate that a path exists
result = parsers.parse_path("/etc/hosts").bind(validators.exists())
match result:
    case Success(path):
        print(f"File exists: {path}")
    case Failure(err):
        print(f"Error: {err}")  # "Path does not exist: /etc/hosts"
```

### is_file / is_dir

Verify that a path is a file or directory:

```python
# Validate file
result = (
    parsers.parse_path("/etc/hosts")
    .bind(validators.exists())
    .bind(validators.is_file())
)

# Validate directory
result = (
    parsers.parse_path("/etc")
    .bind(validators.exists())
    .bind(validators.is_dir())
)
```

### Permission Validators

Check file permissions:

```python
# Readable file
result = (
    parsers.parse_path("config.yaml")
    .bind(validators.exists())
    .bind(validators.is_readable())
)

# Writable file
result = (
    parsers.parse_path("output.log")
    .bind(validators.exists())
    .bind(validators.is_writable())
)

# Executable file
result = (
    parsers.parse_path("/usr/bin/python3")
    .bind(validators.exists())
    .bind(validators.is_executable())
)
```

### File Size Validators

Validate file sizes (in bytes):

```python
# Maximum size (10MB)
result = (
    parsers.parse_path("upload.pdf")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(validators.max_size(10 * 1024 * 1024))
)

# Minimum size (reject empty files)
result = (
    parsers.parse_path("data.csv")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(validators.min_size(1))
)

# Size range
size_range = validators.min_size(1024) & validators.max_size(1024 * 1024)
result = (
    parsers.parse_path("document.pdf")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(size_range)
)
```

### File Extension Validator

Validate file extensions:

```python
# Single extension
result = (
    parsers.parse_path("document.pdf")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(validators.has_extension(['.pdf']))
)

# Multiple allowed extensions
result = (
    parsers.parse_path("document.docx")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(validators.has_extension(['.pdf', '.docx', '.txt']))
)

# Case-insensitive matching
result = (
    parsers.parse_path("IMAGE.JPG")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(validators.has_extension(['.jpg', '.png']))
)
```

## Combining Validators

Use combinator operators to build complex validation logic:

### AND Combinator (`&`)

All validators must pass:

```python
# Readable PDF under 10MB
pdf_validator = (
    validators.exists() &
    validators.is_file() &
    validators.is_readable() &
    validators.has_extension(['.pdf']) &
    validators.max_size(10 * 1024 * 1024)
)

result = parsers.parse_path("document.pdf").bind(pdf_validator)
```

### OR Combinator (`|`)

At least one validator must pass:

```python
# Accept either PDF or Word documents
document_validator = (
    validators.has_extension(['.pdf']) |
    validators.has_extension(['.docx', '.doc'])
)

result = (
    parsers.parse_path("document.docx")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(document_validator)
)
```

### NOT Combinator (`~`)

Negate a validator:

```python
# File must NOT be executable (security check)
result = (
    parsers.parse_path("data.txt")
    .bind(validators.exists())
    .bind(validators.is_file())
    .bind(~validators.is_executable())
)
```

## Practical Examples

### File Upload Validation

```python
from valid8r import parsers, validators
from valid8r.core.maybe import Maybe
from pathlib import Path

def validate_upload(file_path: str) -> Maybe[Path]:
    """Validate uploaded files: PDF/DOCX, readable, under 10MB."""
    return (
        parsers.parse_path(file_path)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.pdf', '.docx']))
        .bind(validators.max_size(10 * 1024 * 1024))
    )

# Usage
match validate_upload("/tmp/upload.pdf"):
    case Success(path):
        print(f"Valid upload: {path}")
        # Process file...
    case Failure(err):
        print(f"Upload rejected: {err}")
```

### Configuration File Validation

```python
def validate_config_file(path_str: str) -> Maybe[Path]:
    """Validate configuration file: exists, readable, YAML/JSON."""
    return (
        parsers.parse_path(path_str, expand_user=True, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.yaml', '.yml', '.json']))
    )

# Usage
match validate_config_file("~/config.yaml"):
    case Success(path):
        # Load configuration
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f)
    case Failure(err):
        print(f"Invalid config: {err}")
```

### Output Directory Validation

```python
def validate_output_directory(path_str: str) -> Maybe[Path]:
    """Validate output directory: exists, is directory, writable."""
    return (
        parsers.parse_path(path_str, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_dir())
        .bind(validators.is_writable())
    )

# Usage
match validate_output_directory("/tmp/output"):
    case Success(path):
        output_file = path / "results.txt"
        output_file.write_text("data")
    case Failure(err):
        print(f"Cannot write to directory: {err}")
```

### Image File Validation

```python
def validate_image(path_str: str) -> Maybe[Path]:
    """Validate image files: exists, readable, correct extension, under 5MB."""
    return (
        parsers.parse_path(path_str)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_readable())
        .bind(validators.has_extension(['.jpg', '.jpeg', '.png', '.gif']))
        .bind(validators.max_size(5 * 1024 * 1024))
    )

# Usage in web framework
from flask import request

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    match validate_image(temp_path):
        case Success(path):
            # Process image
            return {"status": "success"}
        case Failure(err):
            return {"status": "error", "message": err}, 400
```

### Executable Validation

```python
def validate_executable(path_str: str) -> Maybe[Path]:
    """Validate executable: exists, is file, executable, not too large."""
    return (
        parsers.parse_path(path_str, resolve=True)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.is_executable())
        .bind(validators.max_size(100 * 1024 * 1024))  # 100MB max
    )

# Usage
match validate_executable("/usr/local/bin/custom-tool"):
    case Success(path):
        import subprocess
        subprocess.run([str(path)], check=True)
    case Failure(err):
        print(f"Cannot execute: {err}")
```

## Security Considerations

### DoS Protection

The `parse_path` function includes DoS protection:

```python
# Rejects excessively long paths (> 10KB) in < 10ms
malicious_path = "a/" * 5000  # 10KB path string
result = parsers.parse_path(malicious_path)
# Returns Failure("Invalid format: path is too long") immediately
```

### Input Validation Best Practices

1. **Validate at boundaries**: Parse and validate user input immediately
2. **Defense in depth**: Combine framework, application, and parser validation
3. **Whitelist extensions**: Use `has_extension()` instead of blacklists
4. **Check permissions**: Verify `is_readable()`/`is_writable()` before file operations
5. **Limit file sizes**: Use `max_size()` to prevent resource exhaustion

### Framework Integration Example

```python
from flask import Flask, request
from valid8r import parsers, validators

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Framework limit: 10MB

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return {"error": "No file provided"}, 400

    # Application-level validation
    if len(file.filename) > 255:
        return {"error": "Filename too long"}, 400

    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    # Parser-level validation (defense in depth)
    result = (
        parsers.parse_path(temp_path)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.has_extension(['.pdf', '.docx']))
        .bind(validators.max_size(10 * 1024 * 1024))
    )

    match result:
        case Success(path):
            # Process validated file
            return {"status": "success"}
        case Failure(err):
            return {"error": err}, 400
```

## Error Messages

Filesystem validators provide clear, actionable error messages:

```python
# Path does not exist
parsers.parse_path("/nonexistent").bind(validators.exists())
# Failure("Path does not exist: /nonexistent")

# Not a file
parsers.parse_path("/etc").bind(validators.is_file())
# Failure("Path is not a file: /etc")

# Not readable
parsers.parse_path("/root/secret").bind(validators.is_readable())
# Failure("Path is not readable: /root/secret")

# File too large
parsers.parse_path("large.bin").bind(validators.max_size(1024))
# Failure("File size (2048 bytes) exceeds maximum size (1024 bytes): large.bin")

# Wrong extension
parsers.parse_path("file.txt").bind(validators.has_extension(['.pdf']))
# Failure("File must have one of these extensions: .pdf (got: .txt)")
```

## Testing

Use Valid8r's testing utilities to test filesystem validation:

```python
from valid8r.testing import assert_maybe_success, assert_maybe_failure
import pytest
from pathlib import Path

def test_parse_existing_file(tmp_path: Path):
    """Test parsing an existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = parsers.parse_path(str(test_file)).bind(validators.exists())
    assert assert_maybe_success(result, test_file)

def test_reject_missing_file(tmp_path: Path):
    """Test rejection of missing file."""
    missing = tmp_path / "missing.txt"

    result = parsers.parse_path(str(missing)).bind(validators.exists())
    assert assert_maybe_failure(result, "does not exist")

def test_validate_file_size(tmp_path: Path):
    """Test file size validation."""
    test_file = tmp_path / "large.bin"
    test_file.write_bytes(b"x" * 2000)

    result = (
        parsers.parse_path(str(test_file))
        .bind(validators.exists())
        .bind(validators.max_size(1000))
    )
    assert assert_maybe_failure(result, "exceeds maximum size")
```

## Performance

All filesystem validators are designed for efficiency:

- **Path parsing**: < 1ms for normal paths, < 10ms for malicious inputs
- **File existence checks**: Single `Path.exists()` call
- **Size validation**: Single `Path.stat()` call
- **Permission checks**: Single `os.access()` call

## See Also

- [Validators Guide](../user_guide/validators.md) - General validator documentation
- [Combinators Guide](../user_guide/combinators.md) - Combining validators
- [Testing Guide](../user_guide/testing.md) - Testing filesystem validation
- [Security Guide](../security/dos-protection.md) - DoS protection details
