"""BDD step definitions for schema validation feature.

This module implements black-box tests for the Schema API through
step definitions that exercise the public interface.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from behave import (
    given,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context


def unquote(s: str) -> str:
    """Remove surrounding quotes from Gherkin parameter values.

    Behave includes literal quote characters when parsing parameters,
    so "25" becomes the string '"25"' instead of '25'.
    """
    return s.strip('"\'')


def parse_str(val: Any) -> Any:
    """Parse input as string."""
    from valid8r.core.maybe import Success

    return Success(str(val))


def get_errors(result: Any) -> list[Any]:
    """Extract error list from a Failure result.

    Schema validation returns Failure with a list of ValidationError objects.
    This helper extracts that list safely.
    """
    from valid8r.core.maybe import Failure

    match result:
        case Failure():
            # Access the internal _validation_error directly if it's a list
            if isinstance(result._validation_error, list):  # noqa: SLF001
                return result._validation_error  # noqa: SLF001
            # Otherwise wrap the single error in a list
            return [result._validation_error]  # noqa: SLF001
        case _:
            return []


# Context to store schema validation results
class SchemaContext:
    """Test context for schema validation scenarios."""

    def __init__(self) -> None:
        """Initialize the schema context."""
        self.schema = None
        self.input_data: dict[str, Any] = {}
        self.result = None
        self.errors: list[Any] = []


def get_schema_context(context: Context) -> SchemaContext:
    """Get or create the schema context for the current test."""
    if not hasattr(context, 'schema_context'):
        context.schema_context = SchemaContext()
    return context.schema_context


@given('the schema validation API is available')
def step_schema_api_available(context: Context) -> None:
    """Verify that the schema module is importable."""
    # This will fail until we implement the schema module
    from valid8r.core import schema

    assert schema is not None


@given('a schema with age as parse_int and email as parse_email')
def step_schema_age_and_email(context: Context) -> None:
    """Define a simple schema with age and email fields."""
    from valid8r.core import (
        parsers,
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'age': schema.Field(parser=parsers.parse_int, required=True),
            'email': schema.Field(parser=parsers.parse_email, required=True),
        }
    )


@given('input with age {age} and email {email}')
def step_input_age_and_email(context: Context, age: str, email: str) -> None:
    """Provide input data with age and email."""
    sc = get_schema_context(context)
    sc.input_data = {'age': unquote(age), 'email': unquote(email)}


@given('a schema with nested user object')
def step_schema_nested_user(context: Context) -> None:
    """Define a schema with a nested user object."""
    sc = get_schema_context(context)
    # Will be expanded in the next step
    sc.schema = None


@given('the user schema has name as non_empty_string and email as parse_email')
def step_user_schema_fields(context: Context) -> None:
    """Define fields for the nested user schema."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    sc = get_schema_context(context)
    user_schema = schema.Schema(
        fields={
            'name': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'email': schema.Field(parser=parsers.parse_email, required=True),
        }
    )
    sc.schema = schema.Schema(
        fields={
            'user': schema.Field(parser=user_schema.validate, required=True),
        }
    )


@given('input with user name {name} and user email {email}')
def step_input_nested_user(context: Context, name: str, email: str) -> None:
    """Provide nested input data for user object."""
    sc = get_schema_context(context)
    sc.input_data = {'user': {'name': unquote(name), 'email': unquote(email)}}


@given('a schema with age as parse_int with minimum {min_val:d} and maximum {max_val:d}')
def step_schema_age_with_validators(context: Context, min_val: int, max_val: int) -> None:
    """Define a schema with age field that has validators."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(min_val) & validators.maximum(max_val),
                required=True,
            ),
        }
    )


@given('input with only age {age}')
def step_input_with_age_only(context: Context, age: str) -> None:
    """Provide input with just age field."""
    sc = get_schema_context(context)
    sc.input_data = {'age': unquote(age)}


@given('a schema with required name and optional age')
def step_schema_required_and_optional(context: Context) -> None:
    """Define a schema with both required and optional fields."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'name': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'age': schema.Field(parser=parsers.parse_int, required=False),
        }
    )


