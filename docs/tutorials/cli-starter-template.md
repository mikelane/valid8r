# CLI Starter Template

The CLI Starter Template is a production-ready foundation for building command-line applications with **valid8r** input validation. This guide walks you through using, customizing, and extending the template.

**What you'll learn:**
- Project structure and design philosophy
- Using the template's subcommands
- Adding custom validators and commands
- Configuration file validation (YAML/JSON)
- Testing patterns for CLI applications
- Verbose/quiet output modes and exit codes

**Prerequisites:**
- Python 3.9+
- Basic knowledge of argparse
- Familiarity with valid8r basics (see [Build a CLI in 10 Minutes](./build-cli-in-10-minutes.md))

---

## Getting Started

### Clone or Copy the Template

The template is located in the `examples/cli-starter-template/` directory:

```bash
# Option 1: Copy from valid8r repository
git clone https://github.com/mikelane/valid8r
cp -r valid8r/examples/cli-starter-template my-cli

# Option 2: Start fresh with the structure
mkdir -p my-cli/tests
cd my-cli
```

### Install Dependencies

```bash
cd my-cli
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

### Try It Out

```bash
# Add a user
python cli.py add-user --name "Alice Smith" --age 30 --email alice@example.com

# List users from config
python cli.py list-users --file config.yaml

# Load and validate config
python cli.py load-config --file config.yaml --verbose

# Interactive mode
python cli.py add-user --interactive
```

---

## Project Structure

```
cli-starter-template/
├── cli.py              # Main CLI with subcommands
├── validators.py       # Validation logic using valid8r
├── requirements.txt    # Dependencies (just valid8r + PyYAML)
├── README.md          # Quick start guide
└── tests/
    ├── __init__.py
    ├── test_validators.py  # Unit tests for validators
    └── test_cli.py         # Integration tests for CLI
```

### Design Philosophy

The template follows these principles:

1. **Separation of Concerns**: Validators are in `validators.py`, CLI logic in `cli.py`
2. **Fail Fast**: Validate all inputs before processing
3. **Clear Error Messages**: Every error explains what went wrong and how to fix it
4. **Testability**: All logic is testable without running the actual CLI
5. **Proper Exit Codes**: 0 = success, 1 = user error, 2 = system error

---

## Available Commands

### add-user

Add a new user with validated name, age, and email:

```bash
# Command-line mode
python cli.py add-user --name "John Doe" --age 25 --email john@example.com

# Interactive mode (prompts for input)
python cli.py add-user --interactive
```

**Validation Rules:**
- **Name**: 2-100 characters, cannot be empty
- **Age**: Integer 0-150
- **Email**: Valid email format

### list-users

List users from a configuration file:

```bash
python cli.py list-users --file config.yaml
python cli.py list-users --file config.json --verbose
```

### delete-user

Delete a user from a configuration file:

```bash
python cli.py delete-user --name "Alice" --file config.yaml
```

### load-config

Validate a configuration file without modifying it:

```bash
python cli.py load-config --file config.yaml
python cli.py load-config --file config.json --verbose
```

---

## Output Modes

### Verbose Mode (`--verbose` or `-v`)

Shows additional details about operations:

```bash
python cli.py --verbose load-config --file config.yaml
# Loading configuration from config.yaml
# Configuration loaded successfully from config.yaml
# Found 3 user(s)
```

### Quiet Mode (`--quiet` or `-q`)

Shows minimal output (only success/error messages):

```bash
python cli.py --quiet load-config --file config.yaml
# Configuration loaded successfully from config.yaml
```

---

## Exit Codes

The template uses semantic exit codes:

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Operation completed successfully |
| 1 | User Error | Invalid input, validation failure |
| 2 | System Error | File not found, permission denied |

```bash
python cli.py add-user --name "J" --age 25 --email test@example.com
echo $?  # 1 (name too short)

python cli.py load-config --file nonexistent.yaml
echo $?  # 2 (file not found)
```

---

## Configuration Files

The template supports both YAML and JSON configuration files.

### YAML Example

```yaml
# config.yaml
users:
  - name: Alice Smith
    age: 30
    email: alice@example.com
  - name: Bob Jones
    age: 25
    email: bob@example.com
