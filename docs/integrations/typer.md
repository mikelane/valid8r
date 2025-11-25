# Typer Integration

The `valid8r.integrations.typer` module provides seamless integration between valid8r parsers and [Typer](https://typer.tiangolo.com/), a modern CLI framework built on top of Click.

## Overview

Valid8r offers multiple integration patterns for Typer applications:

1. **validator_callback()** - Simple, inline validation for options and arguments (recommended)
2. **ValidatedType** - Reusable custom types for use across multiple commands
3. **validated_prompt()** - Interactive prompts with validation and retry logic
4. **TyperParser** - Lower-level Click ParamType adapter (advanced use)

These patterns enable rich validation of CLI arguments using the same parsers you use throughout your application (FastAPI, Pydantic, environment variables, etc.).

## Installation

Typer must be installed separately:

```bash
uv add typer
# or
pip install typer
```

## Quick Start: Three Integration Patterns

### Pattern 1: validator_callback() (Recommended)

Best for simple, inline validation. Creates a callback function that validates using a valid8r parser:

```python
import typer
from typing_extensions import Annotated
from valid8r.core import parsers, validators
from valid8r.integrations.typer import validator_callback

app = typer.Typer()

# Create validation callbacks
email_callback = validator_callback(parsers.parse_email)
port_callback = validator_callback(
    lambda t: parsers.parse_int(t).bind(
        validators.minimum(1) & validators.maximum(65535)
    )
)

@app.command()
def deploy(
    email: Annotated[str, typer.Option(callback=email_callback)],
    port: Annotated[int, typer.Option(callback=port_callback)] = 8080,
) -> None:
    """Deploy service with validated email and port."""
    print(f"Deploying to {email.local}@{email.domain} on port {port}")

if __name__ == "__main__":
    app()
```

**When to use:** Simple validation, single-use validators, inline validation needs.

### Pattern 2: ValidatedType (Reusable Types)

Best for custom types used across multiple commands:

```python
import typer
from typing_extensions import Annotated
from valid8r.core import parsers
from valid8r.integrations.typer import ValidatedType

app = typer.Typer()

# Create reusable custom types
Email = ValidatedType(parsers.parse_email)
Phone = ValidatedType(parsers.parse_phone)

@app.command()
def contact(
    email: Annotated[str, typer.Option(click_type=Email)],
    phone: Annotated[str, typer.Option(click_type=Phone)] | None = None,
) -> None:
    """Store contact information."""
    print(f"Email: {email.local}@{email.domain}")
    if phone:
        print(f"Phone: {phone.area_code}-{phone.exchange}-{phone.subscriber}")

if __name__ == "__main__":
    app()
```

**When to use:** Types used in multiple commands, cleaner API surface, type documentation.

### Pattern 3: validated_prompt() (Interactive Mode)

Best for interactive CLIs with retry logic:

```python
import typer
from valid8r.core import parsers
from valid8r.integrations.typer import validated_prompt

app = typer.Typer()

@app.command()
def configure() -> None:
    """Interactive configuration wizard."""
    email = validated_prompt(
        'Enter your email',
        parser=parsers.parse_email,
        max_retries=3
    )
    print(f"Email configured: {email.local}@{email.domain}")

if __name__ == "__main__":
    app()
```

**When to use:** Interactive workflows, configuration wizards, onboarding flows.

## Basic Usage (TyperParser)

```python
import typer
from typing_extensions import Annotated
from valid8r.core import parsers
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

@app.command()
def create_user(
    email: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_email))],
    phone: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_phone))],
) -> None:
    """Create a new user with validated email and phone."""
    print(f"Creating user: {email.local}@{email.domain}")
    print(f"Phone: {phone.area_code}-{phone.exchange}-{phone.subscriber}")

if __name__ == "__main__":
    app()
```

### Running the CLI

```bash
$ python cli.py --email alice@example.com --phone "(212) 456-7890"
Creating user: alice@example.com
Phone: 212-456-7890

$ python cli.py --email invalid
Usage: cli.py [OPTIONS]
Try 'cli.py --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--email': An email address must have an @-sign.           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Features

### Chained Validators

Combine parsers with validators for complex validation rules:

```python
import typer
from typing_extensions import Annotated
from valid8r.core import parsers, validators
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

# Create a port parser with validation
def port_parser(text: str | None):
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

@app.command()
def start_server(
    port: Annotated[int, typer.Option(parser=TyperParser(port_parser))],
) -> None:
    """Start server on the specified port."""
    print(f"Starting server on port {port}")

if __name__ == "__main__":
    app()
```

```bash
$ python server.py --port 8080
Starting server on port 8080

$ python server.py --port 70000
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--port': Must be at most 65535.                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Custom Error Prefixes

Add custom prefixes to error messages for clarity:

```python
@app.command()
def register(
    email: Annotated[
        str,
        typer.Option(
            parser=TyperParser(
                parsers.parse_email,
                error_prefix="Email address"
            )
        )
    ],
) -> None:
    """Register a new user."""
    print(f"Registered: {email.local}@{email.domain}")
```

```bash
$ python register.py --email bad
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--email': Email address: An email address must have an    │
│ @-sign.                                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Custom Type Names

Customize the type name shown in help text:

```python
@app.command()
def connect(
    port: Annotated[
        int,
        typer.Option(
            parser=TyperParser(parsers.parse_int, name="port_number")
        )
    ],
) -> None:
    """Connect to a server."""
    print(f"Connecting on port {port}")
```

```bash
$ python connect.py --help
Usage: connect.py [OPTIONS]

  Connect to a server.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --port        PORT_NUMBER  [required]                                     │
│    --help                     Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Arguments (Positional Parameters)

TyperParser works with both Options and Arguments:

```python
import uuid
import typer
from typing_extensions import Annotated
from valid8r.core import parsers
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

@app.command()
def get_user(
    user_id: Annotated[uuid.UUID, typer.Argument(parser=TyperParser(parsers.parse_uuid))],
) -> None:
    """Get user by UUID."""
    print(f"Fetching user: {user_id}")

if __name__ == "__main__":
    app()
```

```bash
$ python get_user.py 550e8400-e29b-41d4-a716-446655440000
Fetching user: 550e8400-e29b-41d4-a716-446655440000

$ python get_user.py not-a-uuid
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for 'USER_ID': Invalid UUID format.                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Available Parsers

All valid8r parsers work with TyperParser:

### Basic Types
- `parse_int`, `parse_float`, `parse_bool`
- `parse_date`, `parse_complex`, `parse_decimal`

### Collections
- `parse_list`, `parse_dict`, `parse_set`

### Network
- `parse_ipv4`, `parse_ipv6`, `parse_ip`
- `parse_cidr`, `parse_url`, `parse_email`

### Communication
- `parse_phone` (North American Number Plan)

### Advanced
- `parse_enum`, `parse_uuid`

### Validated Parsers
- `parse_int_with_validation`
- `parse_list_with_validation`
- `parse_dict_with_validation`

## Structured Result Types

Many parsers return structured types with named fields:

```python
import typer
from typing_extensions import Annotated
from valid8r.core import parsers
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

@app.command()
def analyze_url(
    url: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_url))],
) -> None:
    """Analyze a URL's components."""
    print(f"Scheme: {url.scheme}")
    print(f"Host: {url.host}")
    print(f"Port: {url.port}")
    print(f"Path: {url.path}")
    if url.query:
        print(f"Query: {url.query}")