@given('input with only name {name}')
def step_input_with_only_name(context: Context, name: str) -> None:
    """Provide input with only name field."""
    sc = get_schema_context(context)
    sc.input_data = {'name': unquote(name)}


@given('a schema with address object')
def step_schema_with_address(context: Context) -> None:
    """Define a schema with an address object."""
    sc = get_schema_context(context)
    # Will be defined in next step
    sc.schema = None


@given('the address schema has street and city as non_empty_string')
def step_address_schema_fields(context: Context) -> None:
    """Define fields for the address schema."""
    from valid8r.core import (
        schema,
        validators,
    )

    sc = get_schema_context(context)
    address_schema = schema.Schema(
        fields={
            'street': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'city': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )
    sc.schema = schema.Schema(
        fields={
            'address': schema.Field(parser=address_schema.validate, required=True),
        }
    )


@given('input with address street {street} and city {city}')
def step_input_address(context: Context, street: str, city: str) -> None:
    """Provide input with address object."""
    sc = get_schema_context(context)
    sc.input_data = {'address': {'street': unquote(street), 'city': unquote(city)}}


@given('a schema with tags as parse_list with parse_int elements')
def step_schema_with_list(context: Context) -> None:
    """Define a schema with a list field."""
    from valid8r.core import (
        parsers,
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'tags': schema.Field(
                parser=lambda val: parsers.parse_list(val, element_parser=parsers.parse_int),
                required=True,
            ),
        }
    )


@given('input with tags {tags}')
def step_input_with_tags(context: Context, tags: str) -> None:
    """Provide input with tags field."""
    sc = get_schema_context(context)
    sc.input_data = {'tags': unquote(tags)}


@given('a schema with user name and addresses list')
def step_schema_complex_nested(context: Context) -> None:
    """Define a complex schema with nested objects and arrays."""
    sc = get_schema_context(context)
    # Will be expanded in next step
    sc.schema = None


@given('the address schema has street and zipcode')
def step_address_schema_street_zipcode(context: Context) -> None:
    """Define address schema with street and zipcode."""
    from valid8r.core import (
        schema,
        validators,
    )

    sc = get_schema_context(context)
    address_schema = schema.Schema(
        fields={
            'street': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'zipcode': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )

    def parse_addresses(val: object) -> object:
        """Parse a list of addresses."""
        # This is a placeholder - will be implemented properly
        from valid8r.core.maybe import (
            Failure,
            Success,
        )

        if not isinstance(val, list):
            return Failure('Expected list of addresses')
        results = []
        for addr in val:
            result = address_schema.validate(addr)
            if result.is_failure():
                return result
            results.append(result.value_or({}))
        return Success(results)

    user_schema = schema.Schema(
        fields={
            'name': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )

    sc.schema = schema.Schema(
        fields={
            'user': schema.Field(parser=user_schema.validate, required=True),
            'addresses': schema.Field(parser=parse_addresses, required=True),
        }
    )


@given('input with user name {name} and two addresses with invalid data')
def step_input_complex_invalid(context: Context, name: str) -> None:
    """Provide complex nested input with multiple errors."""
    sc = get_schema_context(context)
    sc.input_data = {
        'user': {'name': unquote(name)},
        'addresses': [
            {'street': '', 'zipcode': '12345'},  # Empty street
            {'street': '456 Oak Ave', 'zipcode': ''},  # Empty zipcode
        ],
    }


@given('a schema with required name and email')
def step_schema_required_fields(context: Context) -> None:
    """Define a schema with required fields."""
    from valid8r.core import (
        parsers,
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parse_str, required=True),
            'email': schema.Field(parser=parsers.parse_email, required=True),
        }
    )