```

### JSON Example

```json
{
  "users": [
    {
      "name": "Alice Smith",
      "age": 30,
      "email": "alice@example.com"
    },
    {
      "name": "Bob Jones",
      "age": 25,
      "email": "bob@example.com"
    }
  ]
}
```

### Validation Errors

Configuration validation provides detailed error messages:

```bash
python cli.py load-config --file bad_config.yaml
# Configuration validation failed for bad_config.yaml:
#   Invalid age for user at position 1 in bad_config.yaml: Age must be a valid integer
#   Invalid email for user at position 2 in bad_config.yaml: Must be a valid email address
```

---

## Customization Guide

### Adding Custom Validators

Edit `validators.py` to add your own validation functions:

```python
from valid8r import Maybe, parsers, validators


def parse_username(text: str) -> Maybe[str]:
    """Parse and validate a username (alphanumeric, 3-20 chars)."""
    if not text or not text.strip():
        return Maybe.failure('Username cannot be empty')

    username = text.strip().lower()

    if len(username) < 3:
        return Maybe.failure('Username must be at least 3 characters')

    if len(username) > 20:
        return Maybe.failure('Username must be at most 20 characters')

    if not username.isalnum():
        return Maybe.failure('Username must be alphanumeric')

    return Maybe.success(username)


def parse_port(text: str) -> Maybe[int]:
    """Parse and validate a port number (1-65535)."""
    return parsers.parse_int(text).bind(
        validators.between(1, 65535, error_message='Port must be 1-65535')
    )
```

### Adding New Subcommands

Add a new subcommand in `cli.py`:

```python
def my_command(args: argparse.Namespace, output: OutputMode) -> int:
    """Your custom command implementation."""
    # Validate inputs
    if not args.required_field:
        output.error('Error: --required-field is required')
        return ExitCode.USER_ERROR

    # Do the work
    output.success('Operation completed!')
    output.detail(f'Processed: {args.required_field}')
    return ExitCode.SUCCESS


# In main(), add the subparser:
my_parser = subparsers.add_parser('my-command', help='Description of my command')
my_parser.add_argument('--required-field', type=str, required=True, help='A required field')
my_parser.add_argument('--optional-field', type=str, help='An optional field')

# Add to command dispatch:
if args.command == 'my-command':
    return my_command(args, output)
```

### Using type_from_parser for Argparse

For automatic validation in argparse, use `type_from_parser`:

```python
from valid8r.integrations.argparse import type_from_parser
from valid8r import parsers

parser.add_argument(
    '--email',
    type=type_from_parser(parsers.parse_email),
    help='Email address (validated)',
)

parser.add_argument(
    '--port',
    type=type_from_parser(parse_port),
    help='Port number (1-65535)',
)
```

This provides validation at argument parsing time with automatic error messages.

---

## Testing Patterns

### Unit Tests for Validators

Test validators independently:

```python
import pytest
from validators import parse_age, parse_name, parse_email


class DescribeParseAge:
    """Tests for age validation."""

    @pytest.mark.parametrize(
        ('age_str', 'expected'),
        [
            pytest.param('25', 25, id='valid-25'),
            pytest.param('0', 0, id='zero'),
            pytest.param('150', 150, id='edge-150'),
        ],
    )
    def it_parses_valid_ages(self, age_str: str, expected: int) -> None:
        result = parse_age(age_str)
        assert result.is_success()
        assert result.value_or(None) == expected

    @pytest.mark.parametrize(
        ('invalid_age', 'error_substr'),
        [
            pytest.param('not-a-number', 'integer', id='non-numeric'),
            pytest.param('-5', 'negative', id='negative'),
            pytest.param('999', 'unrealistic', id='too-large'),
        ],
    )
    def it_rejects_invalid_ages(self, invalid_age: str, error_substr: str) -> None:
        result = parse_age(invalid_age)
        assert result.is_failure()
        assert error_substr.lower() in result.error_or('').lower()
```

### Integration Tests for CLI

Test the CLI as a subprocess:

```python
import subprocess
import sys
from pathlib import Path

import yaml


