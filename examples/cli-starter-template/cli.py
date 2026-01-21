#!/usr/bin/env python
"""CLI Starter Template - Production-ready CLI with valid8r validation.

This template demonstrates how to build a CLI application with:
- Argument parsing with validation using valid8r's type_from_parser
- Interactive prompts with retry logic
- Configuration file validation (YAML and JSON)
- Clear error messages with proper exit codes
- Verbose and quiet output modes

Exit Codes:
- 0: Success
- 1: User input error (invalid arguments, validation failure)
- 2: System error (file not found, permission denied)

Customize this CLI by:
1. Adding your own subcommands
2. Using validators from validators.py
3. Extending with your own validation logic
"""

from __future__ import annotations

import argparse
import json
import sys
from enum import IntEnum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

import yaml
from validators import (
    parse_age,
    parse_email,
    parse_name,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from valid8r import Maybe

T = TypeVar('T')


class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    SUCCESS = 0
    USER_ERROR = 1
    SYSTEM_ERROR = 2


class OutputMode:
    """Output mode configuration for controlling verbosity."""

    def __init__(self, verbose: bool = False, quiet: bool = False) -> None:
        """Initialize output mode.

        Args:
            verbose: Enable verbose output
            quiet: Enable quiet mode (minimal output)

        """
        self.verbose = verbose
        self.quiet = quiet

    def info(self, message: str) -> None:
        """Print an info message (not shown in quiet mode)."""
        if not self.quiet:
            print(message)

    def success(self, message: str) -> None:
        """Print a success message (always shown)."""
        print(message)

    def detail(self, message: str) -> None:
        """Print a detail message (only in verbose mode)."""
        if self.verbose:
            print(message)

    def error(self, message: str) -> None:
        """Print an error message to stderr."""
        print(message, file=sys.stderr)


def prompt_with_retry(prompt_text: str, parser: Callable[[str], Maybe[T]]) -> T:
    """Prompt user for input with validation and retry logic.

    This function displays a prompt, reads user input, validates it using the
    provided parser, and retries on validation failure.

    Args:
        prompt_text: The text to display as the prompt
        parser: A validation function that returns Maybe[T]

    Returns:
        The successfully parsed and validated value

    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
        EOFError: If input stream ends unexpectedly

    """
    print(f'{prompt_text}: ', end='', flush=True)
    user_input = input()
    result = parser(user_input)

    while result.is_failure():
        print(f'Invalid input: {result.error_or("")}. Please try again.')
        print(f'{prompt_text}: ', end='', flush=True)
        user_input = input()
        result = parser(user_input)

    return result.value_or(None)  # type: ignore[return-value]


def add_user_command(args: argparse.Namespace, output: OutputMode) -> int:
    """Add a user with validated input.

    Args:
        args: Parsed command-line arguments
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for error)

    """
    if args.interactive:
        return add_user_interactive(output)

    return add_user_from_args(args.name, args.age, args.email, output)


def add_user_interactive(output: OutputMode) -> int:
    """Add a user using interactive prompts.

    Args:
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for error)

    """
    try:
        name = prompt_with_retry('Enter name', parse_name)
        age = prompt_with_retry('Enter age', parse_age)
        email = prompt_with_retry('Enter email', parse_email)
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled by user')
        return ExitCode.USER_ERROR
    else:
        output.success('User added successfully!')
        output.info(f'Name: {name}')
        output.info(f'Age: {age}')
        output.info(f'Email: {email}')
        return ExitCode.SUCCESS


def validate_name_arg(name: str | None) -> tuple[str | None, str | None]:
    """Validate the name argument.

    Args:
        name: The name argument value (may be None if not provided)

    Returns:
        A tuple of (validated_value, error_message).
        If validation succeeds, error_message is None.
        If validation fails, validated_value is None.

    """
    if name is None:
        return None, 'Error: --name is required'

    name_result = parse_name(name)
    if name_result.is_failure():
        return None, f'Error: Invalid name: {name_result.error_or("")}'

    return name_result.value_or(None), None


def validate_age_arg(age: str | None) -> tuple[int | None, str | None]:
    """Validate the age argument.

    Args:
        age: The age argument value as string (may be None if not provided)

    Returns:
        A tuple of (validated_value, error_message).
        If validation succeeds, error_message is None.
        If validation fails, validated_value is None.

    """
    if age is None:
        return None, 'Error: --age is required'

    age_result = parse_age(age)
    if age_result.is_failure():
        return None, f'Error: Invalid age: {age_result.error_or("")}. Expected a valid integer.'

    return age_result.value_or(None), None


def validate_email_arg(email: str | None) -> tuple[str | None, str | None]:
    """Validate the email argument.

    Args:
        email: The email argument value (may be None if not provided)

    Returns:
        A tuple of (validated_value, error_message).
        If validation succeeds or email is None/empty, error_message is None.
        If validation fails, validated_value is None.

    """
    if not email:
        return None, None

    email_result = parse_email(email)
    if email_result.is_failure():
        return None, f'Error: Invalid email: {email_result.error_or("")}'

    return email_result.value_or(None), None


def add_user_from_args(name: str | None, age: str | None, email: str | None, output: OutputMode) -> int:
    """Add a user from command-line arguments.

    Args:
        name: User's name
        age: User's age (as string)
        email: User's email
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for error)

    """
    errors: list[str] = []

    name_value, name_error = validate_name_arg(name)
    if name_error:
        errors.append(name_error)

    age_value, age_error = validate_age_arg(age)
    if age_error:
        errors.append(age_error)

    email_value, email_error = validate_email_arg(email)
    if email_error:
        errors.append(email_error)

    if errors:
        for error in errors:
            output.error(error)
        return ExitCode.USER_ERROR

    output.success('User added successfully!')
    if name_value:
        output.info(f'Name: {name_value}')
    if age_value is not None:
        output.info(f'Age: {age_value}')
    if email_value:
        output.info(f'Email: {email_value}')

    return ExitCode.SUCCESS


def list_users_command(args: argparse.Namespace, output: OutputMode) -> int:
    """List users from a configuration file.

    Args:
        args: Parsed command-line arguments
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for user error, 2 for system error)

    """
    config_path = Path(args.file)

    config, error_code = load_config_file(config_path, output)
    if config is None:
        return error_code

    errors = validate_config(config, config_path)
    if errors:
        output.error(f'Configuration validation failed for {config_path}:')
        for error in errors:
            output.error(f'  {error}')
        return ExitCode.USER_ERROR

    users = config.get('users', [])
    if not users:
        output.info('No users found in configuration.')
        return ExitCode.SUCCESS

    output.detail(f'Found {len(users)} user(s) in {config_path}')
    output.info('')
    output.info('Users:')
    for i, user in enumerate(users, 1):
        name = user.get('name', 'Unknown')
        age = user.get('age', 'N/A')
        email = user.get('email', 'N/A')
        output.info(f'  {i}. {name} (age: {age}, email: {email})')

    return ExitCode.SUCCESS


def delete_user_command(args: argparse.Namespace, output: OutputMode) -> int:
    """Delete a user from a configuration file.

    Args:
        args: Parsed command-line arguments
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for user error, 2 for system error)

    """
    config_path = Path(args.file)

    config, error_code = load_config_file(config_path, output)
    if config is None:
        return error_code

    users = config.get('users', [])
    target_name = args.name

    user_index = None
    for i, user in enumerate(users):
        if user.get('name') == target_name:
            user_index = i
            break

    if user_index is None:
        output.error(f'Error: User "{target_name}" not found in {config_path}')
        return ExitCode.USER_ERROR

    del users[user_index]

    try:
        save_config_file(config_path, config)
    except OSError as e:
        output.error(f'Error: Failed to save configuration: {e}')
        return ExitCode.SYSTEM_ERROR

    output.success(f'User "{target_name}" deleted successfully.')
    output.detail(f'Configuration saved to {config_path}')
    return ExitCode.SUCCESS


def load_config_file(config_path: Path, output: OutputMode) -> tuple[dict | None, int]:
    """Load a configuration file (YAML or JSON).

    Args:
        config_path: Path to the configuration file
        output: Output mode configuration

    Returns:
        Tuple of (config dict, exit code). If loading fails, config is None.

    """
    if not config_path.exists():
        output.error(f'Error: Configuration file not found: {config_path}')
        return None, ExitCode.SYSTEM_ERROR

    output.detail(f'Loading configuration from {config_path}')

    try:
        with config_path.open() as f:
            content = f.read()
    except OSError as e:
        output.error(f'Error: Failed to read configuration file: {e}')
        return None, ExitCode.SYSTEM_ERROR

    suffix = config_path.suffix.lower()
    try:
        if suffix == '.json':
            config = json.loads(content)
        else:
            config = yaml.safe_load(content)
    except json.JSONDecodeError as e:
        output.error(f'Error: Invalid JSON in configuration file: {e}')
        return None, ExitCode.USER_ERROR
    except yaml.YAMLError as e:
        output.error(f'Error: Invalid YAML in configuration file: {e}')
        return None, ExitCode.USER_ERROR

    return config, ExitCode.SUCCESS


def save_config_file(config_path: Path, config: dict) -> None:
    """Save a configuration file (YAML or JSON).

    Args:
        config_path: Path to the configuration file
        config: Configuration dictionary to save

    Raises:
        OSError: If writing fails

    """
    suffix = config_path.suffix.lower()
    if suffix == '.json':
        content = json.dumps(config, indent=2)
    else:
        content = yaml.dump(config, default_flow_style=False)

    with config_path.open('w') as f:
        f.write(content)


def load_config_command(args: argparse.Namespace, output: OutputMode) -> int:
    """Load and validate a configuration file.

    Args:
        args: Parsed command-line arguments
        output: Output mode configuration

    Returns:
        Exit code (0 for success, 1 for user error, 2 for system error)

    """
    config_path = Path(args.file)

    config, error_code = load_config_file(config_path, output)
    if config is None:
        return error_code

    errors = validate_config(config, config_path)

    if errors:
        output.error(f'Configuration validation failed for {config_path}:')
        for error in errors:
            output.error(f'  {error}')
        return ExitCode.USER_ERROR

    output.success(f'Configuration loaded successfully from {config_path}')
    output.detail(f'Found {len(config.get("users", []))} user(s)')
    return ExitCode.SUCCESS


def validate_config(config: object, config_path: Path) -> list[str]:
    """Validate a configuration dictionary.

    This function accepts any object from yaml.safe_load() and validates that
    it conforms to the expected configuration structure.

    Args:
        config: Configuration object (expected to be a dict, but may be any YAML value)
        config_path: Path to the configuration file (for error messages)

    Returns:
        List of error messages (empty if valid)

    """
    errors: list[str] = []

    if not isinstance(config, dict):
        errors.append('Configuration must be a dictionary')
        return errors

    if 'users' not in config:
        errors.append('Configuration must contain a "users" key')
        return errors

    users = config['users']
    if not isinstance(users, list):
        errors.append('The "users" key must be a list')
        return errors

    for i, user in enumerate(users):
        user_errors = validate_user(user, i + 1, config_path)
        errors.extend(user_errors)

    return errors


def validate_user(user: object, index: int, config_path: Path) -> list[str]:
    """Validate a user dictionary from configuration.

    This function accepts any object and validates that it conforms to the
    expected user structure with name, age, and email fields.

    Args:
        user: User object (expected to be a dict, but may be any YAML value)
        index: User index in the list (1-based, for error reporting)
        config_path: Path to the configuration file (for error messages)

    Returns:
        List of error messages (empty if valid)

    """
    errors: list[str] = []

    if not isinstance(user, dict):
        errors.append(f'User at position {index} must be a dictionary')
        return errors

    if 'name' in user:
        name_result = parse_name(str(user['name']))
        if name_result.is_failure():
            errors.append(
                f'Invalid name for user at position {index} in {config_path.name}: {name_result.error_or("")}'
            )

    if 'age' in user:
        age_value = user['age']
        age_str = str(age_value) if age_value is not None else ''

        age_result = parse_age(age_str)
        if age_result.is_failure():
            errors.append(f'Invalid age for user at position {index} in {config_path.name}: {age_result.error_or("")}')

    if 'email' in user:
        email_result = parse_email(str(user['email']))
        if email_result.is_failure():
            errors.append(
                f'Invalid email for user at position {index} in {config_path.name}: {email_result.error_or("")}'
            )

    return errors


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for user error, 2 for system error)

    """
    parser = argparse.ArgumentParser(
        description='CLI Starter Template - Production-ready CLI with valid8r validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output',
    )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Enable quiet mode (minimal output)',
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    add_user_parser = subparsers.add_parser('add-user', help='Add a new user with validation')
    add_user_parser.add_argument('--name', type=str, help='User name')
    add_user_parser.add_argument('--age', type=str, help='User age')
    add_user_parser.add_argument('--email', type=str, help='User email')
    add_user_parser.add_argument('--interactive', action='store_true', help='Interactive mode with prompts')

    list_users_parser = subparsers.add_parser('list-users', help='List users from a configuration file')
    list_users_parser.add_argument('--file', type=str, required=True, help='Path to configuration file')

    delete_user_parser = subparsers.add_parser('delete-user', help='Delete a user from configuration')
    delete_user_parser.add_argument('--name', type=str, required=True, help='Name of user to delete')
    delete_user_parser.add_argument('--file', type=str, required=True, help='Path to configuration file')

    load_config_parser = subparsers.add_parser('load-config', help='Load and validate a configuration file')
    load_config_parser.add_argument('--file', type=str, required=True, help='Path to configuration file')

    args = parser.parse_args()

    output = OutputMode(verbose=args.verbose, quiet=args.quiet)

    if args.command == 'add-user':
        return add_user_command(args, output)
    if args.command == 'list-users':
        return list_users_command(args, output)
    if args.command == 'delete-user':
        return delete_user_command(args, output)
    if args.command == 'load-config':
        return load_config_command(args, output)

    parser.print_help()
    return ExitCode.USER_ERROR


if __name__ == '__main__':
    sys.exit(main())
