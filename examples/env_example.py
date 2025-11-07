"""Example: Environment variable configuration with FastAPI.

This example demonstrates how to use valid8r's environment variable integration
to load typed, validated configuration for a FastAPI application.

Run with:
    export APP_PORT=8080
    export APP_DEBUG=true
    export APP_DATABASE_URL=postgresql://localhost/mydb
    export APP_MAX_CONNECTIONS=100
    export APP_ADMIN_EMAIL=admin@example.com
    export APP_ALLOWED_HOSTS=localhost,127.0.0.1,example.com
    python examples/env_example.py

Or set environment variables in a .env file and use python-dotenv.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

from valid8r.core.parsers import parse_bool, parse_email, parse_int, parse_list
from valid8r.core.validators import maximum, minimum
from valid8r.integrations.env import EnvField, EnvSchema, load_env_config


def parse_str(text: str | None):
    """Simple string parser for environment variables."""
    from valid8r.core.maybe import Maybe

    if text is None or not isinstance(text, str):
        return Maybe.failure('Value must be a string')
    return Maybe.success(text)


def main() -> int:
    """Load configuration from environment variables and display results."""
    # Define configuration schema
    schema = EnvSchema(
        fields={
            'port': EnvField(parser=lambda x: parse_int(x).bind(minimum(1)).bind(maximum(65535)), default=8080),
            'debug': EnvField(parser=parse_bool, default=False),
            'database_url': EnvField(parser=parse_str, required=True),
            'max_connections': EnvField(
                parser=lambda x: parse_int(x).bind(minimum(1)).bind(maximum(1000)), default=100
            ),
            'admin_email': EnvField(parser=parse_email, required=True),
            'allowed_hosts': EnvField(
                parser=lambda x: parse_list(x, element_parser=parse_str, separator=',') if x else [],
                default=[],
            ),
        }
    )

    # Load configuration
    result = load_env_config(schema, prefix='APP_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ Configuration loaded successfully:')
            print(f'   Port: {config["port"]}')
            print(f'   Debug: {config["debug"]}')
            print(f'   Database URL: {config["database_url"]}')
            print(f'   Max Connections: {config["max_connections"]}')
            print(f'   Admin Email: {config["admin_email"].local}@{config["admin_email"].domain}')
            print(f'   Allowed Hosts: {config["allowed_hosts"]}')
            print()
            print('FastAPI app would be configured with these settings.')
            return 0

        case result if result.is_failure():
            print('❌ Configuration validation failed:')
            print(f'   {result.error}')
            print()
            print('Please set the required environment variables:')
            print('   export APP_DATABASE_URL=postgresql://localhost/mydb')
            print('   export APP_ADMIN_EMAIL=admin@example.com')
            print()
            print('Optional variables (with defaults):')
            print('   export APP_PORT=8080')
            print('   export APP_DEBUG=true')
            print('   export APP_MAX_CONNECTIONS=100')
            print('   export APP_ALLOWED_HOSTS=localhost,127.0.0.1')
            return 1


if __name__ == '__main__':
    sys.exit(main())