@given('empty input')
def step_empty_input(context: Context) -> None:
    """Provide empty input dictionary."""
    sc = get_schema_context(context)
    sc.input_data = {}


@given('a schema with only name field')
def step_schema_only_name(context: Context) -> None:
    """Define a schema with only name field."""
    from valid8r.core import (
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(fields={'name': schema.Field(parser=parse_str, required=True)})


@given('input with name {name} and extra field age {age}')
def step_input_with_extra_field(context: Context, name: str, age: str) -> None:
    """Provide input with an extra field."""
    sc = get_schema_context(context)
    sc.input_data = {'name': unquote(name), 'age': unquote(age)}


@given('a strict schema with only name field')
def step_strict_schema_only_name(context: Context) -> None:
    """Define a strict schema that rejects extra fields."""
    from valid8r.core import (
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={'name': schema.Field(parser=parse_str, required=True)},
        strict=True,
    )


@given('a schema for user registration')
def step_schema_user_registration(context: Context) -> None:
    """Define a complex schema for user registration."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    sc = get_schema_context(context)
    address_schema = schema.Schema(
        fields={
            'street': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'city': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'zipcode': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )

    sc.schema = schema.Schema(
        fields={
            'username': schema.Field(
                parser=parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'password': schema.Field(
                parser=parse_str,
                validator=validators.length(8, 100),
                required=True,
            ),
            'address': schema.Field(parser=address_schema.validate, required=True),
        }
    )


@given('the schema requires username, email, password, and address')
def step_registration_schema_requirements(context: Context) -> None:
    """Verify registration schema requirements (already defined above)."""
    sc = get_schema_context(context)
    assert sc.schema is not None


@given('input with invalid username, malformed email, weak password, and incomplete address')
def step_input_registration_invalid(context: Context) -> None:
    """Provide registration input with multiple errors."""
    sc = get_schema_context(context)
    sc.input_data = {
        'username': '',  # Empty username
        'email': 'not-an-email',  # Invalid email
        'password': 'weak',  # Too short (< 8 chars)
        'address': {
            'street': '',  # Empty street
            'city': 'Boston',
            'zipcode': '',  # Empty zipcode
        },
    }


@given('a schema with age as parse_int and active as parse_bool')
def step_schema_int_and_bool(context: Context) -> None:
    """Define a schema with int and bool fields."""
    from valid8r.core import (
        parsers,
        schema,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'age': schema.Field(parser=parsers.parse_int, required=True),
            'active': schema.Field(parser=parsers.parse_bool, required=True),
        }
    )


@given('input with age {age} and active {active}')
def step_input_age_and_active(context: Context, age: str, active: str) -> None:
    """Provide input with age and active fields."""
    sc = get_schema_context(context)
    sc.input_data = {'age': unquote(age), 'active': unquote(active)}


@given('a schema with age as parse_int with minimum {min_val:d}')
def step_schema_age_minimum(context: Context, min_val: int) -> None:
    """Define a schema with age that has minimum validator."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    sc = get_schema_context(context)
    sc.schema = schema.Schema(
        fields={
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(min_val),
                required=True,
            ),
        }
    )


@when('Alice validates the input')
def step_validate_input(context: Context) -> None:
    """Execute schema validation on the input data."""
    sc = get_schema_context(context)
    sc.result = sc.schema.validate(sc.input_data)


@then('the validation succeeds')
def step_validation_succeeds(context: Context) -> None:
    """Assert that validation succeeded."""
    sc = get_schema_context(context)
    if not sc.result.is_success():
        errors = get_errors(sc.result)
        error_msg = ', '.join(f'{e.path}: {e.message}' for e in errors[:3])
        msg = f'Expected success but got errors: {error_msg}'
        raise AssertionError(msg)


@then('the validation fails')
def step_validation_fails(context: Context) -> None:
    """Assert that validation failed."""
    sc = get_schema_context(context)
    assert sc.result.is_failure(), f'Expected failure but validation succeeded with: {sc.result.value_or(None)}'


