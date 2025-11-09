# Typer Integration

The `valid8r.integrations.typer` module provides seamless integration between valid8r parsers and [Typer](https://typer.tiangolo.com/), a modern CLI framework built on top of Click.

## Overview

The `TyperParser` class wraps valid8r parsers for use with Typer's `Option()` and `Argument()` functions, enabling rich validation of CLI arguments using the same parsers you use throughout your application (FastAPI, Pydantic, environment variables, etc.).

## Installation

Typer must be installed separately:

```bash
uv add typer
# or
pip install typer
```

## Basic Usage

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

## How It Works

TyperParser works as both:
1. **Click ParamType**: Can be used with `typer.Option(click_type=TyperParser(...))`
2. **Callable Parser**: Can be used with `typer.Option(parser=TyperParser(...))`

When used with the `parser` parameter (recommended), Typer wraps the TyperParser in a FuncParamType internally. The TyperParser implements both the Click ParamType interface and the callable interface to support both use cases.

### Error Handling

When validation fails, TyperParser raises a `click.exceptions.BadParameter` exception with the error message from the valid8r parser. Typer catches this exception and formats it nicely in the terminal with colored output and error boxes.

### Type Preservation

The parsed values retain their structured types (EmailAddress, PhoneNumber, UrlParts, etc.), allowing you to access component fields directly in your CLI commands.

## Best Practices

1. **Use Type Annotations**: Always use `typing_extensions.Annotated` for clear parameter specifications
2. **Descriptive Error Prefixes**: Add context to error messages with `error_prefix` parameter
3. **Meaningful Type Names**: Use custom `name` parameter for better help text
4. **Combine with Validators**: Chain validators for complex validation rules
5. **Test Your CLIs**: Write BDD tests to validate CLI behavior end-to-end

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

### TyperParser

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

**Parameters:**
- `parser`: A valid8r parser function that takes a string and returns `Maybe[T]`
- `name`: Optional custom name for the type (defaults to `parser.__name__`)
- `error_prefix`: Optional prefix for error messages (e.g., "Email address")

**Methods:**
- `convert(value, param, ctx)`: Converts and validates the input value
- `__call__(value)`: Makes TyperParser callable for use with Typer's `parser` parameter

**Attributes:**
- `name`: The type name (used in help text)
- `parser`: The underlying valid8r parser function
- `error_prefix`: The error message prefix (if set)

## Related Documentation

- [Click Integration](click.md) - Lower-level Click integration (TyperParser builds on this)
- [Pydantic Integration](pydantic.md) - Use the same parsers in Pydantic models
- [Environment Variables](environment.md) - Use the same parsers for configuration
- [Typer Official Docs](https://typer.tiangolo.com/) - Learn more about Typer
