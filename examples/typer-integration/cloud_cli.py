"""Cloud Infrastructure CLI - Complete Typer Integration Example.

This example demonstrates all valid8r + Typer integration patterns:
1. validator_callback() for option validation
2. ValidatedType for custom parameter types
3. validated_prompt() for interactive mode

A fictional cloud infrastructure management CLI with realistic validation needs.
"""

from __future__ import annotations

from typing import Annotated

import typer

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.integrations.typer import (
    ValidatedType,
    validated_prompt,
    validator_callback,
)

app = typer.Typer(help='Cloud Infrastructure Management CLI')

# ============================================================================
# Pattern 1: validator_callback() - Recommended for simple validations
# ============================================================================


def port_parser(text: str | None) -> parsers.Maybe[int]:
    """Parse and validate port number (1-65535)."""
    return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))


port_callback = validator_callback(port_parser, error_prefix='Port')


def region_parser(text: str | None) -> parsers.Maybe[str]:
    """Parse and validate cloud region."""
    valid_regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']

    result = parsers.parse_str(text)
    if result.is_failure():
        return result

    if result.value_or('') not in valid_regions:
        from valid8r.core.maybe import Maybe

        return Maybe.failure(f'Invalid region. Must be one of: {", ".join(valid_regions)}')

    return result


region_callback = validator_callback(region_parser, error_prefix='Region')


@app.command()
def deploy(
    service: Annotated[str, typer.Argument(help='Service name to deploy')],
    region: Annotated[
        str, typer.Option('--region', '-r', callback=region_callback, help='AWS region (us-east-1, us-west-2, etc.)')
    ],
    port: Annotated[int, typer.Option('--port', '-p', callback=port_callback, help='Service port (1-65535)')] = 8080,
    email: Annotated[
        str,
        typer.Option(
            '--notify', callback=validator_callback(parsers.parse_email), help='Email for deployment notifications'
        ),
    ]
    | None = None,
) -> None:
    """Deploy a service to the specified region.

    Example:
        cloud_cli.py deploy my-api --region us-east-1 --port 8080 --notify admin@example.com

    """
    from valid8r.core.parsers import EmailAddress

    typer.secho(f'\n✓ Deploying service: {service}', fg=typer.colors.GREEN, bold=True)
    typer.echo(f'  Region: {region}')
    typer.echo(f'  Port: {port}')

    if email and isinstance(email, EmailAddress):
        typer.echo(f'  Notifications: {email.local}@{email.domain}')

    typer.secho('\n✓ Deployment successful!', fg=typer.colors.GREEN)


# ============================================================================
# Pattern 2: ValidatedType - For custom types used across multiple commands
# ============================================================================

# Create reusable custom types
ProjectId = ValidatedType(
    lambda t: parsers.parse_str(t).bind(validators.matches(r'^[a-z][a-z0-9-]{2,39}$')),
    help_text='Project ID (lowercase, alphanumeric with hyphens, 3-40 chars)',
)


# AWS ARN validator
def arn_parser(text: str | None) -> parsers.Maybe[str]:
    """Parse and validate AWS ARN format."""
    import re

    result = parsers.parse_str(text)
    if result.is_failure():
        return result

    arn_pattern = r'^arn:aws:[a-z0-9-]+:[a-z0-9-]*:\d{12}:[a-zA-Z0-9/_-]+$'
    if not re.match(arn_pattern, result.value_or('')):
        from valid8r.core.maybe import Maybe

        return Maybe.failure('Invalid ARN format (expected: arn:aws:service:region:account-id:resource)')

    return result


Arn = ValidatedType(arn_parser, help_text='AWS ARN (arn:aws:service:region:account-id:resource)')


@app.command()
def grant_access(
    project: Annotated[str, typer.Argument(click_type=ProjectId, help='Project ID')],
    role_arn: Annotated[str, typer.Option('--role', click_type=Arn, help='IAM role ARN')],
    email: Annotated[str, typer.Option('--user', callback=validator_callback(parsers.parse_email), help='User email')],
) -> None:
    r"""Grant user access to a project via IAM role.

    Example:
        cloud_cli.py grant-access my-project-123 \
            --role arn:aws:iam::123456789012:role/MyRole \
            --user alice@example.com

    """
    from valid8r.core.parsers import EmailAddress

    typer.secho('\n✓ Granting access:', fg=typer.colors.GREEN, bold=True)
    typer.echo(f'  Project: {project}')
    typer.echo(f'  Role ARN: {role_arn}')

    if isinstance(email, EmailAddress):
        typer.echo(f'  User: {email.local}@{email.domain}')

    typer.secho('\n✓ Access granted successfully!', fg=typer.colors.GREEN)


