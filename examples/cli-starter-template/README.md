# CLI Starter Template

A production-ready CLI starter template demonstrating best practices for building command-line applications with **valid8r** input validation.

## Features

- **Argument Parsing**: Parse and validate command-line arguments with clear error messages
- **Interactive Prompts**: Prompt users for input with built-in validation and retry logic
- **Configuration Files**: Load and validate YAML configuration files with detailed error reporting
- **Clean Architecture**: Separated validation logic in `validators.py` for easy customization
- **Comprehensive Tests**: Full test suite demonstrating testing patterns for CLI applications

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

#### Load Configuration File

```bash
python cli.py load-config --file config.yaml
```

## Project Structure

```
cli-starter-template/
├── cli.py              # Main CLI with subcommands
├── validators.py       # Validation logic using valid8r
├── README.md          # This file
├── requirements.txt   # Dependencies
└── tests/            # Test directory
    ├── __init__.py
    └── test_validators.py  # Unit tests for validators
```

## Customization Guide

### Adding Your Own Validators

Edit `validators.py` to add custom validation logic:

```python
from valid8r import Maybe, parsers

def parse_username(username_str: str) -> Maybe[str]:
    """Validate a username (alphanumeric, 3-20 chars)."""
    if not username_str or not username_str.strip():
        return Maybe.failure('Username cannot be empty')

    # Use valid8r's parsers for common types
    # Or implement your own validation logic
    if len(username_str) < 3:
        return Maybe.failure('Username too short (min 3 characters)')

    if len(username_str) > 20:
        return Maybe.failure('Username too long (max 20 characters)')

    if not username_str.isalnum():
        return Maybe.failure('Username must be alphanumeric')

    return Maybe.success(username_str)
```

### Adding New Subcommands

Add a new subcommand in `cli.py`:

```python
def my_command(args: argparse.Namespace) -> int:
    """Your custom command logic."""
    # Add your implementation here
    return 0

# In main()
my_parser = subparsers.add_parser('my-command', help='Description')
my_parser.add_argument('--option', type=str, help='Option description')

# Add to command dispatch
if args.command == 'my-command':
    return my_command(args)
```

### Using valid8r's Built-in Parsers

valid8r provides many built-in parsers you can use directly:

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

### Interactive Prompts with Validation

Use `valid8r.prompt.ask()` for interactive input:

```python
from valid8r import prompt
from validators import parse_age

# Automatically retries on invalid input
age = prompt.ask('Enter your age: ', parser=parse_age)
```

### Configuration File Validation

The template shows how to validate YAML configuration files with detailed error messages including line numbers:

```yaml
# config.yaml
users:
  - name: Alice
    age: 30
    email: alice@example.com
  - name: Bob
    age: 25
    email: bob@example.com
```

The validator will report specific fields that are invalid and their location in the file.

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=term tests/

# Run specific test
pytest tests/test_validators.py::DescribeParseAge
```

## Error Handling Best Practices

This template demonstrates:

1. **Clear Error Messages**: Errors explain what went wrong and what's expected
2. **Exit Codes**: 0 for success, 1 for user errors
3. **Validation Before Processing**: Validate all inputs before taking action
4. **Helpful Feedback**: Guide users to correct their mistakes

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
```

## Design Philosophy

This template follows these principles:

- **Fail Fast**: Validate inputs immediately, before processing
- **Clear Feedback**: Every error message should be actionable
- **Separation of Concerns**: Validators are separate from CLI logic
- **Testability**: All logic is testable without running the CLI
- **Composability**: Validators can be combined using `&`, `|`, `~` operators

## Extending the Template

### For Simple CLIs

If you're building a simple CLI with a few commands:

1. Add validators to `validators.py`
2. Add subcommands to `cli.py`
3. Add tests to `tests/test_*.py`

### For Complex CLIs

If you're building a complex CLI with many commands:

1. Split subcommands into separate files (e.g., `commands/add_user.py`)
2. Organize validators by domain (e.g., `validators/user.py`, `validators/config.py`)
3. Use dependency injection for testability
4. Consider using a CLI framework like Click or Typer (both work great with valid8r)

## Additional Resources

- **valid8r Documentation**: https://github.com/mikelane/valid8r
- **Argparse Documentation**: https://docs.python.org/3/library/argparse.html
- **Click Framework**: https://click.palletsprojects.com/
- **Typer Framework**: https://typer.tiangolo.com/

## License

This template is provided as an example and starting point. Feel free to modify it for your needs.
