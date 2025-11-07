"""Environment variable integration module for valid8r.

This module provides utilities for loading typed, validated configuration
from environment variables using valid8r parsers.

Example:
    >>> from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
    >>> from valid8r.core.parsers import parse_int, parse_bool
    >>> schema = EnvSchema(fields={
    ...     'port': EnvField(parser=parse_int, default=8080),
    ...     'debug': EnvField(parser=parse_bool, default=False),
    ... })
    >>> env = {'APP_PORT': '3000', 'APP_DEBUG': 'true'}
    >>> result = load_env_config(schema, prefix='APP_', environ=env)
    >>> result.value_or({})
    {'port': 3000, 'debug': True}
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from valid8r.core.maybe import Failure, Maybe, Success


@dataclass
class EnvField:
    """Represents a field in an environment variable schema.

    Args:
        parser: A function that parses a string into a Maybe[T]
        default: Optional default value if environment variable is not set
        required: Whether this field must be present in the environment
        nested: Optional nested schema for hierarchical configuration
    """

    parser: Callable[[str | None], Maybe[Any]] | None
    default: Any = None
    required: bool = False
    nested: EnvSchema | None = None


@dataclass
class EnvSchema:
    """Represents a schema for environment variable configuration.

    Args:
        fields: Dictionary mapping field names to EnvField objects
    """

    fields: dict[str, EnvField]


def load_env_config(
    schema: EnvSchema,
    *,
    prefix: str = '',
    delimiter: str = '_',
    list_separator: str = ',',
    environ: dict[str, str] | None = None,
) -> Maybe[dict[str, Any]]:
    """Load and validate configuration from environment variables.

    Args:
        schema: The EnvSchema defining expected fields and their parsers
        prefix: Optional prefix for environment variable names (e.g., 'APP_')
        delimiter: Delimiter for nested configuration (default: '_')
        list_separator: Separator for list values (default: ',')
        environ: Optional dict of environment variables (defaults to os.environ)

    Returns:
        Maybe[dict]: Success with parsed config dict, or Failure with error message

    Example:
        >>> from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
        >>> from valid8r.core.parsers import parse_int
        >>> schema = EnvSchema(fields={'port': EnvField(parser=parse_int, default=8080)})
        >>> env = {'APP_PORT': '3000'}
        >>> result = load_env_config(schema, prefix='APP_', environ=env)
        >>> result.value_or({})
        {'port': 3000}
    """
    if environ is None:
        environ = dict(os.environ)

    config: dict[str, Any] = {}
    errors: list[str] = []

    for field_name, field_spec in schema.fields.items():
        # Handle nested schemas
        if field_spec.nested is not None:
            nested_prefix = f'{prefix}{field_name.upper()}{delimiter}'
            nested_result = load_env_config(
                field_spec.nested, prefix=nested_prefix, delimiter=delimiter, environ=environ
            )

            match nested_result:
                case Success(value):
                    config[field_name] = value
                case Failure(error):
                    errors.append(f'{field_name}: {error}')
            continue

        # Construct environment variable name
        env_var_name = f'{prefix}{field_name.upper()}'
        env_value = environ.get(env_var_name)

        # Handle missing required fields
        if env_value is None:
            if field_spec.required:
                errors.append(f'{field_name}: required field is missing')
                continue
            if field_spec.default is not None:
                config[field_name] = field_spec.default
                continue
            # Optional field without default - skip it
            if not field_spec.required:
                continue

        # Parse the environment variable value
        if env_value is not None and field_spec.parser is not None:
            parse_result = field_spec.parser(env_value)

            match parse_result:
                case Success(value):
                    config[field_name] = value
                case Failure(error):
                    errors.append(f'{field_name}: {error}')

    # Return accumulated errors or success
    if errors:
        return Maybe.failure('; '.join(errors))

    return Maybe.success(config)
