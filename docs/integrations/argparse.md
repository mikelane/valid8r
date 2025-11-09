# argparse Integration

Valid8r provides seamless integration with Python's standard library `argparse` module through the `type_from_parser` function. This allows you to use valid8r's rich validation ecosystem for robust CLI argument validation with helpful error messages.

## Why Integrate valid8r with argparse?

Python's `argparse` module is the standard library solution for creating command-line interfaces. While it provides basic type conversion (int, float, etc.), complex validation requires custom logic. Valid8r bridges this gap by providing:

- **Type-safe parsing** with structured result types (EmailAddress, PhoneNumber, UUID, etc.)
- **Composable validators** for complex validation rules
- **Helpful error messages** that guide users to correct input
- **Reusable validation logic** shared across CLI, web, and prompt interfaces
- **Zero external dependencies** (argparse is in the standard library)

## Installation

No additional dependencies required! argparse is part of Python's standard library.

```bash
pip install valid8r
```

## Quick Start

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--email',
    type=type_from_parser(parsers.parse_email),
    help='Email address'
)

args = parser.parse_args()
print(f"Email: {args.email.local}@{args.email.domain}")
```

## API Reference

### `type_from_parser(parser)`

Convert a valid8r parser into an argparse-compatible type function.

**Parameters:**
- `parser` (Callable[[str | None], Maybe[T]]): A valid8r parser function that takes a string and returns `Maybe[T]`

**Returns:**
- `Callable[[str], T]`: A function suitable for use with argparse's `type` parameter

**Behavior:**
- On success: Returns the parsed value (extracted from `Success[T]`)
- On failure: Raises `ValueError` with the error message (extracted from `Failure`)

**Example:**
```python
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

email_type = type_from_parser(parsers.parse_email)
email = email_type('alice@example.com')  # Returns EmailAddress
# email_type('bad-email')  # Raises ValueError
```

## Common Patterns

### Email Validation

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--email',
    type=type_from_parser(parsers.parse_email),
    required=True,
    help='Email address (validated format)'
)

args = parser.parse_args()
# args.email is an EmailAddress with .local and .domain attributes
print(f"User: {args.email.local}, Domain: {args.email.domain}")
```

**Example usage:**
```bash
$ python app.py --email alice@example.com
User: alice, Domain: example.com

$ python app.py --email bad-email
usage: app.py [-h] --email EMAIL
app.py: error: argument --email: invalid argparse_type value: 'bad-email'
```

### Port Number Validation

Combine `parse_int` with range validators for sophisticated validation:

```python
import argparse
from valid8r.core import parsers, validators
from valid8r.core.maybe import Maybe
from valid8r.integrations.argparse import type_from_parser

def port_parser(text: str | None) -> Maybe[int]:
    """Parse and validate a port number (1-65535)."""
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

parser = argparse.ArgumentParser()
parser.add_argument(
    '--port',
    type=type_from_parser(port_parser),
    default=8080,
    help='Port number (1-65535)'
)

args = parser.parse_args()
print(f"Starting server on port {args.port}")
```

**Example usage:**
```bash
$ python app.py --port 3000
Starting server on port 3000

$ python app.py --port 70000
usage: app.py [-h] [--port PORT]
app.py: error: argument --port: invalid argparse_type value: '70000'
```

### UUID Validation

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--id',
    type=type_from_parser(parsers.parse_uuid),
    help='Resource UUID'
)

args = parser.parse_args()
if args.id:
    print(f"Resource ID: {args.id}")
```

**Example usage:**
```bash
$ python app.py --id 550e8400-e29b-41d4-a716-446655440000
Resource ID: 550e8400-e29b-41d4-a716-446655440000

$ python app.py --id not-a-uuid
usage: app.py [-h] [--id ID]
app.py: error: argument --id: invalid argparse_type value: 'not-a-uuid'
```

### Phone Number Validation

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--phone',
    type=type_from_parser(parsers.parse_phone),
    help='Phone number (US format)'
)

args = parser.parse_args()
if args.phone:
    formatted = f"({args.phone.area_code}) {args.phone.exchange}-{args.phone.subscriber}"
    print(f"Phone: {formatted}")
```

**Example usage:**
```bash
$ python app.py --phone "(212) 456-7890"
Phone: (212) 456-7890

$ python app.py --phone "123"
usage: app.py [-h] [--phone PHONE]
app.py: error: argument --phone: invalid argparse_type value: '123'
```

### Boolean Flags

Use `parse_bool` for flexible boolean parsing (accepts true/false, yes/no, 1/0):

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--debug',
    type=type_from_parser(parsers.parse_bool),
    default=False,
    help='Enable debug mode (true/false, yes/no, 1/0)'
)