if __name__ == "__main__":
    app()
```

```bash
$ python analyze_url.py --url "https://example.com:8080/path?key=value"
Scheme: https
Host: example.com
Port: 8080
Path: /path
Query: key=value
```

## Detailed Pattern Guide

### validator_callback() - Simple and Powerful

The `validator_callback()` function creates a Typer-compatible callback from any valid8r parser:

```python
from valid8r.integrations.typer import validator_callback
from valid8r.core import parsers, validators

# Simple parser
email_callback = validator_callback(parsers.parse_email)

# With custom error prefix
port_callback = validator_callback(
    lambda t: parsers.parse_int(t).bind(
        validators.minimum(1) & validators.maximum(65535)
    ),
    error_prefix="Port"
)

# Using in command
@app.command()
def my_command(
    email: str = typer.Option(..., callback=email_callback),
    port: int = typer.Option(8080, callback=port_callback)
) -> None:
    # Parameters are validated and converted
    pass
```

**Advantages:**
- Simple and straightforward
- Works with Typer's native callback parameter
- Custom error prefixes for clarity
- No special imports needed in function signatures

**Error Output:**
```bash
$ cli --port 99999
Error: Invalid parameter value for '--port': Port: Must be at most 65535.
```

### ValidatedType - Reusable Custom Types

Create custom types once, use them everywhere:

```python
from valid8r.integrations.typer import ValidatedType
from valid8r.core import parsers, validators

