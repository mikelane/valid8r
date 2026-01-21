# CLI Starter Template

A production-ready CLI starter template demonstrating best practices for building command-line applications with **valid8r** input validation.

## Features

- **Argument Parsing**: Parse and validate command-line arguments with clear error messages
- **Interactive Prompts**: Prompt users for input with built-in validation and retry logic
- **Configuration Files**: Load and validate YAML/JSON configuration files
- **User Management**: Add, list, and delete users with comprehensive validation
- **Output Modes**: Verbose (`-v`) and quiet (`-q`) output modes
- **Proper Exit Codes**: 0 = success, 1 = user error, 2 = system error
- **Clean Architecture**: Separated validation logic for easy customization
- **Comprehensive Tests**: Full test suite demonstrating testing patterns

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use uv
uv pip install -r requirements.txt
```

### Usage

#### Add User (Command-line mode)

```bash
python cli.py add-user --name "John Doe" --age 25 --email john@example.com
```

#### Add User (Interactive mode)

```bash
python cli.py add-user --interactive
```

#### List Users

```bash
python cli.py list-users --file config.yaml
```

#### Delete User

```bash
python cli.py delete-user --name "John Doe" --file config.yaml
```

#### Load and Validate Configuration

```bash
python cli.py load-config --file config.yaml
python cli.py load-config --file config.json --verbose
```

## Project Structure

```
cli-starter-template/
├── cli.py              # Main CLI with subcommands
├── validators.py       # Validation logic using valid8r
├── README.md          # This file
├── requirements.txt   # Dependencies
└── tests/
    ├── __init__.py
    ├── test_validators.py  # Unit tests for validators
    └── test_cli.py         # Integration tests for CLI
```

## Configuration Files

### YAML Format

```yaml
users:
  - name: Alice
    age: 30
    email: alice@example.com
  - name: Bob
    age: 25
    email: bob@example.com
```

### JSON Format

```json
{
  "users": [
    {"name": "Alice", "age": 30, "email": "alice@example.com"},
    {"name": "Bob", "age": 25, "email": "bob@example.com"}
  ]
}
```

## Output Modes

### Verbose Mode (`--verbose` or `-v`)

Shows additional details:

```bash
python cli.py --verbose load-config --file config.yaml
# Loading configuration from config.yaml
# Configuration loaded successfully from config.yaml
# Found 2 user(s)
```

### Quiet Mode (`--quiet` or `-q`)

Minimal output:

```bash
python cli.py --quiet load-config --file config.yaml
# Configuration loaded successfully from config.yaml
```

## Exit Codes

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Operation completed successfully |
| 1 | User Error | Invalid input, validation failure |
| 2 | System Error | File not found, permission denied |

## Customization Guide

### Adding Your Own Validators

Edit `validators.py`:

```python
from valid8r import Maybe, parsers, validators

def parse_username(username_str: str) -> Maybe[str]:
    """Validate a username (alphanumeric, 3-20 chars)."""
    if not username_str or not username_str.strip():
        return Maybe.failure('Username cannot be empty')

    username = username_str.strip().lower()

    if len(username) < 3:
        return Maybe.failure('Username must be at least 3 characters')

    if len(username) > 20:
        return Maybe.failure('Username must be at most 20 characters')

    if not username.isalnum():
        return Maybe.failure('Username must be alphanumeric')

    return Maybe.success(username)
```

### Adding New Subcommands

In `cli.py`:

```python
def my_command(args: argparse.Namespace, output: OutputMode) -> int:
    """Your custom command logic."""
    # Validate inputs
    # Do work
    # Return exit code
    return ExitCode.SUCCESS

# In main()
my_parser = subparsers.add_parser('my-command', help='Description')
my_parser.add_argument('--option', type=str, help='Option description')

# Add to command dispatch
if args.command == 'my-command':
    return my_command(args, output)
```

### Using valid8r's Built-in Parsers

```python
from valid8r import parsers

# Basic types
parsers.parse_int('42')
parsers.parse_float('3.14')
parsers.parse_bool('yes')

# Network types
parsers.parse_email('user@example.com')
parsers.parse_url('https://example.com')
parsers.parse_ipv4('192.168.1.1')

# Dates and times
parsers.parse_date('2024-01-15')

# And many more...
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=term tests/

# Run specific test file
pytest tests/test_validators.py

# Run specific test class
pytest tests/test_cli.py::DescribeAddUserCommand
```

## Error Handling Best Practices

This template demonstrates:

1. **Clear Error Messages**: Errors explain what went wrong and what's expected
2. **Proper Exit Codes**: Semantic exit codes for scripting
3. **Validation Before Processing**: Validate all inputs before taking action
4. **Error Aggregation**: Report all errors at once, not just the first

### Example Error Messages

```bash
# Invalid age
$ python cli.py add-user --name "John" --age "twenty"
Error: Invalid age: Age must be a valid integer. Expected a valid integer.

# Missing required field
$ python cli.py add-user --name "John"
Error: --age is required

# Configuration file error
$ python cli.py load-config --file bad_config.yaml
Configuration validation failed for bad_config.yaml:
  Invalid age for user at position 1 (line 3): Age must be a valid integer
  Invalid email for user at position 2 (line 7): Must be a valid email address

# File not found (system error)
$ python cli.py load-config --file nonexistent.yaml
Error: Configuration file not found: nonexistent.yaml
$ echo $?
2
```

## Extending the Template

### For Simple CLIs

1. Add validators to `validators.py`
2. Add subcommands to `cli.py`
3. Add tests to `tests/test_*.py`

### For Complex CLIs

Consider organizing into modules:

```
my-cli/
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── commands/
│   │   ├── users.py
│   │   └── config.py
│   └── validators/
│       ├── user.py
│       └── config.py
├── tests/
│   ├── unit/
│   └── integration/
└── pyproject.toml
```

For complex CLIs, consider using Click or Typer (both integrate with valid8r):

```python
# Click integration
from valid8r.integrations.click import ParamTypeAdapter

@click.command()
@click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
def greet(email):
    click.echo(f'Hello {email.local}@{email.domain}!')
```

## Additional Resources

- **valid8r Documentation**: https://github.com/mikelane/valid8r
- **CLI Starter Template Tutorial**: docs/tutorials/cli-starter-template.md
- **Build a CLI in 10 Minutes**: docs/tutorials/build-cli-in-10-minutes.md

## License

This template is provided as an example and starting point. Feel free to modify it for your needs.
