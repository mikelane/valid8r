#!/usr/bin/env python
"""Task Manager CLI - A simple task manager built in 10 minutes with valid8r.

This is the complete code from the "Build a CLI in 10 Minutes" tutorial.
It demonstrates:
- Argument parsing with validation using valid8r parsers
- Interactive prompts with retry logic
- Using 3+ parsers (parse_int, parse_email, parse_bool)
- Combining validators with logical operators

Run examples:
    python task_cli.py add "Review PR" --priority 3
    python task_cli.py add "Send report" --priority 1 --notify alice@example.com
    python task_cli.py add --interactive
    python task_cli.py list
    python task_cli.py list --priority 3

"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from valid8r import (
    parsers,
    prompt,
    validators,
)
from valid8r.core.maybe import (
    Failure,
    Success,
)

if TYPE_CHECKING:
    from valid8r import Maybe

# Storage file for tasks (in current directory)
TASKS_FILE = Path('tasks.json')


def load_tasks() -> list[dict]:
    """Load tasks from JSON file."""
    if TASKS_FILE.exists():
        with TASKS_FILE.open() as f:
            return json.load(f)
    return []


def save_tasks(tasks: list[dict]) -> None:
    """Save tasks to JSON file."""
    with TASKS_FILE.open('w') as f:
        json.dump(tasks, f, indent=2)


def parse_priority(text: str) -> Maybe[int]:
    """Parse and validate task priority (1-5).

    Priority levels:
        1 = Critical (must do today)
        2 = High (important)
        3 = Medium (default)
        4 = Low (when you have time)
        5 = Someday (nice to have)
    """
    return parsers.parse_int(text).bind(validators.between(1, 5, error_message='Priority must be 1-5'))


def add_task_interactive() -> int:
    """Add a task using interactive prompts.

    Returns:
        Exit code (0 for success, 1 for error)

    """
    print('Add a new task')
    print('-' * 40)

    # Get task description (simple string input)
    description = prompt.ask(
        'Task description: ',
        validator=validators.non_empty_string('Description cannot be empty'),
        retry=True,
    )

    if description.is_failure():
        print(f'Error: {description.error_or("")}', file=sys.stderr)
        return 1

    # Get priority with validation (1-5)
    priority = prompt.ask(
        'Priority (1-5, where 1=Critical): ',
        parser=parse_priority,
        default=3,
        retry=True,
    )

    if priority.is_failure():
        print(f'Error: {priority.error_or("")}', file=sys.stderr)
        return 1

    # Ask if user wants email notification
    wants_notification = prompt.ask(
        'Enable email notification? (yes/no): ',
        parser=parsers.parse_bool,
        default=False,
        retry=True,
    )

    notify_email = None
    default_notification = False
    if wants_notification.value_or(default_notification):
        email_result = prompt.ask(
            'Notification email: ',
            parser=parsers.parse_email,
            retry=True,
        )
        if email_result.is_failure():
            print(f'Error: {email_result.error_or("")}', file=sys.stderr)
            return 1
        email = email_result.value_or(None)
        if email:
            notify_email = f'{email.local}@{email.domain}'

    # Create and save the task
    task = {
        'description': description.value_or(''),
        'priority': priority.value_or(3),
        'notify_email': notify_email,
        'completed': False,
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    print()
    print('Task added successfully!')
    print(f'  Description: {task["description"]}')
    print(f'  Priority: {task["priority"]}')
    if task['notify_email']:
        print(f'  Notify: {task["notify_email"]}')

    return 0


def add_task_command(args: argparse.Namespace) -> int:
    """Add a task from command-line arguments or interactively.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    if args.interactive:
        return add_task_interactive()

    # Validate description
    if not args.description:
        print('Error: Task description is required', file=sys.stderr)
        print('Use: python task_cli.py add "Your task description"', file=sys.stderr)
        return 1

    # Validate priority
    priority = 3  # default
    if args.priority:
        priority_result = parse_priority(args.priority)
        match priority_result:
            case Success(value):
                priority = value
            case Failure(error):
                print(f'Error: {error}', file=sys.stderr)
                return 1

    # Validate notification email if provided
    notify_email = None
    if args.notify:
        email_result = parsers.parse_email(args.notify)
        match email_result:
            case Success(email):
                notify_email = f'{email.local}@{email.domain}'
            case Failure(error):
                print(f'Error: Invalid email: {error}', file=sys.stderr)
                return 1

    # Create and save the task
    task = {
        'description': args.description,
        'priority': priority,
        'notify_email': notify_email,
        'completed': False,
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    print('Task added successfully!')
    print(f'  Description: {task["description"]}')
    print(f'  Priority: {task["priority"]}')
    if task['notify_email']:
        print(f'  Notify: {task["notify_email"]}')

    return 0


def list_tasks_command(args: argparse.Namespace) -> int:
    """List tasks, optionally filtered by priority.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success)

    """
    tasks = load_tasks()

    if not tasks:
        print('No tasks found. Add one with: python task_cli.py add "Your task"')
        return 0

    # Filter by priority if specified
    if args.priority:
        priority_result = parse_priority(args.priority)
        match priority_result:
            case Success(priority):
                tasks = [t for t in tasks if t.get('priority') == priority]
            case Failure(error):
                print(f'Error: {error}', file=sys.stderr)
                return 1

    if not tasks:
        print('No tasks match your filter.')
        return 0

    # Sort by priority (1 = highest priority)
    tasks = sorted(tasks, key=lambda t: t.get('priority', 3))

    # Display tasks
    print('Tasks')
    print('=' * 50)
    for i, task in enumerate(tasks, 1):
        priority_label = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW', 5: 'SOMEDAY'}
        priority = task.get('priority', 3)
        status = 'DONE' if task.get('completed') else 'TODO'

        print(f'{i}. [{status}] [{priority_label.get(priority, "?")}] {task["description"]}')
        if task.get('notify_email'):
            print(f'   Notify: {task["notify_email"]}')

    return 0


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)

    """
    parser = argparse.ArgumentParser(
        description='Task Manager CLI - Built with valid8r',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python task_cli.py add "Review PR" --priority 2
  python task_cli.py add "Send report" --priority 1 --notify alice@example.com
  python task_cli.py add --interactive
  python task_cli.py list
  python task_cli.py list --priority 1
        """,
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # add subcommand
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', nargs='?', help='Task description')
    add_parser.add_argument('--priority', '-p', help='Priority level (1-5, default: 3)')
    add_parser.add_argument('--notify', '-n', help='Email address for notifications')
    add_parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    # list subcommand
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--priority', '-p', help='Filter by priority (1-5)')

    args = parser.parse_args()

    if args.command == 'add':
        return add_task_command(args)
    if args.command == 'list':
        return list_tasks_command(args)

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
