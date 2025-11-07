"""Environment Variable Configuration Examples.

This example demonstrates multiple approaches to using valid8r's environment
variable integration for typed, validated configuration.

Run with:
    # Basic example
    export APP_PORT=8080
    export APP_DEBUG=true
    export APP_DATABASE_URL=postgresql://localhost/mydb
    export APP_MAX_CONNECTIONS=100
    export APP_ADMIN_EMAIL=admin@example.com
    export APP_ALLOWED_HOSTS=localhost,127.0.0.1,example.com
    python examples/env_example.py

Or set environment variables in a .env file and use python-dotenv:
    pip install python-dotenv
    python examples/env_example.py
"""

from __future__ import annotations

import sys

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    parse_bool,
    parse_email,
    parse_int,
    parse_list,
)
from valid8r.core.validators import (
    maximum,
    minimum,
)
from valid8r.integrations.env import (
    EnvField,
    EnvSchema,
    load_env_config,
)


def parse_str(text: str | None) -> Maybe[str]:
    """Parse a string value from an environment variable.

    Args:
        text: The string value to parse

    Returns:
        Success with the string value, or Failure if invalid

    """
    if text is None or not isinstance(text, str):
        return Maybe.failure('Value must be a string')
    return Maybe.success(text)


def example_basic_config() -> int:
    """Demonstrate basic configuration with defaults and required fields."""
    print('=' * 60)
    print('Example 1: Basic Configuration')
    print('=' * 60)

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
            return 1


def example_nested_config() -> int:
    """Demonstrate nested configuration with hierarchical schemas."""
    print()
    print('=' * 60)
    print('Example 2: Nested Configuration')
    print('=' * 60)

    # Database schema
    database_schema = EnvSchema(
        fields={
            'host': EnvField(parser=parse_str, default='localhost'),
            'port': EnvField(parser=parse_int, default=5432),
            'name': EnvField(parser=parse_str, default='myapp'),
            'user': EnvField(parser=parse_str, default='postgres'),
        }
    )

    # Cache schema
    cache_schema = EnvSchema(
        fields={
            'host': EnvField(parser=parse_str, default='localhost'),
            'port': EnvField(parser=parse_int, default=6379),
            'ttl': EnvField(parser=parse_int, default=3600),
        }
    )

    # Main schema with nested configs
    app_schema = EnvSchema(
        fields={
            'port': EnvField(parser=parse_int, default=8080),
            'debug': EnvField(parser=parse_bool, default=False),
            'database': EnvField(nested=database_schema),
            'cache': EnvField(nested=cache_schema),
        }
    )

    # Load configuration
    result = load_env_config(app_schema, prefix='APP_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ Nested configuration loaded successfully:')
            print(f'   App Port: {config["port"]}')
            print(f'   App Debug: {config["debug"]}')
            print()
            print('   Database Configuration:')
            print(f'     Host: {config["database"]["host"]}')
            print(f'     Port: {config["database"]["port"]}')
            print(f'     Name: {config["database"]["name"]}')
            print(f'     User: {config["database"]["user"]}')
            print()
            print('   Cache Configuration:')
            print(f'     Host: {config["cache"]["host"]}')
            print(f'     Port: {config["cache"]["port"]}')
            print(f'     TTL: {config["cache"]["ttl"]}s')
            return 0

        case result if result.is_failure():
            print('❌ Nested configuration validation failed:')
            print(f'   {result.error}')
            return 1


def example_list_parsing() -> int:
    """Demonstrate parsing lists from environment variables."""
    print()
    print('=' * 60)
    print('Example 3: List Parsing')
    print('=' * 60)

    schema = EnvSchema(
        fields={
            'allowed_hosts': EnvField(
                parser=lambda x: parse_list(x, element_parser=parse_str, separator=',') if x else Maybe.success([]),
                default=[],
            ),
            'cors_origins': EnvField(
                parser=lambda x: parse_list(x, element_parser=parse_str, separator=',') if x else Maybe.success([]),
                default=[],
            ),
        }
    )

    result = load_env_config(schema, prefix='APP_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ List configuration loaded successfully:')
            print(f'   Allowed Hosts: {config["allowed_hosts"]}')
            print(f'   CORS Origins: {config["cors_origins"]}')
            return 0

        case result if result.is_failure():
            print('❌ List configuration validation failed:')
            print(f'   {result.error}')
            return 1