# Define reusable types
Email = ValidatedType(parsers.parse_email)
Port = ValidatedType(
    lambda t: parsers.parse_int(t).bind(
        validators.minimum(1) & validators.maximum(65535)
    ),
    name="port",
    help_text="Valid port number (1-65535)"
)

# Use with click_type parameter
@app.command()
def deploy(
    email: str = typer.Option(..., click_type=Email),
    port: int = typer.Option(8080, click_type=Port)
) -> None:
    pass

@app.command()
def notify(
    admin_email: str = typer.Option(..., click_type=Email),
    backup_email: str = typer.Option(..., click_type=Email)
) -> None:
    # Reuse Email type across multiple parameters and commands
    pass
```

**Advantages:**
- Define once, use everywhere
- Cleaner codebase with named types
- Better documentation
- Type reuse across multiple commands

**When to use ValidatedType vs validator_callback:**
- Use `ValidatedType` for types used in 3+ places
- Use `validator_callback()` for one-off validations
- Use `ValidatedType` when you want named types in documentation

### validated_prompt() - Interactive Workflows

Interactive prompts with validation and automatic retry:

```python
from valid8r.integrations.typer import validated_prompt
from valid8r.core import parsers, validators

@app.command()
def configure() -> None:
    """Interactive configuration wizard."""

    # Basic prompt with validation
    email = validated_prompt(
        "Enter your email",
        parser=parsers.parse_email,
        max_retries=3
    )

    # With custom validators
    port = validated_prompt(
        "Enter server port",
        parser=lambda t: parsers.parse_int(t).bind(
            validators.minimum(1) & validators.maximum(65535)
        ),
        max_retries=5
    )

    # Prompt shows errors and retries automatically
    print(f"Configured: {email.local}@{email.domain} on port {port}")