@app.command()
def create_project(
    project_id: Annotated[str, typer.Argument(click_type=ProjectId, help='Unique project ID')],
    owner_email: Annotated[
        str, typer.Option('--owner', callback=validator_callback(parsers.parse_email), help='Project owner email')
    ],
    region: Annotated[
        str, typer.Option('--region', '-r', callback=region_callback, help='Primary region')
    ] = 'us-east-1',
) -> None:
    """Create a new cloud project.

    Example:
        cloud_cli.py create-project my-webapp-api --owner alice@example.com --region us-west-2

    """
    from valid8r.core.parsers import EmailAddress

    typer.secho('\n✓ Creating project:', fg=typer.colors.GREEN, bold=True)
    typer.echo(f'  Project ID: {project_id}')
    typer.echo(f'  Region: {region}')

    if isinstance(owner_email, EmailAddress):
        typer.echo(f'  Owner: {owner_email.local}@{owner_email.domain}')

    typer.secho('\n✓ Project created successfully!', fg=typer.colors.GREEN)


# ============================================================================
# Pattern 3: validated_prompt() - For interactive workflows
# ============================================================================


@app.command()
def configure() -> None:
    """Interactive configuration wizard.

    Prompts for all required configuration with validation.
    """
    typer.secho('\n=== Cloud CLI Configuration Wizard ===\n', fg=typer.colors.CYAN, bold=True)

    # Prompt for project ID with validation
    typer.echo('Enter your project ID (lowercase, 3-40 chars, alphanumeric with hyphens):')
    project_id = validated_prompt(
        'Project ID',
        parser=lambda t: parsers.parse_str(t).bind(validators.matches(r'^[a-z][a-z0-9-]{2,39}$')),
        max_retries=5,
    )

    # Prompt for region
    typer.echo('\nSelect your primary region (us-east-1, us-west-2, eu-west-1, ap-southeast-1):')
    region = validated_prompt(
        'Region',
        parser=region_parser,
        max_retries=3,
    )

    # Prompt for email
    typer.echo('\nEnter your email for notifications:')
    from valid8r.core.parsers import EmailAddress

    email = validated_prompt(
        'Email',
        parser=parsers.parse_email,
        max_retries=3,
    )

    # Prompt for port
    typer.echo('\nEnter the default service port (1-65535):')
    port = validated_prompt(
        'Port',
        parser=port_parser,
        max_retries=3,
    )

    # Display configuration
    typer.secho('\n✓ Configuration complete!', fg=typer.colors.GREEN, bold=True)
    typer.echo('\nYour configuration:')
    typer.echo(f'  Project ID: {project_id}')
    typer.echo(f'  Region: {region}')
    if isinstance(email, EmailAddress):
        typer.echo(f'  Email: {email.local}@{email.domain}')
    typer.echo(f'  Port: {port}')

    # Save configuration (in real app, would persist to file)
    typer.secho('\n✓ Configuration saved!', fg=typer.colors.GREEN)


# ============================================================================
# Pattern 4: Combining validation with Typer features
# ============================================================================


@app.command()
def scale(
    service: Annotated[str, typer.Argument(help='Service name')],
    instances: Annotated[
        int,
        typer.Option(
            '--instances',
            '-i',
            callback=validator_callback(
                lambda t: parsers.parse_int(t).bind(validators.minimum(1) & validators.maximum(100))
            ),
            help='Number of instances (1-100)',
        ),
    ] = 1,
    region: Annotated[
        str, typer.Option('--region', '-r', callback=region_callback, help='Target region')
    ] = 'us-east-1',
    *,
    force: Annotated[bool, typer.Option('--force', '-f', help='Skip confirmation')] = False,
) -> None:
    """Scale a service to the specified number of instances.

    Example:
        cloud_cli.py scale my-api --instances 5 --region us-east-1 --force

    """
    if not force:
        confirm = typer.confirm(f'Scale {service} to {instances} instances in {region}?')
        if not confirm:
            typer.secho('Scaling cancelled.', fg=typer.colors.YELLOW)
            raise typer.Abort

    typer.secho('\n✓ Scaling service:', fg=typer.colors.GREEN, bold=True)
    typer.echo(f'  Service: {service}')
    typer.echo(f'  Region: {region}')
    typer.echo(f'  Instances: {instances}')

    typer.secho('\n✓ Scaling complete!', fg=typer.colors.GREEN)


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == '__main__':
    app()
