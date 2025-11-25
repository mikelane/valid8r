#!/usr/bin/env python3
"""Rich Integration Example: Project Configuration Wizard.

This example demonstrates how to integrate valid8r with Rich for creating
beautiful, validated CLI applications.

Key Features:
- Rich panels and tables for success output
- Styled error messages with suggestions
- Progress bars for batch validation
- Interactive prompts with validation

Usage:
    python project_wizard.py --scenario=success
    python project_wizard.py --scenario=failure
    python project_wizard.py --scenario=batch
    python project_wizard.py --scenario=interactive
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    parse_email,
    parse_int,
    parse_url,
)

# Create Rich console (force color for CI/testing)
console = Console(force_terminal=True)

# Configurable delay for demos (set DEMO_DELAY=0 for tests)
DEMO_DELAY = float(os.environ.get('DEMO_DELAY', '0.1'))


def run_success_scenario() -> None:
    """Demonstrate successful validation with Rich styling.

    Shows:
    - Rich panels with success messages
    - Tables displaying validated data
    - Proper color styling
    """
    # Example project configuration
    project_data = {
        'name': 'My Awesome Project',
        'email': 'admin@example.com',
        'url': 'https://example.com',
        'port': '8080',
    }

    # Validate all fields
    validated_data = {}
    validation_errors = []

    # Validate email
    email_result = parse_email(project_data['email'])
    match email_result:
        case Success(email):
            validated_data['Email'] = f'{email.local}@{email.domain}'
        case Failure(error):
            validation_errors.append(f'Email: {error}')

    # Validate URL
    url_result = parse_url(project_data['url'])
    match url_result:
        case Success(url):
            validated_data['URL'] = f'{url.scheme}://{url.host}'
        case Failure(error):
            validation_errors.append(f'URL: {error}')

    # Validate port
    port_result = parse_int(project_data['port'])
    match port_result:
        case Success(port):
            validated_data['Port'] = str(port)
        case Failure(error):
            validation_errors.append(f'Port: {error}')

    # Display success panel
    console.print()
    console.print(
        Panel(
            '[bold green]✓ Project Configuration Validated Successfully![/bold green]\n\n'
            f'Project: [bold]{project_data["name"]}[/bold]',
            title='[bold cyan]Valid8r + Rich Integration[/bold cyan]',
            border_style='green',
        )
    )

    # Display validated data in a table
    table = Table(title='[bold]Validated Data[/bold]', show_header=True, header_style='bold magenta')
    table.add_column('Field', style='cyan')
    table.add_column('Value', style='green')

    for field, value in validated_data.items():
        table.add_row(field, value)

    console.print(table)
    console.print()


def run_failure_scenario() -> None:
    """Demonstrate validation failure with Rich error styling.

    Shows:
    - Error messages styled with Rich
    - Color highlighting for errors
    - Helpful suggestions for fixing issues
    """
    # Example project configuration with INVALID data
    project_data = {
        'name': 'My Broken Project',
        'email': 'not-an-email',
        'url': 'not a url',
        'port': 'not-a-number',
    }

    # Validate all fields
    validation_errors = []

    # Validate email
    email_result = parse_email(project_data['email'])
    match email_result:
        case Failure(error):
            validation_errors.append(('Email', project_data['email'], error))

    # Validate URL
    url_result = parse_url(project_data['url'])
    match url_result:
        case Failure(error):
            validation_errors.append(('URL', project_data['url'], error))

    # Validate port
    port_result = parse_int(project_data['port'])
    match port_result:
        case Failure(error):
            validation_errors.append(('Port', project_data['port'], error))

    # Display error panel
    console.print()
    console.print(
        Panel(
            f'[bold red]✗ Validation Errors Found ({len(validation_errors)})[/bold red]\n\n'
            f'Project: [bold]{project_data["name"]}[/bold]',
            title='[bold red]Validation Error[/bold red]',
            border_style='red',
        )
    )

    # Display errors in a table with suggestions
    table = Table(title='[bold red]Errors[/bold red]', show_header=True, header_style='bold red')
    table.add_column('Field', style='cyan')
    table.add_column('Invalid Value', style='yellow')
    table.add_column('Error', style='red')
    table.add_column('Suggestion', style='dim')

    suggestions = {
        'Email': 'Format: user@example.com',
        'URL': 'Format: https://example.com',
        'Port': 'Format: 1-65535 (integer)',
    }

    for field, value, error in validation_errors:
        suggestion = suggestions.get(field, 'Check format')
        table.add_row(field, value, error, suggestion)

    console.print(table)
    console.print()


def run_batch_scenario() -> None:
    """Demonstrate batch validation with Rich progress bars.

    Shows:
    - Rich progress bar
    - Progress updates during validation
    - Validation status for multiple items
    """
    # Example batch of email addresses to validate
    emails = [
        'user1@example.com',
        'user2@example.com',
        'invalid-email',
        'user3@example.com',
        'another-bad-email',
        'user4@example.com',
        'user5@example.com',
    ]

    console.print()
    console.print(Panel('[bold cyan]Batch Email Validation[/bold cyan]', border_style='cyan'))
    console.print()

    # Create progress bar
    with Progress(
        TextColumn('[bold blue]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task('[cyan]Validating emails...', total=len(emails))

        valid_count = 0
        invalid_count = 0

        for email_text in emails:
            # Simulate some processing time (configurable for tests)
            if DEMO_DELAY > 0:
                time.sleep(DEMO_DELAY)

            # Validate email
            result = parse_email(email_text)
            if result.is_success():
                valid_count += 1
            else:
                invalid_count += 1

            # Update progress
            progress.update(task, advance=1)

    # Display results
    console.print()
    results_table = Table(show_header=True, header_style='bold magenta')
    results_table.add_column('Status', style='bold')
    results_table.add_column('Count', justify='right')

    results_table.add_row('[green]✓ Valid[/green]', str(valid_count))
    results_table.add_row('[red]✗ Invalid[/red]', str(invalid_count))
    results_table.add_row('[bold]Total[/bold]', str(len(emails)))

    console.print(results_table)
    console.print()


def run_interactive_scenario() -> None:
    """Demonstrate interactive prompts with Rich styling.

    Shows:
    - Rich-styled prompts
    - Validation feedback during input
    - Styled error messages for invalid input
    """
    console.print()
    console.print(
        Panel(
            '[bold cyan]Interactive Project Setup[/bold cyan]\n\nEnter project details with real-time validation.',
            border_style='cyan',
        )
    )
    console.print()

    # In a real interactive scenario, we would prompt for input
    # For testing, we read from stdin
    console.print('[bold cyan]Email:[/bold cyan] ', end='')

    try:
        email_input = input()
    except EOFError:
        email_input = 'user@example.com'

    # Validate the input
    result = parse_email(email_input)

    match result:
        case Success(email):
            console.print(f'[green]✓ Valid email: {email.local}@{email.domain}[/green]')
            console.print()
        case Failure(error):
            console.print(f'[red]✗ Invalid email: {error}[/red]')
            console.print('[dim]Suggestion: Use format user@example.com[/dim]')
            console.print()


def main() -> None:
    """Main entry point for the Rich integration example."""
    parser = argparse.ArgumentParser(
        description='Valid8r + Rich Integration Example',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--scenario',
        choices=['success', 'failure', 'batch', 'interactive', 'visual_demo'],
        default='success',
        help='Which scenario to demonstrate',
    )

    args = parser.parse_args()

    # Run the selected scenario
    if args.scenario == 'success':
        run_success_scenario()
    elif args.scenario == 'failure':
        run_failure_scenario()
    elif args.scenario == 'batch':
        run_batch_scenario()
    elif args.scenario == 'interactive':
        run_interactive_scenario()
    elif args.scenario == 'visual_demo':
        # For the visual demo, show all scenarios
        run_success_scenario()
        run_failure_scenario()

    sys.exit(0)


if __name__ == '__main__':
    main()
