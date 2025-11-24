# Rich Integration Example

This example demonstrates how to integrate **valid8r** with **Rich** to create beautiful, validated CLI applications.

## Overview

The project wizard showcases:

- **Success Panels**: Display validated data in styled Rich panels and tables
- **Error Handling**: Show validation errors with helpful suggestions and color highlighting
- **Progress Bars**: Track batch validation progress with Rich progress bars
- **Interactive Prompts**: Validate user input with real-time feedback

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Or install directly:

```bash
pip install valid8r rich
```

## Usage

The example supports multiple scenarios to demonstrate different features:

### Success Scenario

Shows successful validation with Rich panels and tables:

```bash
python project_wizard.py --scenario=success
```

**Output Features**:
- Green success panel with project name
- Table displaying validated fields (email, URL, port)
- Professional styling with colors and borders

### Failure Scenario

Demonstrates validation errors with Rich styling:

```bash
python project_wizard.py --scenario=failure
```

**Output Features**:
- Red error panel with error count
- Table showing invalid values, errors, and suggestions
- Color-coded error messages

### Batch Processing

Shows batch validation with progress tracking:

```bash
python project_wizard.py --scenario=batch
```

**Output Features**:
- Rich progress bar with task description
- Real-time progress updates during validation
- Summary table with valid/invalid counts

### Interactive Mode

Demonstrates interactive prompts with validation:

```bash
python project_wizard.py --scenario=interactive
```

**Output Features**:
- Styled input prompts using Rich
- Real-time validation feedback
- Error messages with suggestions for invalid input

## Key Integration Patterns

### 1. Success Validation with Rich Panels

```python
from rich.console import Console
from rich.panel import Panel
from valid8r.core.parsers import parse_email

console = Console()

# Validate email
result = parse_email("user@example.com")
match result:
    case Success(email):
        console.print(
            Panel(
                f"[green]✓ Valid email: {email.local}@{email.domain}[/green]",
                border_style="green",
            )
        )
```

### 2. Error Handling with Rich Tables

```python
from rich.table import Table
from valid8r.core.parsers import parse_email

# Collect validation errors
errors = []
result = parse_email("invalid-email")
match result:
    case Failure(error):
        errors.append(("Email", "invalid-email", error, "Format: user@example.com"))

# Display errors in a Rich table
table = Table(title="[bold red]Validation Errors[/bold red]")
table.add_column("Field", style="cyan")
table.add_column("Invalid Value", style="yellow")
table.add_column("Error", style="red")
table.add_column("Suggestion", style="dim")

for field, value, error, suggestion in errors:
    table.add_row(field, value, error, suggestion)

console.print(table)
```

### 3. Batch Processing with Progress Bars

```python
from rich.progress import Progress, BarColumn, TaskProgressColumn, TextColumn
from valid8r.core.parsers import parse_email

emails = ["user1@example.com", "invalid", "user2@example.com"]

with Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
) as progress:
    task = progress.add_task("[cyan]Validating emails...", total=len(emails))

    for email_text in emails:
        result = parse_email(email_text)
        # Process result...
        progress.update(task, advance=1)
```

## Design Principles

1. **Monadic Validation**: Use `match` statements to handle `Success` and `Failure` cases elegantly
2. **Rich Styling**: Apply consistent color schemes (green for success, red for errors, cyan for info)
3. **User Experience**: Provide helpful error messages with suggestions
4. **Professional Output**: Use panels, tables, and progress bars for polished CLI appearance

## Example Output

When you run the example, you'll see output like this:

```
╭─────────────────────── Valid8r + Rich Integration ────────────────────────╮
│ ✓ Project Configuration Validated Successfully!                           │
│                                                                            │
│ Project: My Awesome Project                                                │
╰────────────────────────────────────────────────────────────────────────────╯
         Validated Data
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Field ┃ Value             ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Email │ admin@example.com │
│ URL   │ https://example.com │
│ Port  │ 8080              │
└───────┴───────────────────┘
```

## Learn More

- [valid8r Documentation](https://github.com/mikelane/valid8r)
- [Rich Documentation](https://rich.readthedocs.io/)

## License

This example is part of the valid8r project and is released under the MIT License.
