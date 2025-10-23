# Valid8r

[![PyPI version](https://img.shields.io/pypi/v/valid8r.svg)](https://pypi.org/project/valid8r/)
[![Python versions](https://img.shields.io/pypi/pyversions/valid8r.svg)](https://pypi.org/project/valid8r/)
[![License](https://img.shields.io/github/license/mikelane/valid8r.svg)](https://github.com/mikelane/valid8r/blob/main/LICENSE)
[![CI Status](https://img.shields.io/github/actions/workflow/status/mikelane/valid8r/ci.yml?branch=main)](https://github.com/mikelane/valid8r/actions)
[![codecov](https://codecov.io/gh/mikelane/valid8r/branch/main/graph/badge.svg)](https://codecov.io/gh/mikelane/valid8r)
[![Documentation](https://img.shields.io/readthedocs/valid8r.svg)](https://valid8r.readthedocs.io/)

[![PyPI downloads](https://img.shields.io/pypi/dm/valid8r.svg)](https://pypi.org/project/valid8r/)
[![GitHub stars](https://img.shields.io/github/stars/mikelane/valid8r.svg)](https://github.com/mikelane/valid8r/stargazers)
[![GitHub contributors](https://img.shields.io/github/contributors/mikelane/valid8r.svg)](https://github.com/mikelane/valid8r/graphs/contributors)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Semantic Release](https://img.shields.io/badge/semantic--release-python-blue)](https://github.com/python-semantic-release/python-semantic-release)

A clean, flexible input validation library for Python applications.

## Features

- **Clean Type Parsing**: Parse strings to various Python types with robust error handling
- **Flexible Validation**: Chain validators and create custom validation rules
- **Monadic Error Handling**: Use Maybe monad for clean error propagation
- **Input Prompting**: Prompt users for input with built-in validation
- **Structured Results**: Network parsers return rich dataclasses with parsed components

## Available Parsers

### Basic Types
- **Numbers**: `parse_int`, `parse_float`, `parse_complex`, `parse_decimal`
- **Text**: `parse_bool` (flexible true/false parsing)
- **Dates**: `parse_date` (ISO 8601 format)
- **UUIDs**: `parse_uuid` (with optional version validation)

### Collections
- **Lists**: `parse_list` (with element parser)
- **Dictionaries**: `parse_dict` (with key/value parsers)
- **Sets**: `parse_set` (with element parser)

### Network & Communication
- **IP Addresses**: `parse_ipv4`, `parse_ipv6`, `parse_ip` (either v4 or v6)
- **Networks**: `parse_cidr` (IPv4/IPv6 CIDR notation)
- **Phone Numbers**: `parse_phone` → PhoneNumber (NANP validation)
- **URLs**: `parse_url` → UrlParts (scheme, host, port, path, query, etc.)
- **Email**: `parse_email` → EmailAddress (normalized case)

### Advanced
- **Enums**: `parse_enum` (type-safe enum parsing)
- **Custom**: `create_parser`, `make_parser`, `validated_parser` (parser factories)

## Installation

**Requirements**: Python 3.11 or higher

```bash
pip install valid8r
```

Valid8r supports Python 3.11, 3.12, 3.13, and 3.14.

## Quick Start

```python
from valid8r import (
    parsers,
    prompt,
    validators,
)

# Simple validation
age = prompt.ask(
    "Enter your age: ",
    parser=parsers.parse_int,
    validator=validators.minimum(0) & validators.maximum(120)
)

print(f"Your age is {age}")
```

### IP parsing helpers

```python
from valid8r.core.maybe import Success, Failure
from valid8r.core import parsers

# IPv4 / IPv6 / generic IP
for text in ["192.168.0.1", "::1", " 10.0.0.1 "]:
    match parsers.parse_ip(text):
        case Success(addr):
            print("Parsed:", addr)
        case Failure(err):
            print("Error:", err)

# CIDR (strict by default)
match parsers.parse_cidr("10.0.0.0/8"):
    case Success(net):
        print("Network:", net)  # 10.0.0.0/8
    case Failure(err):
        print("Error:", err)

# Non-strict masks host bits
match parsers.parse_cidr("10.0.0.1/24", strict=False):
    case Success(net):
        assert str(net) == "10.0.0.0/24"
```

### URL and Email helpers

```python
from valid8r.core.maybe import Success, Failure
from valid8r.core import parsers

# URL parsing with structured result (UrlParts)
match parsers.parse_url("https://alice:pw@example.com:8443/x?q=1#top"):
    case Success(u):
        print(f"Scheme: {u.scheme}")     # https
        print(f"Host: {u.host}")         # example.com
        print(f"Port: {u.port}")         # 8443
        print(f"Path: {u.path}")         # /x
        print(f"Query: {u.query}")       # {'q': '1'}
        print(f"Fragment: {u.fragment}") # top
    case Failure(err):
        print("Error:", err)

# Email parsing with normalized case (EmailAddress)
match parsers.parse_email("First.Last+tag@Example.COM"):
    case Success(e):
        print(f"Local: {e.local}")   # First.Last+tag
        print(f"Domain: {e.domain}") # example.com (normalized)
    case Failure(err):
        print("Error:", err)
```

### Phone Number Parsing

```python
from valid8r.core.maybe import Success, Failure
from valid8r.core import parsers

# Phone number parsing with NANP validation (PhoneNumber)
match parsers.parse_phone("+1 (555) 123-4567"):
    case Success(phone):
        print(f"Country: {phone.country_code}")  # 1
        print(f"Area: {phone.area_code}")        # 555
        print(f"Exchange: {phone.exchange}")     # 123
        print(f"Subscriber: {phone.subscriber}") # 4567

        # Format for display using properties
        print(f"E.164: {phone.e164}")           # +15551234567
        print(f"National: {phone.national}")    # (555) 123-4567
    case Failure(err):
        print("Error:", err)

# Also accepts various formats
for number in ["5551234567", "(555) 123-4567", "555-123-4567"]:
    result = parsers.parse_phone(number)
    assert result.is_success()
```

## Testing Support

Valid8r includes comprehensive testing utilities to help you verify your validation logic:

```python
from valid8r import Maybe, validators, parsers, prompt
from valid8r.testing import (
    MockInputContext,
    assert_maybe_success,
    assert_maybe_failure,
)

def validate_age(age: int) -> Maybe[int]:
    """Validate age is between 0 and 120."""
    return (validators.minimum(0) & validators.maximum(120))(age)

# Test validation functions with assert helpers
result = validate_age(42)
assert assert_maybe_success(result, 42)

result = validate_age(-5)
assert assert_maybe_failure(result, "at least 0")

# Test prompts with mock input
with MockInputContext(["yes", "42", "invalid", "25"]):
    # First prompt
    result = prompt.ask("Continue? ", parser=parsers.parse_bool)
    assert result.value_or(False) == True

    # Second prompt
    age = prompt.ask(
        "Age? ",
        parser=parsers.parse_int,
        validator=validate_age
    )
    assert age == 42

    # Third prompt will fail, fourth succeeds
    age = prompt.ask(
        "Age again? ",
        parser=parsers.parse_int,
        retries=1  # Retry once after failure
    )
    assert age == 25
```

### Testing Utilities Reference

- **`assert_maybe_success(result, expected_value)`**: Assert that a Maybe is Success with the expected value
- **`assert_maybe_failure(result, error_substring)`**: Assert that a Maybe is Failure containing the error substring
- **`MockInputContext(inputs)`**: Context manager for mocking user input in tests

For more examples, see the [documentation](https://valid8r.readthedocs.io/).

## Development

This project uses Poetry for dependency management and Tox for testing.

### Setup

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### Running Tests

```bash
# Run all tests
poetry run tox

# Run BDD tests
poetry run tox -e bdd
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Mike Lane