@then('the result contains age {expected_age:d}')
def step_result_contains_age(context: Context, expected_age: int) -> None:
    """Assert that result contains expected age value."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'age' in result_data, f'Age not found in result: {result_data}'
    assert result_data['age'] == expected_age, f'Expected age {expected_age} but got {result_data["age"]}'


@then('the result contains email {expected_email}')
def step_result_contains_email(context: Context, expected_email: str) -> None:
    """Assert that result contains expected email value."""
    from valid8r.core.parsers import EmailAddress

    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'email' in result_data, f'Email not found in result: {result_data}'
    # Email is returned as EmailAddress object
    email_obj = result_data['email']
    expected = unquote(expected_email)  # Remove quotes from Gherkin parameter
    # EmailAddress is a dataclass - reconstruct the email string
    email_value = f'{email_obj.local}@{email_obj.domain}' if isinstance(email_obj, EmailAddress) else str(email_obj)
    assert email_value == expected, f'Expected email {expected} but got {email_value}'


@then('the result contains two errors')
def step_result_contains_two_errors(context: Context) -> None:
    """Assert that result contains exactly two errors."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    assert len(errors) == 2, f'Expected 2 errors but got {len(errors)}: {errors}'


@then('the result contains an error for path {expected_path}')
def step_result_contains_error_for_path(context: Context, expected_path: str) -> None:
    """Assert that result contains an error for the specified path."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    paths = [error.path for error in errors]
    expected = unquote(expected_path)  # Remove quotes if present
    assert expected in paths, f'Expected error for path {expected} but got paths: {paths}'


@then('the validation error message contains "{keyword}"')
def step_validation_error_contains_keyword(context: Context, keyword: str) -> None:
    """Assert that at least one validation error message contains the keyword."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    messages = [error.message.lower() for error in errors]
    keyword_lower = keyword.lower()
    assert any(keyword_lower in msg for msg in messages), f'Expected keyword "{keyword}" in error messages: {messages}'


@then('the result contains name {expected_name}')
def step_result_contains_name(context: Context, expected_name: str) -> None:
    """Assert that result contains expected name value."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'name' in result_data, f'Name not found in result: {result_data}'
    expected = unquote(expected_name)
    assert result_data['name'] == expected, f'Expected name {expected} but got {result_data["name"]}'


@then('the result does not contain age')
def step_result_does_not_contain_age(context: Context) -> None:
    """Assert that result does not contain age field."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'age' not in result_data, f'Did not expect age in result but got: {result_data}'


@then('the result contains address street {expected_street}')
def step_result_contains_address_street(context: Context, expected_street: str) -> None:
    """Assert that result contains expected address street value."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'address' in result_data, f'Address not found in result: {result_data}'
    assert 'street' in result_data['address'], f'Street not found in address: {result_data["address"]}'
    actual_street = result_data['address']['street']
    expected = unquote(expected_street)
    assert actual_street == expected, f'Expected street {expected} but got {actual_street}'


@then('the result contains address city {expected_city}')
def step_result_contains_address_city(context: Context, expected_city: str) -> None:
    """Assert that result contains expected address city value."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'address' in result_data, f'Address not found in result: {result_data}'
    assert 'city' in result_data['address'], f'City not found in address: {result_data["address"]}'
    actual_city = result_data['address']['city']
    expected = unquote(expected_city)
    assert actual_city == expected, f'Expected city {expected} but got {actual_city}'


@then('the result contains errors for multiple paths')
def step_result_contains_multiple_path_errors(context: Context) -> None:
    """Assert that result contains errors for multiple different paths."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    paths = {error.path for error in errors}
    assert len(paths) > 1, f'Expected errors for multiple paths but got: {paths}'


@then('the result contains an error mentioning {keyword}')
def step_result_contains_error_mentioning(context: Context, keyword: str) -> None:
    """Assert that at least one error mentions the keyword."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    messages = [error.message.lower() for error in errors]
    keyword_lower = keyword.strip('"').lower()
    assert any(keyword_lower in msg for msg in messages), (
        f'Expected keyword "{keyword}" in at least one error: {messages}'
    )