```

**Interactive Session:**
```bash
$ cli configure
Enter your email: not-an-email
Error: An email address must have an @-sign.
Enter your email: alice@
Error: An email address must have a domain.
Enter your email: alice@example.com
Enter server port: 99999
Error: Must be at most 65535.
Enter server port: 8080
Configured: alice@example.com on port 8080
```

**Advantages:**
- Built-in retry logic
- User-friendly error messages
- Reduces boilerplate for interactive CLIs
- Works with any valid8r parser

**Options:**
- `max_retries`: Number of retry attempts (default: 10)
- `typer_style`: Use Typer's styled output (default: False)

## How It Works

### validator_callback()

Creates a callback function that:
1. Calls the valid8r parser on the input
2. Returns the validated value on success
3. Raises `typer.BadParameter` on failure

The callback integrates seamlessly with Typer's Option() and Argument() callback parameter.

### ValidatedType

Returns a Click ParamType (TyperParser) that:
1. Implements Click's ParamType interface
2. Converts input strings using valid8r parsers
3. Can be used with Typer's `click_type` parameter

### validated_prompt()

Prompts for input in a loop:
1. Displays the prompt text
2. Reads user input
3. Validates using the parser
4. Retries on failure (up to max_retries)
5. Returns validated value or raises exception

### TyperParser (Advanced)

TyperParser works as both:
1. **Click ParamType**: Can be used with `typer.Option(click_type=TyperParser(...))`
2. **Callable Parser**: Can be used with `typer.Option(parser=TyperParser(...))`

When used with the `parser` parameter, Typer wraps the TyperParser in a FuncParamType internally. The TyperParser implements both the Click ParamType interface and the callable interface to support both use cases.

### Error Handling

All patterns raise user-friendly exceptions:
- `validator_callback()`: Raises `typer.BadParameter`
- `ValidatedType`: Raises `click.exceptions.BadParameter`
- `validated_prompt()`: Displays error, retries, then raises `typer.Exit`

Typer catches these exceptions and formats them nicely in the terminal with colored output and error boxes.

### Type Preservation

The parsed values retain their structured types (EmailAddress, PhoneNumber, UrlParts, etc.), allowing you to access component fields directly in your CLI commands.

## Complete Example

See the [Cloud CLI example](../../examples/typer-integration/cloud_cli.py) for a comprehensive demonstration of all integration patterns in a realistic CLI application.

The example includes:
- `validator_callback()` for port and region validation
- `ValidatedType` for custom ProjectId and ARN types
- `validated_prompt()` for interactive configuration wizard
- Error handling and help text generation
- Combining validation with Typer features (confirmations, styling, etc.)

## Best Practices

### Pattern Selection
1. **Use validator_callback() by default**: Simple, straightforward, works everywhere
2. **Use ValidatedType for reuse**: When the same type appears in 3+ places
3. **Use validated_prompt() for interactive flows**: Configuration wizards, onboarding

### Code Quality
4. **Use Type Annotations**: Always use `typing_extensions.Annotated` for clear parameter specifications
5. **Descriptive Error Prefixes**: Add context with `error_prefix` parameter in validator_callback()
6. **Meaningful Type Names**: Use custom `name` parameter in ValidatedType for better help text
7. **Combine with Validators**: Chain validators using monadic operations for complex rules

### Testing
8. **Test Your CLIs**: Write BDD tests using Typer's CliRunner to validate end-to-end behavior
9. **Test Error Cases**: Verify that invalid inputs produce clear error messages
10. **Test Interactive Prompts**: Use `MockInputContext` from valid8r.testing for interactive tests

## Integration with Other valid8r Features

### FastAPI Consistency

Use the same parsers in your CLI and web API:

```python
# CLI (Typer)
import typer
from typing_extensions import Annotated
from valid8r.core import parsers
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

@app.command()
def create_user(
    email: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_email))],
) -> None:
    print(f"Creating user: {email.local}@{email.domain}")

# Web API (FastAPI)
from fastapi import FastAPI, Query
from valid8r.integrations.pydantic import validator_from_parser

api = FastAPI()

@api.post("/users")
async def create_user_api(
    email: str = Query(..., description="User email"),
) -> dict:
    # Use the same parser for validation
    result = parsers.parse_email(email)
    if result.is_failure():
        raise ValueError(result.error_or(""))

    email_obj = result.value_or(None)
    return {"email": f"{email_obj.local}@{email_obj.domain}"}
```

### Environment Variables

Use the same parsers for CLI, web API, and environment variables:

```python
# Environment configuration
from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
from valid8r.core import parsers

schema = EnvSchema(fields={
    'port': EnvField(parser=parsers.parse_int, default=8080),
    'debug': EnvField(parser=parsers.parse_bool, default=False),
})
config = load_env_config(schema, prefix='APP_')

# CLI using the same parsers
import typer
from typing_extensions import Annotated
from valid8r.integrations.typer import TyperParser

app = typer.Typer()

def port_parser(text: str | None):
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

@app.command()
def start(
    port: Annotated[int, typer.Option(parser=TyperParser(port_parser))] = 8080,
) -> None:
    print(f"Starting server on port {port}")
