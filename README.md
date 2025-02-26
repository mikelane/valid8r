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
    parser=parsers.int_parser,
    validator=validators.minimum(0) & validators.maximum(120)
)

print(f"Your age is {age}")
```

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
