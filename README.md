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
from valid8r import parsers, validators, prompt

# Simple validation
age = prompt.ask(
    "Enter your age: ",
    parser=parsers.parse_int,
    validator=validators.minimum(0) & validators.maximum(120)
)

print(f"Your age is {age}")
```

## Testing Support

Valid8r includes testing utilities to help you verify your validation logic:

```python
from valid8r.testing import MockInputContext, assert_maybe_success

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
