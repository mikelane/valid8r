#!/usr/bin/env python
"""CLI Starter Template - Production-ready CLI with valid8r validation.

This template demonstrates how to build a CLI application with:
- Argument parsing with validation
- Interactive prompts with retry logic
- Configuration file validation
- Clear error messages

Customize this CLI by:
1. Adding your own subcommands
2. Using validators from validators.py
3. Extending with your own validation logic
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from validators import (
    parse_age,
    parse_email,
    parse_name,
)


def add_user_command(args: argparse.Namespace) -> int:
    """Add a user with validated input.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    # Interactive mode: prompt for all fields
    if args.interactive:
        return add_user_interactive()

    # Command-line mode: validate provided arguments
    return add_user_from_args(args.name, args.age, args.email)


def add_user_interactive() -> int:
    """Add a user using interactive prompts.

    Returns:
        Exit code (0 for success, 1 for error)

    """
    try:
        # Prompt for name
        print('Enter name: ', end='', flush=True)
        name_input = input()
        name_result = parse_name(name_input)

        while name_result.is_failure():
            print(f'Invalid input: {name_result.error_or("")}. Please try again.')
            print('Enter name: ', end='', flush=True)
            name_input = input()
            name_result = parse_name(name_input)

        name = name_result.value_or('')

        # Prompt for age with validation
        print('Enter age: ', end='', flush=True)
        age_input = input()
        age_result = parse_age(age_input)

        while age_result.is_failure():
            print(f'Invalid input: {age_result.error_or("")}. Please try again.')
            print('Enter age: ', end='', flush=True)
            age_input = input()
            age_result = parse_age(age_input)

        age = age_result.value_or(0)

        # Prompt for email
        print('Enter email: ', end='', flush=True)
        email_input = input()
        email_result = parse_email(email_input)

        while email_result.is_failure():
            print(f'Invalid input: {email_result.error_or("")}. Please try again.')
            print('Enter email: ', end='', flush=True)
            email_input = input()
            email_result = parse_email(email_input)

        email = email_result.value_or('')

    except (KeyboardInterrupt, EOFError):
        print('\nCancelled by user')
        return 1
    else:
        print('\nUser added successfully!')
        print(f'Name: {name}')
        print(f'Age: {age}')
        print(f'Email: {email}')
        return 0


def add_user_from_args(name: str | None, age: str | None, email: str | None) -> int:  # noqa: C901, PLR0912
    """Add a user from command-line arguments.

    Args:
        name: User's name
        age: User's age (as string)
        email: User's email

    Returns:
        Exit code (0 for success, 1 for error)

    """
    errors = []

    # Validate name
    if name is None:
        errors.append('Error: --name is required')
        name_value = None
    else:
        name_result = parse_name(name)
        if name_result.is_failure():
            errors.append(f'Error: Invalid name: {name_result.error_or("")}')
            name_value = None
        else:
            name_value = name_result.value_or(None)

    # Validate age
    if age is None:
        errors.append('Error: --age is required')
        age_value = None
    else:
        age_result = parse_age(age)
        if age_result.is_failure():
            errors.append(f'Error: Invalid age: {age_result.error_or("")}. Expected a valid integer.')
            age_value = None
        else:
            age_value = age_result.value_or(None)

    # Validate email
    if email:
        email_result = parse_email(email)
        if email_result.is_failure():
            errors.append(f'Error: Invalid email: {email_result.error_or("")}')
            email_value = None
        else:
            email_value = email_result.value_or(None)
    else:
        email_value = None

    # Report all errors
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    # Success
    print('User added successfully!')
    if name_value:
        print(f'Name: {name_value}')
    if age_value is not None:
        print(f'Age: {age_value}')
    if email_value:
        print(f'Email: {email_value}')

    return 0


def load_config_command(args: argparse.Namespace) -> int:
    """Load and validate a configuration file.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    config_path = Path(args.file)

    if not config_path.exists():
        print(f'Error: Configuration file not found: {config_path}', file=sys.stderr)
        return 1

    try:
        with config_path.open() as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f'Error: Invalid YAML in configuration file: {e}', file=sys.stderr)
        return 1

    # Validate the configuration
    errors = validate_config(config, config_path)

    if errors:
        print(f'Configuration validation failed for {config_path}:', file=sys.stderr)
        for error in errors:
            print(f'  {error}', file=sys.stderr)
        return 1

    print(f'Configuration loaded successfully from {config_path}')
    return 0


def validate_config(config: dict[str, Any] | Any, config_path: Path) -> list[str]:  # noqa: ANN401
    """Validate a configuration dictionary.

    Args:
        config: Configuration dictionary
        config_path: Path to the configuration file

    Returns:
        List of error messages (empty if valid)

    """
    errors = []

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

    # Validate each user
    for i, user in enumerate(users):
        user_errors = validate_user(user, i + 1, config_path)
        errors.extend(user_errors)

    return errors


def validate_user(user: dict[str, Any] | Any, index: int, config_path: Path) -> list[str]:  # noqa: ANN401
    """Validate a user dictionary from configuration.

    Args:
        user: User dictionary
        index: User index (for error reporting)
        config_path: Path to the configuration file

    Returns:
        List of error messages (empty if valid)

    """
    errors = []

    if not isinstance(user, dict):
        errors.append(f'User at position {index} must be a dictionary')
        return errors

    # Validate name
    if 'name' in user:
        name_result = parse_name(str(user['name']))
        if name_result.is_failure():
            errors.append(
                f'Invalid name for user at position {index} in {config_path.name}: {name_result.error_or("")}'
            )

    # Validate age
    if 'age' in user:
        age_value = user['age']
        age_str = str(age_value) if isinstance(age_value, int) else str(age_value) if age_value else ''

        age_result = parse_age(age_str)
        if age_result.is_failure():
            errors.append(
                f'Invalid age for user at position {index} (line {index * 4 + 2}) in {config_path.name}: '
                f'{age_result.error_or("")}'
            )

    # Validate email
    if 'email' in user:
        email_result = parse_email(str(user['email']))
        if email_result.is_failure():
            errors.append(
                f'Invalid email for user at position {index} (line {index * 4 + 3}) in {config_path.name}: '
                f'{email_result.error_or("")}'
            )

    return errors


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)

    """
    parser = argparse.ArgumentParser(
        description='CLI Starter Template - Production-ready CLI with valid8r validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # add-user subcommand
    add_user_parser = subparsers.add_parser('add-user', help='Add a new user with validation')
    add_user_parser.add_argument('--name', type=str, help='User name')
    add_user_parser.add_argument('--age', type=str, help='User age')
    add_user_parser.add_argument('--email', type=str, help='User email')
    add_user_parser.add_argument('--interactive', action='store_true', help='Interactive mode with prompts')

    # load-config subcommand
    load_config_parser = subparsers.add_parser('load-config', help='Load and validate a configuration file')
    load_config_parser.add_argument('--file', type=str, required=True, help='Path to configuration file')

    args = parser.parse_args()

    if args.command == 'add-user':
        return add_user_command(args)
    if args.command == 'load-config':
        return load_config_command(args)
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