@then('the result contains at least four errors')
def step_result_contains_at_least_four_errors(context: Context) -> None:
    """Assert that result contains at least four errors."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    assert len(errors) >= 4, f'Expected at least 4 errors but got {len(errors)}: {errors}'


@then('each error has a clear field path')
def step_each_error_has_field_path(context: Context) -> None:
    """Assert that each error has a non-empty field path."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    for error in errors:
        assert error.path, f'Error missing field path: {error}'
        assert error.path.startswith('.'), f'Field path should start with ".": {error.path}'


@then('the result contains age as integer {expected_age:d}')
def step_result_contains_age_as_integer(context: Context, expected_age: int) -> None:
    """Assert that result contains age as an integer type."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'age' in result_data, f'Age not found in result: {result_data}'
    assert isinstance(result_data['age'], int), f'Expected integer but got {type(result_data["age"])}'
    assert result_data['age'] == expected_age, f'Expected age {expected_age} but got {result_data["age"]}'


@then('the result contains active as boolean {expected_active}')
def step_result_contains_active_as_boolean(context: Context, expected_active: str) -> None:
    """Assert that result contains active as a boolean type."""
    sc = get_schema_context(context)
    result_data = sc.result.value_or({})
    assert 'active' in result_data, f'Active not found in result: {result_data}'
    assert isinstance(result_data['active'], bool), f'Expected bool but got {type(result_data["active"])}'
    expected_bool = expected_active.lower() == 'true'
    assert result_data['active'] == expected_bool, f'Expected active {expected_bool} but got {result_data["active"]}'


@then('the error includes the field path {expected_path}')
def step_error_includes_field_path(context: Context, expected_path: str) -> None:
    """Assert that at least one error has the specified field path."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    paths = [error.path for error in errors]
    expected = unquote(expected_path)  # Remove quotes if present
    assert expected in paths, f'Expected path {expected} in errors but got: {paths}'


@then('the error includes the invalid value {expected_value}')
def step_error_includes_invalid_value(context: Context, expected_value: str) -> None:
    """Assert that at least one error context includes the invalid value."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    found = False
    for error in errors:
        if error.context and 'value' in error.context and str(error.context['value']) == expected_value.strip('"'):
            found = True
            break
    assert found, f'Expected value {expected_value} in error context but not found in: {errors}'


@then('the error includes the constraint {expected_constraint}')
def step_error_includes_constraint(context: Context, expected_constraint: str) -> None:
    """Assert that at least one error mentions the constraint."""
    sc = get_schema_context(context)
    errors = get_errors(sc.result)
    constraint = unquote(expected_constraint).lower()
    found = False
    for error in errors:
        error_msg = error.message.lower()
        # Check if constraint value appears in error message
        # e.g., "minimum 18" - extract "18" and check if it's in "Value must be at least 18"
        # Also accept semantic matches: "minimum" -> "at least", "maximum" -> "at most"
        parts = constraint.split()
        numeric_parts = [p for p in parts if p.isdigit()]
        keyword_parts = [p for p in parts if not p.isdigit()]

        # Check if numeric value appears in error message
        if numeric_parts and all(num in error_msg for num in numeric_parts):
            # Also check if there's semantic alignment
            if ('minimum' in keyword_parts and ('at least' in error_msg or 'minimum' in error_msg)) or (
                'maximum' in keyword_parts and ('at most' in error_msg or 'maximum' in error_msg)
            ):
                found = True
                break
            if not keyword_parts:  # Just numeric value
                found = True
                break
        # Also check context
        if error.context:
            context_str = str(error.context).lower()
            if any(part in context_str for part in parts):
                found = True
                break
    assert found, f'Expected constraint "{constraint}" related info in errors but not found in: {errors}'