args = parser.parse_args()
print(f"Debug mode: {'enabled' if args.debug else 'disabled'}")
```

**Example usage:**
```bash
$ python app.py --debug yes
Debug mode: enabled

$ python app.py --debug false
Debug mode: disabled

$ python app.py --debug maybe
usage: app.py [-h] [--debug DEBUG]
app.py: error: argument --debug: invalid argparse_type value: 'maybe'
```

### Multiple Validators

Chain multiple validators for complex business rules:

```python
import argparse
from valid8r.core import parsers, validators
from valid8r.core.maybe import Maybe
from valid8r.integrations.argparse import type_from_parser

def percentage_parser(text: str | None) -> Maybe[int]:
    """Parse a percentage value (0-100)."""
    return parsers.parse_int(text).bind(
        validators.minimum(0) & validators.maximum(100)
    )

parser = argparse.ArgumentParser()
parser.add_argument(
    '--discount',
    type=type_from_parser(percentage_parser),
    help='Discount percentage (0-100)'
)

args = parser.parse_args()
if args.discount:
    print(f"Applying {args.discount}% discount")
```

### Positional Arguments

Works seamlessly with positional arguments:

```python
import argparse
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

parser = argparse.ArgumentParser()
parser.add_argument(
    'email',
    type=type_from_parser(parsers.parse_email),
    help='Email address'
)
parser.add_argument(
    'port',
    type=type_from_parser(parsers.parse_int),
    help='Port number'
)

args = parser.parse_args()
print(f"Email: {args.email.local}@{args.email.domain}")
print(f"Port: {args.port}")
```

**Example usage:**
```bash
$ python app.py alice@example.com 8080
Email: alice@example.com
Port: 8080
```

## Complete Working Example

See [`examples/argparse_example.py`](../../examples/argparse_example.py) for a complete working example demonstrating:

- Email validation with structured results
- Port validation with range validators
- Optional UUID validation
- Optional phone number validation
- Boolean flag parsing
- Helpful error messages for all validation failures

Run the example:

```bash
python examples/argparse_example.py --help
python examples/argparse_example.py --email alice@example.com --port 8080
python examples/argparse_example.py --email alice@example.com --port 8080 --uuid 550e8400-e29b-41d4-a716-446655440000
```

## Comparison to Native argparse Types

### Native argparse

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, help='Port number')

args = parser.parse_args()
# args.port is an int, but no range validation
# Must add custom validation logic:
if args.port < 1 or args.port > 65535:
    parser.error("Port must be between 1 and 65535")
```

### With valid8r

```python
import argparse
from valid8r.core import parsers, validators
from valid8r.core.maybe import Maybe
from valid8r.integrations.argparse import type_from_parser

def port_parser(text: str | None) -> Maybe[int]:
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=type_from_parser(port_parser))

args = parser.parse_args()
# args.port is guaranteed to be in range (1-65535)
# No additional validation needed
```

## Error Handling Behavior

When validation fails, `type_from_parser` raises `ValueError` with the error message from the valid8r parser. argparse automatically catches this and displays a helpful error message to the user.

**Error message format:**
```
usage: script.py [-h] --email EMAIL
script.py: error: argument --email: invalid argparse_type value: 'bad-input'
```

The error message after "invalid argparse_type value:" is the error message from the valid8r parser, providing context-specific validation feedback.

## Best Practices

### 1. Create Reusable Parser Functions

Define common parsers once and reuse them across your application:

```python
# validators.py
from valid8r.core import parsers, validators
from valid8r.core.maybe import Maybe

def port_parser(text: str | None) -> Maybe[int]:
    """Parse a network port (1-65535)."""
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

def percentage_parser(text: str | None) -> Maybe[int]:
    """Parse a percentage (0-100)."""
    return parsers.parse_int(text).bind(
        validators.minimum(0) & validators.maximum(100)
    )

# cli.py
from valid8r.integrations.argparse import type_from_parser
from . import validators

parser.add_argument('--port', type=type_from_parser(validators.port_parser))
parser.add_argument('--discount', type=type_from_parser(validators.percentage_parser))
```

### 2. Use Descriptive Help Messages

Combine argparse's `help` parameter with valid8r's validation for self-documenting CLIs:

```python
parser.add_argument(
    '--port',
    type=type_from_parser(port_parser),
    help='Port number (1-65535)',
    metavar='PORT'
)
```

### 3. Provide Sensible Defaults

Use argparse's `default` parameter for optional arguments:

```python
parser.add_argument(
    '--port',
    type=type_from_parser(port_parser),
    default=8080,
    help='Port number (default: 8080)'
)
```

### 4. Use metavar for Cleaner Help Output

Use `metavar` to control how argument names appear in help text:

```python
parser.add_argument(
    '--email',
    type=type_from_parser(parsers.parse_email),
    help='Email address',
    metavar='EMAIL'  # Shows "--email EMAIL" instead of "--email PARSE_EMAIL"
)
```

### 5. Share Parsers Across Interfaces

Use the same parser functions across CLI, web, and interactive prompts:

```python
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser
from valid8r.integrations.pydantic import validator_from_parser

# CLI
parser.add_argument('--email', type=type_from_parser(parsers.parse_email))

# Pydantic model
class User(BaseModel):
    email: str
    _validate_email = validator_from_parser(parsers.parse_email)

# Interactive prompt
from valid8r.prompt import ask
email = ask("Enter email:", parser=parsers.parse_email)
```

## Advanced Usage

### Custom Error Messages

Wrap parsers to provide custom error messages:

```python
from valid8r.core.maybe import Maybe, Failure
from valid8r.core import parsers

def email_parser_with_hint(text: str | None) -> Maybe:
    result = parsers.parse_email(text)
    match result:
        case Failure(err):
            return Failure(f"{err}. Example: user@example.com")
        case _:
            return result

parser.add_argument(
    '--email',
    type=type_from_parser(email_parser_with_hint)
)
```

### Conditional Validation

Combine multiple validation strategies:

```python
def smart_port_parser(text: str | None) -> Maybe[int]:
    """Parse port with conditional validation."""
    result = parsers.parse_int(text)
    match result:
        case Success(port):
            if port < 1024:
                # Warn about privileged ports
                return parsers.parse_int(text).bind(
                    validators.minimum(1) & validators.maximum(65535)
                )
            else:
                return result
        case _:
            return result
```

## Integration with Other valid8r Features

### With Pydantic Models

Share validation logic between CLI and data models:

```python
from pydantic import BaseModel
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser
from valid8r.integrations.pydantic import validator_from_parser

# Define validation once
email_parser = parsers.parse_email

# Use in Pydantic
class User(BaseModel):
    email: str
    _validate_email = validator_from_parser(email_parser)

# Use in argparse
parser.add_argument('--email', type=type_from_parser(email_parser))
```

### With Environment Variables

Use the same parsers for CLI args and environment variables:

```python
import os
from valid8r.core import parsers
from valid8r.integrations.argparse import type_from_parser

# From CLI
parser.add_argument('--port', type=type_from_parser(parsers.parse_int))

# From environment
port_str = os.getenv('PORT', '8080')
port_result = parsers.parse_int(port_str)
match port_result:
    case Success(port):
        print(f"Using port {port}")
    case Failure(err):
        print(f"Invalid PORT env var: {err}")
```

## Troubleshooting

### Error: "invalid argparse_type value"

This is argparse's standard error message when a type function raises `ValueError` or `TypeError`. The error message from valid8r appears after this prefix.

**Solution:** The validation failed. Check the error message after "invalid argparse_type value:" for details.

### Type Hints Not Working

Ensure you're using Python 3.10+ for proper type hint support with the Maybe monad.

### Import Errors

Ensure valid8r is installed:
```bash
pip install valid8r
```

## Performance Considerations

- **argparse is fast:** Type conversion happens once during parsing, not on every access
- **Validation is early:** Invalid arguments are caught before your application logic runs
- **No overhead:** valid8r parsers are simple functions with minimal overhead

## Migration Guide

### From Manual Validation

**Before:**
```python
parser.add_argument('--port', type=int)
args = parser.parse_args()
if args.port < 1 or args.port > 65535:
    parser.error("Invalid port")
```

**After:**
```python
from valid8r.integrations.argparse import type_from_parser
from valid8r.core import parsers, validators

def port_parser(text):
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

parser.add_argument('--port', type=type_from_parser(port_parser))
args = parser.parse_args()
# args.port is guaranteed valid
```

### From Custom Type Functions

**Before:**
```python
def email_type(value):
    if '@' not in value:
        raise ValueError("Invalid email")
    return value

parser.add_argument('--email', type=email_type)
```

**After:**
```python
from valid8r.integrations.argparse import type_from_parser
from valid8r.core import parsers

parser.add_argument('--email', type=type_from_parser(parsers.parse_email))
# Returns EmailAddress with .local and .domain attributes
```

## Related Documentation

- [Core Parsers](../parsers.md) - Available validation functions
- [Validators](../validators.md) - Composable validation combinators
- [Pydantic Integration](./pydantic.md) - Validate Pydantic models
- [Click Integration](./click.md) - Build Click CLIs with valid8r
- [Typer Integration](./typer.md) - Build Typer CLIs with valid8r

## Contributing

Found a bug or have a feature request? Please [open an issue](https://github.com/mikelane/valid8r/issues).
