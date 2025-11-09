#!/usr/bin/env python3
"""Example Typer CLI demonstrating valid8r integration.

This example shows how to use TyperParser to validate CLI arguments
using valid8r parsers in a Typer application.

Run examples:
    python typer_example.py create-user --email alice@example.com --phone "(212) 456-7890"
    python typer_example.py start-server --port 8080 --host 192.168.1.1
    python typer_example.py get-user 550e8400-e29b-41d4-a716-446655440000
    python typer_example.py fetch-url --url "https://example.com:8080/api/users?page=1"

"""

from __future__ import annotations

import ipaddress  # noqa: TC003
import uuid  # noqa: TC003
from typing import (
    TYPE_CHECKING,
    Annotated,
)

import typer

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.integrations.typer import TyperParser

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe

# Create the main Typer app
app = typer.Typer(
    help='Example CLI demonstrating valid8r + Typer integration',
    no_args_is_help=True,
)


@app.command()
def create_user(
    email: Annotated[
        str,
        typer.Option(
            parser=TyperParser(parsers.parse_email),
            help="User's email address",
        ),
    ],
    phone: Annotated[
        str,
        typer.Option(
            parser=TyperParser(parsers.parse_phone),
            help="User's phone number (NANP format)",
        ),
    ],
) -> None:
    """Create a new user with validated email and phone number."""
    typer.echo(typer.style('Creating new user:', fg=typer.colors.GREEN, bold=True))
    typer.echo(f'  Email: {email.local}@{email.domain}')
    typer.echo(f'  Phone: ({phone.area_code}) {phone.exchange}-{phone.subscriber}')
    if phone.extension:
        typer.echo(f'  Extension: {phone.extension}')
    typer.echo(typer.style('✓ User created successfully!', fg=typer.colors.GREEN))


# Create a port parser with validation (1-65535)
def port_parser(text: str | None) -> Maybe[int]:
    """Parse and validate a TCP/UDP port number."""
    return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))


@app.command()
def start_server(
    port: Annotated[
        int,
        typer.Option(
            parser=TyperParser(port_parser, name='port_number'),
            help='Server port (1-65535)',
        ),
    ] = 8080,
    host: Annotated[
        ipaddress.IPv4Address,
        typer.Option(
            parser=TyperParser(parsers.parse_ipv4),
            help='Server host IP address',
        ),
    ] = '127.0.0.1',  # type: ignore[assignment]
) -> None:
    """Start a server on the specified port and host."""
    typer.echo(typer.style('Starting server...', fg=typer.colors.CYAN, bold=True))
    typer.echo(f'  Host: {host}')
    typer.echo(f'  Port: {port}')
    typer.echo(typer.style(f'✓ Server listening on http://{host}:{port}', fg=typer.colors.GREEN))


@app.command()
def get_user(
    user_id: Annotated[
        uuid.UUID,
        typer.Argument(
            parser=TyperParser(parsers.parse_uuid),
            help="User's unique identifier (UUID)",
        ),
    ],
) -> None:
    """Fetch a user by their UUID."""
    typer.echo(typer.style('Fetching user...', fg=typer.colors.CYAN, bold=True))
    typer.echo(f'  User ID: {user_id}')
    typer.echo(f'  Version: {user_id.version}')
    typer.echo(typer.style('✓ User found!', fg=typer.colors.GREEN))


@app.command()
def fetch_url(
    url: Annotated[
        str,
        typer.Option(
            parser=TyperParser(parsers.parse_url, error_prefix='URL'),
            help='URL to fetch',
        ),
    ],
) -> None:
    """Fetch and analyze a URL."""
    typer.echo(typer.style('Analyzing URL...', fg=typer.colors.CYAN, bold=True))
    typer.echo(f'  Scheme: {url.scheme}')
    typer.echo(f'  Host: {url.host}')
    typer.echo(f'  Port: {url.port or "default"}')
    typer.echo(f'  Path: {url.path or "/"}')
    if url.query:
        typer.echo(f'  Query: {url.query}')
    if url.fragment:
        typer.echo(f'  Fragment: {url.fragment}')
    if url.username:
        typer.echo(f'  Username: {url.username}')
    typer.echo(typer.style('✓ URL is valid!', fg=typer.colors.GREEN))


# Create an age parser with validation (0-120)
def age_parser(text: str | None) -> Maybe[int]:
    """Parse and validate a person's age."""
    return parsers.parse_int(text).bind(validators.minimum(0) & validators.maximum(120))


@app.command()
def register(
    email: Annotated[
        str,
        typer.Option(
            parser=TyperParser(parsers.parse_email, error_prefix='Email address'),
            help="User's email address",
        ),
    ],
    age: Annotated[
        int,
        typer.Option(
            parser=TyperParser(age_parser),
            help="User's age (0-120)",
        ),
    ],
) -> None:
    """Register a new user with age validation and custom error prefixes."""
    typer.echo(typer.style('Registering user...', fg=typer.colors.GREEN, bold=True))
    typer.echo(f'  Email: {email.local}@{email.domain}')
    typer.echo(f'  Age: {age}')
    typer.echo(typer.style('✓ Registration complete!', fg=typer.colors.GREEN))


if __name__ == '__main__':
    app()
