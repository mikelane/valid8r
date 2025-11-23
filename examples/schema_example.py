"""Example demonstrating the Schema API for validating structured data.

This example shows how to use the Schema and Field classes to validate
complex nested objects with error accumulation and field path tracking.
"""

from __future__ import annotations

from valid8r.core import (
    parsers,
    schema,
    validators,
)
from valid8r.core.maybe import (
    Failure,
)


def basic_validation_example() -> None:
    """Basic schema validation with error accumulation."""
    print('=' * 60)
    print('Basic Validation Example')
    print('=' * 60)

    # Define a schema for user data
    user_schema = schema.Schema(
        fields={
            'age': schema.Field(parser=parsers.parse_int, required=True),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'name': schema.Field(
                parser=parsers.parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )

    # Valid input
    valid_input = {'age': '25', 'email': 'alice@example.com', 'name': 'Alice'}
    result = user_schema.validate(valid_input)

    if result.is_success():
        data = result.value_or({})
        print('\n✓ Validation succeeded:')
        print(f'  Name: {data["name"]}')
        print(f'  Age: {data["age"]} (type: {type(data["age"]).__name__})')
        print(f'  Email: {data["email"]}')

    # Invalid input - multiple errors
    print('\n' + '-' * 60)
    invalid_input = {'age': 'not-a-number', 'email': 'bad-email', 'name': ''}
    result = user_schema.validate(invalid_input)

    if isinstance(result, Failure):
        from valid8r.core.errors import ValidationError

        errors = result.validation_error  # Access error list
        if isinstance(errors, list):
            print(f'\n✗ Validation failed with {len(errors)} errors:')
            for err in errors:
                if isinstance(err, ValidationError):
                    print(f'  {err.path}: {err.message}')


def nested_schema_example() -> None:
    """Nested schema validation with field path tracking."""
    print('\n' + '=' * 60)
    print('Nested Schema Example')
    print('=' * 60)

    # Define address schema
    address_schema = schema.Schema(
        fields={
            'street': schema.Field(
                parser=parsers.parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'city': schema.Field(
                parser=parsers.parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'zipcode': schema.Field(parser=parsers.parse_str, required=True),
        }
    )

    # Define user schema with nested address
    user_schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parsers.parse_str, required=True),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'address': schema.Field(parser=address_schema.validate, required=True),
        }
    )

    # Valid nested input
    valid_input = {
        'name': 'Bob',
        'email': 'bob@example.com',
        'address': {'street': '123 Main St', 'city': 'Boston', 'zipcode': '02101'},
    }
    result = user_schema.validate(valid_input)

    if result.is_success():
        data = result.value_or({})
        print('\n✓ Validation succeeded:')
        print(f'  Name: {data["name"]}')
        print(f'  Email: {data["email"]}')
        print(f'  Address: {data["address"]["street"]}, {data["address"]["city"]}')

    # Invalid nested input - errors in nested fields
    print('\n' + '-' * 60)
    invalid_input = {
        'name': 'Bob',
        'email': 'invalid-email',
        'address': {'street': '', 'city': 'Boston', 'zipcode': ''},  # Empty fields
    }
    result = user_schema.validate(invalid_input)

    if isinstance(result, Failure):
        from valid8r.core.errors import ValidationError

        errors = result.validation_error
        if isinstance(errors, list):
            print(f'\n✗ Validation failed with {len(errors)} errors:')
            for err in errors:
                if isinstance(err, ValidationError):
                    print(f'  {err.path}: {err.message}')


def optional_fields_example() -> None:
    """Optional vs required fields."""
    print('\n' + '=' * 60)
    print('Optional Fields Example')
    print('=' * 60)

    user_schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parsers.parse_str, required=True),
            'age': schema.Field(parser=parsers.parse_int, required=False),  # Optional
            'email': schema.Field(parser=parsers.parse_email, required=False),  # Optional
        }
    )

    # Input with only required field
    minimal_input = {'name': 'Charlie'}
    result = user_schema.validate(minimal_input)

    if result.is_success():
        data = result.value_or({})
        print('\n✓ Validation succeeded with minimal data:')
        print(f'  Name: {data["name"]}')
        print(f'  Age provided: {"age" in data}')
        print(f'  Email provided: {"email" in data}')

    # Input with optional fields
    print('\n' + '-' * 60)
    full_input = {'name': 'Charlie', 'age': '30', 'email': 'charlie@example.com'}
    result = user_schema.validate(full_input)

    if result.is_success():
        data = result.value_or({})
        print('\n✓ Validation succeeded with all fields:')
        print(f'  Name: {data["name"]}')
        print(f'  Age: {data["age"]}')
        print(f'  Email: {data["email"]}')


def strict_mode_example() -> None:
    """Strict mode rejects extra fields."""
    print('\n' + '=' * 60)
    print('Strict Mode Example')
    print('=' * 60)

    # Non-strict (default) - extra fields allowed
    lenient_schema = schema.Schema(
        fields={'name': schema.Field(parser=parsers.parse_str, required=True)},
        strict=False,
    )

    input_with_extra = {'name': 'Diana', 'age': '25', 'extra': 'field'}
    result = lenient_schema.validate(input_with_extra)

    if result.is_success():
        print('\n✓ Non-strict mode: Extra fields allowed')
        print(f'  Input had {len(input_with_extra)} fields')
        print(f'  Validated data has {len(result.value_or({}))} field(s)')

    # Strict mode - extra fields rejected
    print('\n' + '-' * 60)
    strict_schema = schema.Schema(
        fields={'name': schema.Field(parser=parsers.parse_str, required=True)},
        strict=True,
    )

    result = strict_schema.validate(input_with_extra)

    if isinstance(result, Failure):
        from valid8r.core.errors import ValidationError

        errors = result.validation_error
        if isinstance(errors, list):
            print('\n✗ Strict mode: Extra fields rejected')
            print(f'  Errors: {len(errors)}')
            for err in errors:
                if isinstance(err, ValidationError):
                    print(f'  {err.path}: {err.message}')


def validator_example() -> None:
    """Combining parsers with validators."""
    print('\n' + '=' * 60)
    print('Validator Example')
    print('=' * 60)

    user_schema = schema.Schema(
        fields={
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(18) & validators.maximum(120),  # type: ignore[type-var]
                required=True,
            ),
            'username': schema.Field(
                parser=parsers.parse_str,
                validator=validators.length(3, 20),
                required=True,
            ),
        }
    )

    # Valid input
    valid_input = {'age': '25', 'username': 'john_doe'}
    result = user_schema.validate(valid_input)

    if result.is_success():
        data = result.value_or({})
        print('\n✓ Validation succeeded:')
        print(f'  Age: {data["age"]}')
        print(f'  Username: {data["username"]}')

    # Invalid - fails validators
    print('\n' + '-' * 60)
    invalid_input = {'age': '15', 'username': 'ab'}  # Too young, username too short
    result = user_schema.validate(invalid_input)

    if isinstance(result, Failure):
        from valid8r.core.errors import ValidationError

        errors = result.validation_error
        if isinstance(errors, list):
            print('\n✗ Validation failed:')
            for err in errors:
                if isinstance(err, ValidationError):
                    print(f'  {err.path}: {err.message}')


if __name__ == '__main__':
    basic_validation_example()
    nested_schema_example()
    optional_fields_example()
    strict_mode_example()
    validator_example()

    print('\n' + '=' * 60)
    print('All examples completed!')
    print('=' * 60)
