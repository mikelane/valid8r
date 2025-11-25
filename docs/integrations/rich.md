# Rich Integration

This guide demonstrates how to integrate **valid8r** with **[Rich](https://rich.readthedocs.io/)** to create beautiful, validated CLI applications with styled output, tables, progress bars, and interactive prompts.

## Why Integrate valid8r with Rich?

**Professional CLI Output**: Combine valid8r's robust validation with Rich's beautiful terminal rendering for polished user experiences.

**Clear Feedback**: Display validation success and failure with color-coded panels, tables, and helpful suggestions.

**Progress Tracking**: Show batch validation progress with Rich progress bars for long-running operations.

**Consistent Patterns**: Use the same valid8r parsers across CLI output, web APIs, and configuration while leveraging Rich for presentation.

## Installation

Rich must be installed separately:

```bash
pip install valid8r rich
```

Or with uv:

```bash
uv add valid8r rich
```

## Quick Start

### Success Display with Rich Panels

Display validated data in styled Rich panels:

```python
from rich.console import Console
from rich.panel import Panel
from valid8r.core.maybe import Success, Failure
from valid8r.core.parsers import parse_email

console = Console()

# Validate email
result = parse_email('user@example.com')

match result:
    case Success(email):
        console.print(
            Panel(
                f'[bold green]Valid email: {email.local}@{email.domain}[/bold green]',
                title='[bold cyan]Validation Success[/bold cyan]',
                border_style='green',
            )
        )
    case Failure(error):
        console.print(
            Panel(
                f'[bold red]Error: {error}[/bold red]',
                title='[bold red]Validation Failed[/bold red]',
                border_style='red',
            )
        )
```

**Output:**
```
╭─────────────────── Validation Success ────────────────────╮
│ Valid email: user@example.com                              │
╰────────────────────────────────────────────────────────────╯
```

### Error Display with Rich Tables

Display validation errors with suggestions in styled tables:

```python
from rich.console import Console
from rich.table import Table
from valid8r.core.maybe import Failure
from valid8r.core.parsers import parse_email, parse_url, parse_int

console = Console()

# Example validation data (with intentional errors)
inputs = {
    'email': 'not-an-email',
    'url': 'not a url',
    'port': 'not-a-number',
}

# Collect validation errors
errors = []
result = parse_email(inputs['email'])
match result:
    case Failure(error):
        errors.append(('Email', inputs['email'], error, 'Format: user@example.com'))

result = parse_url(inputs['url'])
match result:
    case Failure(error):
        errors.append(('URL', inputs['url'], error, 'Format: https://example.com'))

result = parse_int(inputs['port'])
match result:
    case Failure(error):
        errors.append(('Port', inputs['port'], error, 'Format: 1-65535 (integer)'))

# Display errors in a Rich table
table = Table(title='[bold red]Validation Errors[/bold red]')
table.add_column('Field', style='cyan')
table.add_column('Invalid Value', style='yellow')
table.add_column('Error', style='red')
table.add_column('Suggestion', style='dim')

for field, value, error, suggestion in errors:
    table.add_row(field, value, error, suggestion)

console.print(table)
```

**Output:**
```
               Validation Errors
┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field ┃ Invalid Value ┃ Error          ┃ Suggestion             ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Email │ not-an-email  │ Missing @-sign │ Format: user@example.  │
│ URL   │ not a url     │ Invalid format │ Format: https://exam...│
│ Port  │ not-a-number  │ Not an integer │ Format: 1-65535        │
└───────┴───────────────┴────────────────┴────────────────────────┘
```

## Key Integration Patterns

### 1. Success Panels with Validated Data Tables

Display validated configuration in a professional format:

```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from valid8r.core.maybe import Success, Failure
from valid8r.core.parsers import parse_email, parse_url, parse_int

console = Console()

def display_config(config: dict) -> None:
    """Display validated configuration with Rich styling."""
    validated = {}
    errors = []

    # Validate email
    match parse_email(config.get('email', '')):
        case Success(email):
            validated['Email'] = f'{email.local}@{email.domain}'
        case Failure(error):
            errors.append(('Email', error))

    # Validate URL
    match parse_url(config.get('url', '')):
        case Success(url):
            validated['URL'] = f'{url.scheme}://{url.host}'
        case Failure(error):
            errors.append(('URL', error))

    # Validate port
    match parse_int(config.get('port', '')):
        case Success(port):
            validated['Port'] = str(port)
        case Failure(error):
            errors.append(('Port', error))

    if errors:
        console.print(Panel(
            f'[bold red]Validation failed with {len(errors)} error(s)[/bold red]',
            border_style='red',
        ))
    else:
        console.print(Panel(
            '[bold green]Configuration validated successfully![/bold green]',
            title='[bold cyan]Valid8r + Rich[/bold cyan]',
            border_style='green',
        ))

        # Display validated data in a table
        table = Table(title='[bold]Validated Configuration[/bold]')
        table.add_column('Field', style='cyan')
        table.add_column('Value', style='green')

        for field, value in validated.items():
            table.add_row(field, value)

        console.print(table)

# Example usage
display_config({
    'email': 'admin@example.com',
    'url': 'https://api.example.com',
    'port': '8080',
})
```

### 2. Batch Validation with Progress Bars

Track validation progress for large datasets:

```python
import os
from rich.console import Console
from rich.progress import Progress, BarColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from valid8r.core.parsers import parse_email

console = Console()

def validate_email_batch(emails: list[str]) -> dict:
    """Validate a batch of emails with progress tracking."""
    # Use configurable delay for demos (0 for tests)
    demo_delay = float(os.environ.get('DEMO_DELAY', '0.1'))

    valid_count = 0
    invalid_count = 0

    with Progress(
        TextColumn('[bold blue]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task('[cyan]Validating emails...', total=len(emails))

        for email_text in emails:
            # Optional delay for visual demo
            if demo_delay > 0:
                import time
                time.sleep(demo_delay)

            result = parse_email(email_text)
            if result.is_success():
                valid_count += 1
            else:
                invalid_count += 1

            progress.update(task, advance=1)

    return {'valid': valid_count, 'invalid': invalid_count, 'total': len(emails)}

# Display results
emails = [
    'user1@example.com',
    'user2@example.com',
    'invalid-email',
    'user3@example.com',
]

results = validate_email_batch(emails)

# Show results table
results_table = Table(show_header=True, header_style='bold magenta')
results_table.add_column('Status', style='bold')
results_table.add_column('Count', justify='right')

results_table.add_row('[green]Valid[/green]', str(results['valid']))
results_table.add_row('[red]Invalid[/red]', str(results['invalid']))
results_table.add_row('[bold]Total[/bold]', str(results['total']))

console.print(results_table)
```

**Note:** Set `DEMO_DELAY=0` in tests to skip the visual delay:
```bash
DEMO_DELAY=0 pytest tests/
```

### 3. Interactive Prompts with Validation

Create interactive prompts with real-time validation feedback:

```python
from rich.console import Console
from rich.panel import Panel
from valid8r.core.maybe import Success, Failure
from valid8r.core.parsers import parse_email

console = Console()

def prompt_with_validation(prompt_text: str, parser) -> any:
    """Prompt for input with validation feedback."""
    console.print(Panel(
        '[bold cyan]Interactive Input[/bold cyan]\n\n'
        'Enter values with real-time validation.',
        border_style='cyan',
    ))

    while True:
        console.print(f'[bold cyan]{prompt_text}:[/bold cyan] ', end='')
        try:
            user_input = input()
        except EOFError:
            return None

        result = parser(user_input)

        match result:
            case Success(value):
                console.print(f'[green]Valid input accepted.[/green]')
                return value
            case Failure(error):
                console.print(f'[red]Invalid: {error}[/red]')
                console.print('[dim]Please try again.[/dim]')

# Example usage
# email = prompt_with_validation('Email address', parse_email)
```

### 4. Validated Data Display Table

Create reusable components for displaying validated data:

```python
from rich.console import Console
from rich.table import Table
from valid8r.core.maybe import Success, Failure

console = Console()

def create_validation_table(title: str) -> Table:
    """Create a styled table for validation results."""
    table = Table(title=title, show_header=True, header_style='bold magenta')
    table.add_column('Field', style='cyan')
    table.add_column('Value', style='green')
    table.add_column('Status', style='bold')
    return table

def add_result_row(table: Table, field: str, result) -> None:
    """Add a validation result row to the table."""
    match result:
        case Success(value):
            table.add_row(field, str(value), '[green]Valid[/green]')
        case Failure(error):
            table.add_row(field, f'[red]{error}[/red]', '[red]Invalid[/red]')

# Example usage
from valid8r.core.parsers import parse_email, parse_int, parse_url

table = create_validation_table('[bold]Configuration Validation[/bold]')

add_result_row(table, 'Email', parse_email('admin@example.com'))
add_result_row(table, 'Port', parse_int('8080'))
add_result_row(table, 'URL', parse_url('https://api.example.com'))

console.print(table)
```

## Best Practices

### 1. Use Pattern Matching for Clean Code

Python's pattern matching works elegantly with valid8r's `Success` and `Failure` types:

```python
from valid8r.core.maybe import Success, Failure

match result:
    case Success(value):
        # Handle success
        console.print(f'[green]Success: {value}[/green]')
    case Failure(error):
        # Handle failure
        console.print(f'[red]Error: {error}[/red]')
```

### 2. Consistent Color Scheme

Follow Rich color conventions for user experience:

- **Green**: Success, valid data, positive feedback
- **Red**: Errors, invalid data, warnings
- **Cyan**: Information, prompts, headers
- **Yellow**: Invalid input values, caution
- **Dim**: Suggestions, hints, secondary information
- **Bold**: Important text, field names, emphasis

### 3. Provide Helpful Suggestions

When displaying errors, include suggestions for fixing them:

```python
suggestions = {
    'Email': 'Format: user@example.com',
    'URL': 'Format: https://example.com',
    'Port': 'Integer between 1 and 65535',
    'Phone': 'Format: (XXX) XXX-XXXX',
}
```

### 4. Make Delays Configurable

For visual demos with progress bars, use environment variables:

```python
import os
import time

DEMO_DELAY = float(os.environ.get('DEMO_DELAY', '0.1'))

# Use in loops
for item in items:
    # Process item...
    if DEMO_DELAY > 0:
        time.sleep(DEMO_DELAY)
```

Tests can set `DEMO_DELAY=0` for fast execution.

### 5. Force Terminal Colors for CI

When running in CI/CD environments, force terminal output:

```python
from rich.console import Console

# Force color output (useful for CI/testing)
console = Console(force_terminal=True)
```

## Complete Example

See the full project wizard example at `examples/rich_integration/project_wizard.py`:

```bash
# Run different scenarios
python examples/rich_integration/project_wizard.py --scenario=success
python examples/rich_integration/project_wizard.py --scenario=failure
python examples/rich_integration/project_wizard.py --scenario=batch
python examples/rich_integration/project_wizard.py --scenario=interactive
```

The example demonstrates:
- Success panels with validated data tables
- Error tables with suggestions
- Progress bars for batch validation
- Interactive prompts with validation feedback

## Testing Rich Integration

### Unit Testing

Test Rich output by capturing console output:

```python
from io import StringIO
from rich.console import Console

def test_success_panel():
    """Test that success panel displays correctly."""
    output = StringIO()
    console = Console(file=output, force_terminal=True)

    # Run your Rich output code...

    result = output.getvalue()
    assert 'Success' in result
    assert '\x1b[' in result  # ANSI codes present
```

### BDD Testing

Write Gherkin scenarios for CLI behavior:

```gherkin
Feature: Rich Integration with Valid8r

  Scenario: Display validation success with Rich panels
    Given the project wizard is available
    When I run the wizard with the success scenario
    Then I should see a success panel with validated data
    And the output should include Rich styling

  Scenario: Display validation errors with Rich tables
    Given the project wizard is available
    When I run the wizard with the failure scenario
    Then I should see an error panel with error count
    And I should see a table with validation errors
```

## API Reference

### Console Setup

```python
from rich.console import Console

# Basic console
console = Console()

# Force terminal (for CI/testing)
console = Console(force_terminal=True)

# Capture output (for testing)
from io import StringIO
output = StringIO()
console = Console(file=output, force_terminal=True)
```

### Panel Creation

```python
from rich.panel import Panel

# Success panel
Panel(
    '[bold green]Success message[/bold green]',
    title='[bold cyan]Title[/bold cyan]',
    border_style='green',
)

# Error panel
Panel(
    '[bold red]Error message[/bold red]',
    title='[bold red]Error[/bold red]',
    border_style='red',
)
```

### Table Creation

```python
from rich.table import Table

table = Table(
    title='[bold]Table Title[/bold]',
    show_header=True,
    header_style='bold magenta',
)
table.add_column('Field', style='cyan')
table.add_column('Value', style='green')
table.add_row('Email', 'user@example.com')
```

### Progress Bar

```python
from rich.progress import Progress, BarColumn, TaskProgressColumn, TextColumn

with Progress(
    TextColumn('[bold blue]{task.description}'),
    BarColumn(),
    TaskProgressColumn(),
    console=console,
) as progress:
    task = progress.add_task('[cyan]Processing...', total=100)
    for i in range(100):
        # Do work...
        progress.update(task, advance=1)
```

## Related Documentation

- [Rich Official Documentation](https://rich.readthedocs.io/)
- [valid8r Parsers](../api/parsers.html)
- [Typer Integration](typer.md) - CLI framework that uses Rich
- [Pydantic Integration](pydantic.md) - Data validation