def it_accepts_valid_arguments(self) -> None:
    """Accept valid command-line arguments."""
    result = subprocess.run(
        [
            sys.executable,
            'cli.py',
            'add-user',
            '--name', 'John Doe',
            '--age', '25',
            '--email', 'john@example.com',
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert 'User added successfully' in result.stdout


def it_validates_config_files(self, tmp_path: Path) -> None:
    """Validate configuration files."""
    config = {'users': [{'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}]}
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(yaml.dump(config))

    result = subprocess.run(
        [sys.executable, 'cli.py', 'load-config', '--file', str(config_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

### Testing Interactive Mode

Use `MockInputContext` to test interactive prompts:

```python
from valid8r.testing import MockInputContext


def it_handles_interactive_input(self) -> None:
    """Test interactive mode with mocked input."""
    with MockInputContext(['John Doe', '25', 'john@example.com']):
        # Call the interactive function
        result = add_user_interactive(output)
        assert result == 0
```

---

## Best Practices

### 1. Validate Early

Validate all inputs before doing any work:

```python
def my_command(args: argparse.Namespace, output: OutputMode) -> int:
    # Validate ALL inputs first
    errors = []

    name_result = parse_name(args.name)
    if name_result.is_failure():
        errors.append(f'Invalid name: {name_result.error_or("")}')

    age_result = parse_age(args.age)
    if age_result.is_failure():
        errors.append(f'Invalid age: {age_result.error_or("")}')

    # Report ALL errors at once
    if errors:
        for error in errors:
            output.error(error)
        return ExitCode.USER_ERROR

    # Now do the work...
```

### 2. Use Semantic Exit Codes

```python
class ExitCode(IntEnum):
    SUCCESS = 0
    USER_ERROR = 1      # Bad input, validation failure
    SYSTEM_ERROR = 2    # File not found, permission denied
```

### 3. Support Multiple Output Modes

```python
class OutputMode:
    def info(self, message: str) -> None:
        """Normal output (hidden in quiet mode)."""
        if not self.quiet:
            print(message)

    def detail(self, message: str) -> None:
        """Verbose output (only in verbose mode)."""
        if self.verbose:
            print(message)

    def error(self, message: str) -> None:
        """Error output (always shown, to stderr)."""
        print(message, file=sys.stderr)
```

### 4. Test Both Success and Failure Paths

```python
def it_succeeds_with_valid_input(self) -> None:
    assert result.returncode == 0

def it_fails_with_invalid_input(self) -> None:
    assert result.returncode == 1
    assert 'error' in result.stderr.lower()
```

---

## Extending the Template

### For Simple CLIs

1. Add validators to `validators.py`
2. Add subcommands to `cli.py`
3. Add tests to `tests/`

### For Complex CLIs

Consider organizing into modules:

```
my-cli/
├── cli/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── users.py     # User-related commands
│   │   └── config.py    # Config-related commands
│   └── validators/
│       ├── __init__.py
│       ├── user.py      # User validators
│       └── config.py    # Config validators
├── tests/
│   ├── unit/
│   │   └── validators/
│   └── integration/
│       └── commands/
└── pyproject.toml
```

### Using Click or Typer

valid8r integrates with both Click and Typer for more complex CLIs:

```python
# Click integration
from valid8r.integrations.click import ParamTypeAdapter
import click

@click.command()
@click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
def greet(email):
    click.echo(f'Hello {email.local}@{email.domain}!')


# Typer integration
from valid8r.integrations.typer import TyperParser
import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def greet(
    email: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_email))]
) -> None:
    print(f'Hello {email.local}@{email.domain}!')
```

---

## Additional Resources

- **[Build a CLI in 10 Minutes](./build-cli-in-10-minutes.md)** - Quick start tutorial
- **[Validators Guide](../user_guide/validators.rst)** - All validators and combinators
- **[Parsers Reference](../user_guide/parsers.rst)** - All parser types
- **[argparse Integration](../integrations/argparse.rst)** - type_from_parser details
- **[Click Integration](../integrations/click.rst)** - ParamTypeAdapter details
- **[Typer Integration](../integrations/typer.rst)** - TyperParser details

---

## Template License

The CLI Starter Template is provided as an example and starting point. Feel free to modify and use it for any purpose, including commercial projects.
