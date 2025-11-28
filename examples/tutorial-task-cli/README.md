# Task Manager CLI Tutorial Example

This directory contains the complete code from the **"Build a CLI in 10 Minutes"** tutorial.

## What This Example Demonstrates

- **Argument parsing** with validation using valid8r parsers
- **Interactive prompts** with retry logic using `prompt.ask()`
- **Multiple parsers**: `parse_int`, `parse_email`, `parse_bool`
- **Validator composition** with `validators.between()` and `validators.non_empty_string()`
- **Testing** interactive prompts with `MockInputContext`

## Quick Start

```bash
# Navigate to this directory
cd examples/tutorial-task-cli

# Add a task with command-line arguments
python task_cli.py add "Review PR" --priority 2

# Add a task with email notification
python task_cli.py add "Send report" --priority 1 --notify alice@example.com

# Add a task interactively
python task_cli.py add --interactive

# List all tasks
python task_cli.py list

# List only high-priority tasks
python task_cli.py list --priority 1
```

## Running Tests

```bash
# From the repository root
cd examples/tutorial-task-cli
pytest test_task_cli.py -v
```

## Files

| File | Description |
|------|-------------|
| `task_cli.py` | Complete CLI implementation |
| `test_task_cli.py` | Tests demonstrating MockInputContext |
| `README.md` | This file |

## Tutorial

See the full tutorial at: [Build a CLI in 10 Minutes](../../docs/tutorials/build-cli-in-10-minutes.md)

## Key Concepts

### 1. Custom Parser with Validation

```python
from valid8r import parsers, validators, Maybe

def parse_priority(text: str) -> Maybe[int]:
    """Parse and validate task priority (1-5)."""
    return parsers.parse_int(text).bind(
        validators.between(1, 5, error_message='Priority must be 1-5')
    )
```

### 2. Interactive Prompts with Retry

```python
from valid8r import prompt

priority = prompt.ask(
    'Priority (1-5): ',
    parser=parse_priority,
    default=3,
    retry=True,
)
```

### 3. Testing with MockInputContext

```python
from valid8r.testing import MockInputContext

def test_interactive_task():
    with MockInputContext(['Review PR', '2', 'no']):
        exit_code = add_task_interactive()
    assert exit_code == 0
```

## Next Steps

After completing this tutorial, explore:

- [Validators Guide](../../docs/user_guide/validators.rst) - Learn about all available validators
- [Parsers Reference](../../docs/user_guide/parsers.rst) - Explore all parser types
- [CLI Starter Template](../cli-starter-template/) - A more production-ready CLI template