def example_feature_flags() -> int:
    """Demonstrate using environment variables for feature flags."""
    print()
    print('=' * 60)
    print('Example 4: Feature Flags')
    print('=' * 60)

    schema = EnvSchema(
        fields={
            'feature_new_api': EnvField(parser=parse_bool, default=False),
            'feature_experimental': EnvField(parser=parse_bool, default=False),
            'feature_beta': EnvField(parser=parse_bool, default=False),
        }
    )

    result = load_env_config(schema, prefix='FEATURE_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ Feature flags loaded successfully:')
            print(f'   New API: {"ENABLED" if config["feature_new_api"] else "DISABLED"}')
            print(f'   Experimental: {"ENABLED" if config["feature_experimental"] else "DISABLED"}')
            print(f'   Beta: {"ENABLED" if config["feature_beta"] else "DISABLED"}')
            return 0

        case result if result.is_failure():
            print('❌ Feature flag configuration validation failed:')
            print(f'   {result.error}')
            return 1


def example_fastapi_integration() -> int:  # noqa: PLR0915
    """Demonstrate FastAPI application configuration.

    Shows complete configuration schema suitable for a production
    FastAPI application with validation, defaults, and required fields.
    """
    print()
    print('=' * 60)
    print('Example 5: FastAPI Application Configuration')
    print('=' * 60)

    schema = EnvSchema(
        fields={
            # Server configuration
            'host': EnvField(parser=parse_str, default='0.0.0.0'),  # noqa: S104
            'port': EnvField(parser=lambda x: parse_int(x).bind(minimum(1024)).bind(maximum(65535)), default=8080),
            'workers': EnvField(parser=lambda x: parse_int(x).bind(minimum(1)).bind(maximum(32)), default=4),
            'debug': EnvField(parser=parse_bool, default=False),
            # Database configuration
            'database_url': EnvField(parser=parse_str, required=True),
            'database_pool_size': EnvField(
                parser=lambda x: parse_int(x).bind(minimum(1)).bind(maximum(100)), default=10
            ),
            # Redis configuration
            'redis_url': EnvField(parser=parse_str, default='redis://localhost:6379/0'),
            # Security
            'secret_key': EnvField(parser=parse_str, required=True),
            'admin_email': EnvField(parser=parse_email, required=True),
            # API configuration
            'api_prefix': EnvField(parser=parse_str, default='/api/v1'),
            'api_rate_limit': EnvField(parser=lambda x: parse_int(x).bind(minimum(1)), default=100),
        }
    )

    result = load_env_config(schema, prefix='API_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ FastAPI configuration loaded successfully:')
            print()
            print('Server Configuration:')
            print(f'   Host: {config["host"]}')
            print(f'   Port: {config["port"]}')
            print(f'   Workers: {config["workers"]}')
            print(f'   Debug: {config["debug"]}')
            print()
            print('Database Configuration:')
            print(f'   URL: {config["database_url"][:30]}...')
            print(f'   Pool Size: {config["database_pool_size"]}')
            print()
            print('Redis Configuration:')
            print(f'   URL: {config["redis_url"]}')
            print()
            print('Security Configuration:')
            print(f'   Secret Key: {"*" * 20} (hidden)')
            print(f'   Admin Email: {config["admin_email"].local}@{config["admin_email"].domain}')
            print()
            print('API Configuration:')
            print(f'   Prefix: {config["api_prefix"]}')
            print(f'   Rate Limit: {config["api_rate_limit"]} requests/minute')
            print()
            print('FastAPI app would be configured with these settings.')
            host = config['host']
            port = config['port']
            workers = config['workers']
            print(f'Start with: uvicorn app:app --host {host} --port {port} --workers {workers}')
            return 0

        case result if result.is_failure():
            print('❌ FastAPI configuration validation failed:')
            print(f'   {result.error}')
            print()
            print('Required environment variables:')
            print('   export API_DATABASE_URL=postgresql://localhost/myapp')
            print('   export API_SECRET_KEY=your-secret-key-here')
            print('   export API_ADMIN_EMAIL=admin@example.com')
            print()
            print('Optional variables (with defaults):')
            print('   export API_HOST=0.0.0.0')
            print('   export API_PORT=8080')
            print('   export API_WORKERS=4')
            print('   export API_DEBUG=false')
            print('   export API_DATABASE_POOL_SIZE=10')
            print('   export API_REDIS_URL=redis://localhost:6379/0')
            print('   export API_API_PREFIX=/api/v1')
            print('   export API_API_RATE_LIMIT=100')
            return 1


