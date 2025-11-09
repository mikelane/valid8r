#!/usr/bin/env python3
"""Example demonstrating argparse integration with valid8r.

This script shows how to use valid8r parsers with argparse for robust
CLI argument validation with helpful error messages.

Usage:
    python examples/argparse_example.py --email alice@example.com --port 8080
    python examples/argparse_example.py --help
    python examples/argparse_example.py --email bad-email  # Shows validation error
    python examples/argparse_example.py --port 70000  # Shows range validation error

"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.integrations.argparse import type_from_parser

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe


def port_parser(text: str | None) -> Maybe[int]:
    """Parse and validate a port number (1-65535)."""
    return parsers.parse_int(text).bind(validators.minimum(1) & validators.maximum(65535))


def main() -> None:
    """Run the example CLI application."""
    parser = argparse.ArgumentParser(
        description='Example CLI application using valid8r for robust argument validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --email alice@example.com --port 8080
  %(prog)s --email bob@test.org --port 3000 --uuid 550e8400-e29b-41d4-a716-446655440000
  %(prog)s --email alice@example.com --port 8080 --phone "(212) 456-7890"

Note: All arguments are validated using valid8r parsers for type safety and helpful error messages.
        """,
    )

    # Email validation using parse_email
    parser.add_argument(
        '--email',
        type=type_from_parser(parsers.parse_email),
        required=True,
        help='Email address (validated format)',
        metavar='EMAIL',
    )

    # Port validation using parse_int with range validators
    parser.add_argument(
        '--port',
        type=type_from_parser(port_parser),
        required=True,
        help='Port number (1-65535)',
        metavar='PORT',
    )

    # Optional UUID validation
    parser.add_argument(
        '--uuid',
        type=type_from_parser(parsers.parse_uuid),
        help='UUID (optional)',
        metavar='UUID',
    )

    # Optional phone number validation (US format)
    parser.add_argument(
        '--phone',
        type=type_from_parser(parsers.parse_phone),
        help='Phone number in US format (optional)',
        metavar='PHONE',
    )

    # Optional debug flag using parse_bool
    parser.add_argument(
        '--debug',
        type=type_from_parser(parsers.parse_bool),
        default=False,
        help='Enable debug mode (true/false, yes/no, 1/0)',
        metavar='BOOL',
    )

    # Parse arguments
    args = parser.parse_args()

    # Display parsed values
    print('Successfully parsed arguments:')
    print(f'  Email: {args.email.local}@{args.email.domain}')
    print(f'  Port: {args.port}')

    if args.uuid:
        print(f'  UUID: {args.uuid}')

    if args.phone:
        formatted_phone = f'({args.phone.area_code}) {args.phone.exchange}-{args.phone.subscriber}'
        if args.phone.extension:
            formatted_phone += f' ext. {args.phone.extension}'
        print(f'  Phone: {formatted_phone}')

    print(f'  Debug mode: {"enabled" if args.debug else "disabled"}')

    # Example: Use the validated values
    print(f'\nStarting server at {args.email.domain}:{args.port}...')
    print('(This is just an example - no actual server is started)')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nInterrupted by user', file=sys.stderr)
        sys.exit(130)