```

## API Reference

### validator_callback()

```python
def validator_callback(
    parser: Callable[[str | None], Maybe[object]],
    *validators: Callable[[object], Maybe[object]],
    error_prefix: str | None = None,
) -> Callable[[str], object]:
    ...
```

Creates a Typer-compatible callback function from a valid8r parser.

**Parameters:**
- `parser`: A valid8r parser function that returns `Maybe[T]`
- `*validators`: Optional validator functions to chain after parsing
- `error_prefix`: Optional prefix for error messages (e.g., "Port number")

**Returns:**
- A callback function compatible with `typer.Option(callback=...)` or `typer.Argument(callback=...)`

**Raises:**
- `typer.BadParameter`: When validation fails

**Example:**
```python
email_callback = validator_callback(parsers.parse_email, error_prefix="Email")
port_callback = validator_callback(
    lambda t: parsers.parse_int(t).bind(validators.minimum(1))
)
```

### ValidatedType()

```python
def ValidatedType(
    parser: Callable[[str | None], Maybe[object]],
    name: str | None = None,
    help_text: str | None = None,
) -> click.ParamType:
    ...
```

Creates a custom Typer type with valid8r validation. Returns a TyperParser instance.

**Parameters:**
- `parser`: A valid8r parser function that returns `Maybe[T]`
- `name`: Optional custom name for the type (defaults to parser function name)
- `help_text`: Optional help text describing validation constraints

**Returns:**
- A Click ParamType (TyperParser) for use with `typer.Option(click_type=...)`

**Example:**
```python
Email = ValidatedType(parsers.parse_email)
Port = ValidatedType(
    lambda t: parsers.parse_int(t).bind(validators.minimum(1)),
    name="port",
    help_text="Port number (1-65535)"
)
```

### validated_prompt()

```python
def validated_prompt(
    prompt_text: str,
    parser: Callable[[str | None], Maybe[object]],
    *validators: Callable[[object], Maybe[object]],
    max_retries: int = 10,
    typer_style: bool = False,
) -> object:
    ...
```

Interactive prompt with valid8r validation and automatic retry logic.

**Parameters:**
- `prompt_text`: The prompt message to display to the user
- `parser`: A valid8r parser function that returns `Maybe[T]`
- `*validators`: Optional validator functions to chain after parsing
- `max_retries`: Maximum number of retry attempts (default: 10)
- `typer_style`: Whether to use Typer's styled output (default: False)

**Returns:**
- The validated and parsed value

**Raises:**
- `typer.Exit`: When max_retries is exceeded without valid input

**Example:**
```python
email = validated_prompt(
    "Enter your email",
    parser=parsers.parse_email,
    max_retries=3
)
```

### TyperParser (Advanced)

```python
class TyperParser(ParamTypeAdapter):
    def __init__(
        self,
        parser: Callable[[str], Maybe[T]],
        name: str | None = None,
        error_prefix: str | None = None,
    ) -> None:
        ...
```

Low-level Click ParamType adapter for valid8r parsers. Most users should use `validator_callback()` or `ValidatedType()` instead.

**Parameters:**
- `parser`: A valid8r parser function that takes a string and returns `Maybe[T]`
- `name`: Optional custom name for the type (defaults to `parser.__name__`)
- `error_prefix`: Optional prefix for error messages (e.g., "Email address")

**Methods:**
- `convert(value, param, ctx)`: Converts and validates the input value
- `__call__(value, param, ctx)`: Makes TyperParser callable for use with Typer's `parser` parameter

**Attributes:**
- `name`: The type name (used in help text)
- `parser`: The underlying valid8r parser function
- `error_prefix`: The error message prefix (if set)

## Related Documentation

- [Click Integration](click.md) - Lower-level Click integration (TyperParser builds on this)
- [Pydantic Integration](pydantic.md) - Use the same parsers in Pydantic models
- [Environment Variables](environment.md) - Use the same parsers for configuration
- [Typer Official Docs](https://typer.tiangolo.com/) - Learn more about Typer