def example_docker_deployment() -> int:
    """Demonstrate Docker deployment configuration.

    Shows minimal configuration schema that works well in containerized
    environments with docker-compose or Kubernetes.
    """
    print()
    print('=' * 60)
    print('Example 6: Docker Deployment Configuration')
    print('=' * 60)

    schema = EnvSchema(
        fields={
            # Application
            'port': EnvField(parser=parse_int, default=8080),
            'workers': EnvField(parser=parse_int, default=4),
            # Database (required - provided by docker-compose)
            'database_url': EnvField(parser=parse_str, required=True),
            # Redis (with docker-compose service name)
            'redis_url': EnvField(parser=parse_str, default='redis://redis:6379/0'),
            # Secrets (must be provided via environment or secrets management)
            'secret_key': EnvField(parser=parse_str, required=True),
        }
    )

    result = load_env_config(schema, prefix='APP_')

    match result:
        case result if result.is_success():
            config = result.value
            print('✅ Docker configuration loaded successfully:')
            print()
            print('Container will start with:')
            print(f'   Port: {config["port"]} (mapped to host)')
            print(f'   Workers: {config["workers"]}')
            print(f'   Database: {config["database_url"][:30]}...')
            print(f'   Redis: {config["redis_url"]}')
            print(f'   Secret: {"*" * 20} (hidden)')
            print()
            print('Docker Compose example:')
            print('  services:')
            print('    app:')
            print('      image: myapp:latest')
            print('      ports:')
            print(f'        - "8000:{config["port"]}"')
            print('      environment:')
            print(f'        APP_PORT: {config["port"]}')
            print(f'        APP_WORKERS: {config["workers"]}')
            print('        APP_DATABASE_URL: postgresql://postgres:password@db:5432/myapp')
            print(f'        APP_REDIS_URL: {config["redis_url"]}')
            print('        APP_SECRET_KEY: ${SECRET_KEY}')
            return 0

        case result if result.is_failure():
            print('❌ Docker configuration validation failed:')
            print(f'   {result.error}')
            print()
            print('Required environment variables:')
            print('   export APP_DATABASE_URL=postgresql://postgres:password@db:5432/myapp')
            print('   export APP_SECRET_KEY=your-secret-key-here')
            return 1


def main() -> int:
    """Run all environment configuration examples."""
    print()
    print('Valid8r Environment Variable Configuration Examples')
    print('=' * 60)
    print()
    print('This example demonstrates various approaches to loading')
    print('typed, validated configuration from environment variables.')
    print()

    # Run all examples
    examples = [
        example_basic_config,
        example_nested_config,
        example_list_parsing,
        example_feature_flags,
        example_fastapi_integration,
        example_docker_deployment,
    ]

    results = []
    for example in examples:
        try:
            result = example()
            results.append(result)
        except Exception as e:  # noqa: BLE001
            print(f'❌ Example failed with exception: {e}')
            results.append(1)

    # Summary
    print()
    print('=' * 60)
    print('Summary')
    print('=' * 60)
    successful = sum(1 for r in results if r == 0)
    failed = len(results) - successful
    print(f'Examples run: {len(results)}')
    print(f'Successful: {successful}')
    print(f'Failed: {failed}')
    print()

    if failed > 0:
        print('Some examples failed. This is expected if required')
        print('environment variables are not set.')
        print()
        print('Try running with:')
        print('  export APP_DATABASE_URL=postgresql://localhost/mydb')
        print('  export APP_ADMIN_EMAIL=admin@example.com')
        print('  export API_DATABASE_URL=postgresql://localhost/myapp')
        print('  export API_SECRET_KEY=dev-secret-key')
        print('  export API_ADMIN_EMAIL=admin@example.com')
        print('  python examples/env_example.py')

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
