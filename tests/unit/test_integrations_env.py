from __future__ import annotations

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.parsers import (
    parse_bool,
    parse_int,
)
from valid8r.core.validators import minimum


class DescribeEnvField:
    """Test the EnvField class."""

    def it_creates_a_field_with_parser(self) -> None:
        """Create an EnvField with a parser."""
        from valid8r.integrations.env import EnvField

        field = EnvField(parser=parse_int)
        assert field.parser == parse_int
        assert field.default is None
        assert field.required is False

    def it_creates_a_field_with_default_value(self) -> None:
        """Create an EnvField with a default value."""
        from valid8r.integrations.env import EnvField

        field = EnvField(parser=parse_int, default=42)
        assert field.parser == parse_int
        assert field.default == 42
        assert field.required is False

    def it_creates_a_required_field(self) -> None:
        """Create a required EnvField."""
        from valid8r.integrations.env import EnvField

        field = EnvField(parser=parse_int, required=True)
        assert field.parser == parse_int
        assert field.default is None
        assert field.required is True

    def it_creates_a_field_with_nested_schema(self) -> None:
        """Create an EnvField with nested schema."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
        )

        nested_schema = EnvSchema(fields={'port': EnvField(parser=parse_int)})
        field = EnvField(parser=None, nested=nested_schema)
        assert field.parser is None
        assert field.nested == nested_schema
        assert field.required is False


class DescribeEnvSchema:
    """Test the EnvSchema class."""

    def it_creates_a_schema_with_fields(self) -> None:
        """Create an EnvSchema with fields."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int), 'debug': EnvField(parser=parse_bool)})
        assert 'port' in schema.fields
        assert 'debug' in schema.fields
        assert len(schema.fields) == 2

    def it_creates_an_empty_schema(self) -> None:
        """Create an empty EnvSchema."""
        from valid8r.integrations.env import EnvSchema

        schema = EnvSchema(fields={})
        assert len(schema.fields) == 0


class DescribeLoadEnvConfig:
    """Test the load_env_config function."""

    def it_loads_simple_config_from_environment(self) -> None:
        """Load simple configuration from environment variables."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int), 'debug': EnvField(parser=parse_bool)})
        env = {'APP_PORT': '8080', 'APP_DEBUG': 'true'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'port': 8080, 'debug': True}

    def it_uses_default_values_for_missing_variables(self) -> None:
        """Use default values when environment variables are missing."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int, default=3000)})
        env = {}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'port': 3000}

    def it_fails_validation_for_invalid_environment_variable(self) -> None:
        """Fail validation when environment variable cannot be parsed."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int)})
        env = {'APP_PORT': 'invalid'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Failure)
        assert 'port' in result.error.lower()
        assert 'valid integer' in result.error.lower()

    def it_fails_for_required_field_not_set(self) -> None:
        """Fail when a required field is not set."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(
            fields={
                'api_key': EnvField(parser=lambda x: Maybe.success(x) if x else Maybe.failure('missing'), required=True)
            }
        )
        env = {}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Failure)
        assert 'api_key' in result.error.lower()
        assert 'required' in result.error.lower()

    def it_validates_with_chained_validators(self) -> None:
        """Validate environment variables using chained validators."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        def chained_parser(text: str | None) -> Maybe:
            return parse_int(text).bind(minimum(1))

        schema = EnvSchema(fields={'max_connections': EnvField(parser=chained_parser)})
        env = {'APP_MAX_CONNECTIONS': '0'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Failure)
        assert 'at least' in result.error.lower()

    def it_parses_list_values_from_comma_separated_strings(self) -> None:
        """Parse list values from comma-separated strings."""
        from valid8r.core.parsers import parse_list
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        def list_parser(text: str | None) -> Maybe:
            if text is None:
                return Maybe.failure('missing')
            return parse_list(text, element_parser=lambda x: Maybe.success(x), separator=',')

        schema = EnvSchema(fields={'allowed_hosts': EnvField(parser=list_parser)})
        env = {'APP_ALLOWED_HOSTS': 'localhost,example.com,api.example.com'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'allowed_hosts': ['localhost', 'example.com', 'api.example.com']}

    def it_handles_nested_configuration(self) -> None:
        """Handle nested configuration with delimiter."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        nested_schema = EnvSchema(
            fields={
                'host': EnvField(parser=lambda x: Maybe.success(x) if x else Maybe.failure('missing')),
                'port': EnvField(parser=parse_int),
                'name': EnvField(parser=lambda x: Maybe.success(x) if x else Maybe.failure('missing')),
            }
        )
        schema = EnvSchema(fields={'database': EnvField(parser=None, nested=nested_schema)})
        env = {'APP_DATABASE_HOST': 'localhost', 'APP_DATABASE_PORT': '5432', 'APP_DATABASE_NAME': 'mydb'}
        result = load_env_config(schema, prefix='APP_', delimiter='_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'database': {'host': 'localhost', 'port': 5432, 'name': 'mydb'}}

    def it_accumulates_errors_for_multiple_invalid_fields(self) -> None:
        """Accumulate errors when multiple fields fail validation."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int), 'max_connections': EnvField(parser=parse_int)})
        env = {'APP_PORT': 'invalid', 'APP_MAX_CONNECTIONS': 'also_invalid'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Failure)
        # Both field names should be in the error message
        assert 'port' in result.error.lower()
        assert 'max_connections' in result.error.lower()

    def it_handles_empty_environment(self) -> None:
        """Handle empty environment with all defaults."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(
            fields={
                'port': EnvField(parser=parse_int, default=8080),
                'debug': EnvField(parser=parse_bool, default=False),
            }
        )
        env = {}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'port': 8080, 'debug': False}

    def it_handles_no_prefix(self) -> None:
        """Handle environment variables without a prefix."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'port': EnvField(parser=parse_int)})
        env = {'PORT': '8080'}
        result = load_env_config(schema, prefix='', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'port': 8080}

    def it_converts_field_names_to_uppercase_with_prefix(self) -> None:
        """Convert field names to uppercase and prepend prefix for env var lookup."""
        from valid8r.integrations.env import (
            EnvField,
            EnvSchema,
            load_env_config,
        )

        schema = EnvSchema(fields={'max_connections': EnvField(parser=parse_int)})
        env = {'APP_MAX_CONNECTIONS': '100'}
        result = load_env_config(schema, prefix='APP_', environ=env)

        assert isinstance(result, Success)
        assert result.value == {'max_connections': 100}
