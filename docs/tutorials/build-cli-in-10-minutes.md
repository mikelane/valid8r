# Build a CLI in 10 Minutes

Welcome! In this tutorial, you'll build a **Task Manager CLI** with robust input validation in just 10 minutes. By the end, you'll have a working command-line tool that validates user input, provides helpful error messages, and even has tests.

**What you'll learn:**
- Parse and validate command-line arguments
- Create interactive prompts with retry logic
- Use multiple parsers (integers, emails, booleans)
- Test interactive prompts with `MockInputContext`

**Prerequisites:**
- Python 3.11+
- Basic Python knowledge (functions, if/else, pattern matching)

Let's get started!

---

## Step 1: Setup (1 minute)

First, create a new directory and install valid8r:

```bash
mkdir task-cli
cd task-cli
pip install valid8r
```

Or with uv:

```bash
mkdir task-cli
cd task-cli
uv init
uv add valid8r
```

Create a new file called `task_cli.py`:

```bash
touch task_cli.py
```

**Checkpoint:** You should be at **1 minute** now.

---

## Step 2: Basic Structure (2 minutes)

Open `task_cli.py` and add the basic CLI structure:

```python
#!/usr/bin/env python
"""Task Manager CLI - Built with valid8r."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Storage file for tasks
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


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Task Manager CLI')
    subparsers = parser.add_subparsers(dest='command')

    # add subcommand
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', help='Task description')
    add_parser.add_argument('--priority', '-p', help='Priority (1-5)')

    # list subcommand
    subparsers.add_parser('list', help='List all tasks')

    args = parser.parse_args()

    if args.command == 'add':
        return add_task(args)
    if args.command == 'list':
        return list_tasks()

    parser.print_help()
    return 1


def add_task(args: argparse.Namespace) -> int:
    """Add a task (we'll add validation next!)."""
    task = {
        'description': args.description,
        'priority': int(args.priority) if args.priority else 3,
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f'Added: {task["description"]}')
    return 0


def list_tasks() -> int:
    """List all tasks."""
    tasks = load_tasks()
    if not tasks:
        print('No tasks yet!')
        return 0

    for i, task in enumerate(tasks, 1):
        print(f'{i}. [{task.get("priority", 3)}] {task["description"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

Try it out:

```bash
python task_cli.py add "Review PR" --priority 2
python task_cli.py list
```

But what happens if someone enters an invalid priority?

```bash
python task_cli.py add "Test" --priority "high"
# Crash! ValueError: invalid literal for int()
```

Let's fix that with valid8r!

**Checkpoint:** You should be at **3 minutes** now.

---

## Step 3: Add Input Validation (2 minutes)

Now let's add proper validation. Update your imports and add a priority parser:

```python
#!/usr/bin/env python
"""Task Manager CLI - Built with valid8r."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from valid8r import parsers, validators
from valid8r.core.maybe import Failure, Success

if TYPE_CHECKING:
    from valid8r import Maybe

# Storage file for tasks
TASKS_FILE = Path('tasks.json')


def parse_priority(text: str) -> Maybe[int]:
    """Parse and validate task priority (1-5).

    Priority levels:
        1 = Critical
        2 = High
        3 = Medium (default)
        4 = Low
        5 = Someday
    """
    return parsers.parse_int(text).bind(
        validators.between(1, 5, error_message='Priority must be 1-5')
    )
```

This is the magic of valid8r! Let's break it down:

1. `parsers.parse_int(text)` - Tries to parse the string as an integer, returns `Success(int)` or `Failure(error)`
2. `.bind(validators.between(1, 5))` - If parsing succeeded, validates the value is between 1 and 5

Now update the `add_task` function to use our validator:

```python
def add_task(args: argparse.Namespace) -> int:
    """Add a task with validation."""
    # Validate priority if provided
    priority = 3  # default
    if args.priority:
        result = parse_priority(args.priority)
        match result:
            case Success(value):
                priority = value
            case Failure(error):
                print(f'Error: {error}', file=sys.stderr)
                return 1

    task = {
        'description': args.description,
        'priority': priority,
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f'Added: {task["description"]} (priority: {priority})')
    return 0
```

Try it now:

```bash
python task_cli.py add "Test" --priority "high"
# Error: Input must be a valid integer

python task_cli.py add "Test" --priority 10
# Error: Priority must be 1-5

python task_cli.py add "Test" --priority 2
# Added: Test (priority: 2)
```

Nice! Clear error messages instead of crashes.

**Checkpoint:** You should be at **5 minutes** now.

---

## Step 4: Interactive Prompts (2 minutes)

Let's add an interactive mode that prompts the user for input. Add this import:

```python
from valid8r import parsers, prompt, validators
```

And add the `--interactive` flag to your add subcommand:

```python
add_parser.add_argument('--interactive', '-i', action='store_true')
```

Make the description optional:

```python
add_parser.add_argument('description', nargs='?', help='Task description')
```

Now add the interactive function:

```python
def add_task_interactive() -> int:
    """Add a task using interactive prompts."""
    print('Add a new task')
    print('-' * 40)

    # Get description
    description = prompt.ask(
        'Task description: ',
        validator=validators.non_empty_string('Description cannot be empty'),
        retry=True,
    )
    if description.is_failure():
        return 1

    # Get priority with default
    priority = prompt.ask(
        'Priority (1-5): ',
        parser=parse_priority,
        default=3,
        retry=True,
    )
    if priority.is_failure():
        return 1

    task = {
        'description': description.value_or(''),
        'priority': priority.value_or(3),
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    print(f'\nAdded: {task["description"]} (priority: {task["priority"]})')
    return 0
```

Update `add_task` to handle interactive mode:

```python
def add_task(args: argparse.Namespace) -> int:
    """Add a task with validation."""
    if args.interactive:
        return add_task_interactive()

    if not args.description:
        print('Error: Description required (or use --interactive)', file=sys.stderr)
        return 1

    # ... rest of the function
```

Try it:

```bash
python task_cli.py add --interactive
# Task description: Review PR
# Priority (1-5): 2
# Added: Review PR (priority: 2)
```

The `retry=True` option means invalid input shows an error and prompts again, instead of failing immediately!

**Checkpoint:** You should be at **7 minutes** now.

---

## Step 5: Email Notifications (2 minutes)

Let's add email notification support using `parse_email`. Add a notify flag:

```python
add_parser.add_argument('--notify', '-n', help='Email for notifications')
```

Update the non-interactive `add_task`:

```python
def add_task(args: argparse.Namespace) -> int:
    """Add a task with validation."""
    if args.interactive:
        return add_task_interactive()

    if not args.description:
        print('Error: Description required (or use --interactive)', file=sys.stderr)
        return 1

    # Validate priority
    priority = 3
    if args.priority:
        result = parse_priority(args.priority)
        match result:
            case Success(value):
                priority = value
            case Failure(error):
                print(f'Error: {error}', file=sys.stderr)
                return 1

    # Validate email if provided
    notify_email = None
    if args.notify:
        result = parsers.parse_email(args.notify)
        match result:
            case Success(email):
                notify_email = f'{email.local}@{email.domain}'
            case Failure(error):
                print(f'Error: Invalid email: {error}', file=sys.stderr)
                return 1

    task = {
        'description': args.description,
        'priority': priority,
        'notify_email': notify_email,
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    print(f'Added: {task["description"]} (priority: {priority})')
    if notify_email:
        print(f'  Will notify: {notify_email}')
    return 0
```

And update the interactive version to ask about notifications:

```python
def add_task_interactive() -> int:
    """Add a task using interactive prompts."""
    print('Add a new task')
    print('-' * 40)

    description = prompt.ask(
        'Task description: ',
        validator=validators.non_empty_string('Description cannot be empty'),
        retry=True,
    )
    if description.is_failure():
        return 1

    priority = prompt.ask(
        'Priority (1-5): ',
        parser=parse_priority,
        default=3,
        retry=True,
    )
    if priority.is_failure():
        return 1

    # Ask about notifications using parse_bool
    wants_notification = prompt.ask(
        'Enable email notification? (yes/no): ',
        parser=parsers.parse_bool,
        default=False,
        retry=True,
    )

    notify_email = None
    if wants_notification.value_or(False):
        email_result = prompt.ask(
            'Notification email: ',
            parser=parsers.parse_email,
            retry=True,
        )
        if email_result.is_success():
            email = email_result.value_or(None)
            if email:
                notify_email = f'{email.local}@{email.domain}'

    task = {
        'description': description.value_or(''),
        'priority': priority.value_or(3),
        'notify_email': notify_email,
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    print(f'\nAdded: {task["description"]} (priority: {task["priority"]})')
    if notify_email:
        print(f'  Will notify: {notify_email}')
    return 0
```

Try it:

```bash
python task_cli.py add "Deploy" --priority 1 --notify "team@company.com"
# Added: Deploy (priority: 1)
#   Will notify: team@company.com

python task_cli.py add "Test" --notify "not-an-email"
# Error: Invalid email: Must be a valid email address
```

**Checkpoint:** You should be at **9 minutes** now.

---

## Step 6: Write a Test (1 minute)

Create `test_task_cli.py`:

```python
"""Tests for Task Manager CLI."""

import json
from pathlib import Path

import pytest

from valid8r.testing import MockInputContext, assert_maybe_success, assert_maybe_failure

from task_cli import parse_priority, add_task_interactive


class DescribeParsePriority:
    """Tests for priority validation."""

    def it_accepts_valid_priorities(self) -> None:
        assert assert_maybe_success(parse_priority('1'), 1)
        assert assert_maybe_success(parse_priority('3'), 3)
        assert assert_maybe_success(parse_priority('5'), 5)

    def it_rejects_out_of_range(self) -> None:
        assert assert_maybe_failure(parse_priority('0'), '1-5')
        assert assert_maybe_failure(parse_priority('6'), '1-5')

    def it_rejects_non_integers(self) -> None:
        assert parse_priority('high').is_failure()
        assert parse_priority('').is_failure()


class DescribeInteractiveMode:
    """Tests for interactive prompts using MockInputContext."""

    def it_creates_task_from_prompts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        # Simulate user input
        with MockInputContext(['Review PR', '2', 'no']):
            exit_code = add_task_interactive()

        assert exit_code == 0

        with tasks_file.open() as f:
            tasks = json.load(f)

        assert len(tasks) == 1
        assert tasks[0]['description'] == 'Review PR'
        assert tasks[0]['priority'] == 2
```

Run the tests:

```bash
pip install pytest
pytest test_task_cli.py -v
```

**Congratulations!** You've built a complete CLI with validation in 10 minutes!

---

## What We Learned

In this tutorial, you learned how to:

1. **Parse and validate input** using `parsers.parse_int()` and `validators.between()`
2. **Chain validators** using `.bind()` for pipeline-style validation
3. **Create interactive prompts** with `prompt.ask()` and automatic retry
4. **Use multiple parsers**: `parse_int`, `parse_email`, `parse_bool`
5. **Handle errors elegantly** with pattern matching on `Success` and `Failure`
6. **Test interactive code** using `MockInputContext`

## Key Concepts

### The Maybe Pattern

valid8r uses `Success` and `Failure` types instead of exceptions:

```python
result = parsers.parse_int("42")

match result:
    case Success(value):
        print(f"Got: {value}")
    case Failure(error):
        print(f"Error: {error}")
```

### Chaining Validators

Use `.bind()` to chain parsing and validation:

```python
# Parse as int, then validate range
result = parsers.parse_int(text).bind(validators.between(1, 100))
```

### Interactive Prompts

`prompt.ask()` handles prompting, parsing, validation, and retries:

```python
age = prompt.ask(
    'Your age: ',
    parser=parsers.parse_int,
    validator=validators.minimum(0),
    default=18,
    retry=True,  # Keep asking until valid
)
```

## Next Steps

Now that you've built a basic CLI, explore:

- **[Validators Guide](../user_guide/validators.rst)** - All available validators and how to combine them
- **[Parsers Reference](../user_guide/parsers.rst)** - Every parser type (dates, URLs, IPs, UUIDs...)
- **[CLI Starter Template](../../examples/cli-starter-template/)** - A production-ready CLI template
- **[Testing Guide](../development/testing.rst)** - Advanced testing patterns

## Complete Code

The complete code for this tutorial is available at:
[examples/tutorial-task-cli/](../../examples/tutorial-task-cli/)

---

**Happy coding!** If you found this tutorial helpful, consider [starring valid8r on GitHub](https://github.com/mikelane/valid8r).
