"""Integrations with popular Python frameworks and libraries.

This module provides integrations with popular Python frameworks:

- Click: CLI framework integration via ParamTypeAdapter
- Pydantic: Field validator integration via validator_from_parser

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

    >>> # Pydantic integration
    >>> from valid8r.integrations.pydantic import validator_from_parser
    >>> from pydantic import BaseModel
    >>>
    >>> class User(BaseModel):
    ...     email: str
    ...     _validate_email = validator_from_parser(parsers.parse_email)

"""

from __future__ import annotations

from valid8r.integrations.pydantic import validator_from_parser

__all__ = ['validator_from_parser']

# Click integration is optional, only import if click is available
try:
    from valid8r.integrations.click import ParamTypeAdapter

    __all__ += ['ParamTypeAdapter']
except ImportError:
    pass
