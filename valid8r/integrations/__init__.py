"""Integrations with popular Python frameworks and libraries.

This module provides integrations with popular Python frameworks:

- Click: CLI framework integration via ParamTypeAdapter
- Pydantic: Field validator integration via validator_from_parser
- Environment Variables: Schema-based configuration loading via load_env_config

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

    >>> # Environment variable integration
    >>> from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
    >>> from valid8r.core import parsers
    >>>
    >>> schema = EnvSchema(fields={
    ...     'port': EnvField(parser=parsers.parse_int, default=8080),
    ...     'debug': EnvField(parser=parsers.parse_bool, default=False),
    ... })
    >>> result = load_env_config(schema, prefix='APP_')

"""

from __future__ import annotations

from valid8r.integrations.env import (
    EnvField,
    EnvSchema,
    load_env_config,
)
from valid8r.integrations.pydantic import validator_from_parser

__all__ = ['EnvField', 'EnvSchema', 'load_env_config', 'validator_from_parser']

# Click integration is optional, only import if click is available
try:
    from valid8r.integrations.click import ParamTypeAdapter

    __all__ += ['ParamTypeAdapter']
except ImportError:
    pass
