"""Integrations with popular Python frameworks and libraries.

This module provides integrations with popular Python frameworks:

- Click: CLI framework integration via ParamTypeAdapter

Examples:
    >>> # Click integration
    >>> from valid8r.integrations.click import ParamTypeAdapter
    >>> from valid8r.core import parsers
    >>> import click
    >>>
    >>> @click.command()
    ... @click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
    ... def greet(email):
    ...     click.echo(f"Hello {email.local}@{email.domain}!")

"""

from __future__ import annotations

# Click integration is optional, only import if click is available
try:
    from valid8r.integrations.click import ParamTypeAdapter

    __all__ = ['ParamTypeAdapter']
except ImportError:
    __all__ = []
