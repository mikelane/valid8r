# Valid8r

A clean, flexible input validation library for Python applications.

## Features

- **Clean Type Parsing**: Parse strings to various Python types with robust error handling
- **Flexible Validation**: Chain validators and create custom validation rules
- **Monadic Error Handling**: Use Maybe monad for clean error propagation
- **Input Prompting**: Prompt users for input with built-in validation

## Installation

```bash
pip install valid8r
```

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

# URL parsing
match parsers.parse_url("https://alice:pw@example.com:8443/x?q=1#top"):
    case Success(u):
        print(u.scheme, u.username, u.password, u.host, u.port)
    case Failure(err):
        print("Error:", err)

# Email parsing
match parsers.parse_email("First.Last+tag@Example.COM"):
    case Success(e):
        print(e.local, e.domain)  # First.Last+tag example.com
    case Failure(err):
        print("Error:", err)
```

## Testing Support

Valid8r includes testing utilities to help you verify your validation logic:

```python
from valid8r import (
    Maybe,
    validators,
    parsers,
    prompt,
)

from valid8r.testing import (
    MockInputContext,
    assert_maybe_success,
)

def validate_age(age: int) -> Maybe[int]:
    return validators.minimum(0) & validators.maximum(120)(age)

# Test prompts with mock input
with MockInputContext(["yes"]):
    result = prompt.ask("Continue? ", parser=parsers.parse_bool)
    assert result.is_success()
    assert result.value_or(False) == True

# Test validation functions
result = validate_age(42)
assert assert_maybe_success(result, 42)
```

For more information, see the [Testing with Valid8r](docs/user_guide/testing.rst) guide.

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
MIT
