"""Integrations with popular Python frameworks and libraries.

This module provides integrations with popular Python frameworks:

- argparse: Standard library CLI integration via type_from_parser
- Click: CLI framework integration via ParamTypeAdapter
- Typer: Modern CLI framework integration via TyperParser
- Pydantic: Field validator integration via validator_from_parser
- Environment Variables: Schema-based configuration loading via load_env_config
- Dataclasses: Field validation with @validate decorator

Examples:
    >>> # argparse integration
    >>> from valid8r.integrations.argparse import type_from_parser
    >>> from valid8r.core import parsers
    >>> import argparse
    >>>
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--email', type=type_from_parser(parsers.parse_email))
    >>> args = parser.parse_args(['--email', 'alice@example.com'])
    >>> print(f"Hello {args.email.local}@{args.email.domain}!")

    >>> # Click integration
    >>> from valid8r.integrations.click import ParamTypeAdapter
    >>> from valid8r.core import parsers
    >>> import click
    >>>
    >>> @click.command()
    ... @click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
    ... def greet(email):
    ...     click.echo(f"Hello {email.local}@{email.domain}!")

    >>> # Typer integration
    >>> from valid8r.integrations.typer import TyperParser
    >>> import typer
    >>> from typing_extensions import Annotated
    >>>
    >>> app = typer.Typer()
    >>> @app.command()
    ... def greet(
    ...     email: Annotated[str, typer.Option(parser=TyperParser(parsers.parse_email))]
    ... ) -> None:
    ...     print(f"Hello {email.local}@{email.domain}!")

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

    >>> # Dataclass integration
    >>> from valid8r.integrations.dataclasses import validate
    >>> from valid8r.core.validators import minimum, length
    >>> from dataclasses import dataclass, field
    >>>
    >>> @validate
    ... @dataclass
    ... class Product:
    ...     name: str = field(metadata={'validator': length(1, 100)})
    ...     price: float = field(metadata={'validator': minimum(0.0)})
    >>>
    >>> result = Product.from_dict({'name': 'Widget', 'price': '19.99'})

"""

from __future__ import annotations

from valid8r.integrations.dataclasses import (
    validate,
    validate_dataclass,
)
from valid8r.integrations.env import (
    EnvField,
    EnvSchema,
    load_env_config,
)
from valid8r.integrations.pydantic import (
    make_after_validator,
    make_wrap_validator,
    validator_from_parser,
)

__all__ = [
    'EnvField',
    'EnvSchema',
    'load_env_config',
    'make_after_validator',
    'make_wrap_validator',
    'validate',
    'validate_dataclass',
    'validator_from_parser',
]

# Click integration is optional, only import if click is available
try:
    from valid8r.integrations.click import ParamTypeAdapter

    __all__ += ['ParamTypeAdapter']
except ImportError:
    pass

# Typer integration is optional, only import if typer is available
try:
    from valid8r.integrations.typer import TyperParser

    __all__ += ['TyperParser']
except ImportError:
    pass

# argparse integration is always available (stdlib)
from valid8r.integrations.argparse import type_from_parser

__all__ += ['type_from_parser']
