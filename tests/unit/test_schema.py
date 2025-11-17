"""Unit tests for schema validation module.

This module tests the Schema and Field classes for dict validation
with error accumulation and field path tracking.
"""

from __future__ import annotations

from typing import Any


def parse_str(val: Any) -> Any:  # noqa: ANN401
    """Parse input as string."""
    from valid8r.core.maybe import Success

    return Success(str(val))


def get_errors(result: Any) -> list[Any]:  # noqa: ANN401
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


class DescribeField:
    """Tests for Field class initialization and attributes."""

    def it_creates_required_field_with_parser(self) -> None:
        """Create a required field with a parser function."""
        from valid8r.core import (
            parsers,
            schema,
        )

        field = schema.Field(parser=parsers.parse_int, required=True)

        assert field.parser == parsers.parse_int
        assert field.required is True
        assert field.validator is None

    def it_creates_optional_field(self) -> None:
        """Create an optional field (required=False)."""
        from valid8r.core import schema

        field = schema.Field(parser=parse_str, required=False)

        assert field.parser == parse_str
        assert field.required is False

    def it_creates_field_with_validator(self) -> None:
        """Create a field with both parser and validator."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

        field = schema.Field(
            parser=parsers.parse_int,
            validator=validators.minimum(0),
            required=True,
        )

        assert field.parser == parsers.parse_int
        assert field.validator is not None
        assert field.required is True


class DescribeSchemaBasicValidation:
    """Tests for basic schema validation with single fields."""

    def it_validates_dict_with_all_valid_fields(self) -> None:
        """Validate a dict where all fields parse successfully."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(parser=parsers.parse_int, required=True),
                'email': schema.Field(parser=parsers.parse_email, required=True),
            }
        )

        result = s.validate({'age': '25', 'email': 'alice@example.com'})

        assert result.is_success()
        data = result.value_or({})
        assert data['age'] == 25
        # Email is returned as EmailAddress object
        from valid8r.core.parsers import EmailAddress

        assert isinstance(data['email'], EmailAddress)
        assert data['email'].local == 'alice'
        assert data['email'].domain == 'example.com'

    def it_accumulates_multiple_field_errors(self) -> None:
        """Collect all field errors instead of stopping at first failure."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(parser=parsers.parse_int, required=True),
                'email': schema.Field(parser=parsers.parse_email, required=True),
            }
        )

        result = s.validate({'age': 'invalid', 'email': 'not-an-email'})

        assert result.is_failure()
        errors = get_errors(result)
        assert len(errors) == 2
        error_paths = [e.path for e in errors]
        assert '.age' in error_paths
        assert '.email' in error_paths

    def it_validates_field_with_combined_parser_and_validator(self) -> None:
        """Apply both parser and validator to a field."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(
                    parser=parsers.parse_int,
                    validator=validators.minimum(0) & validators.maximum(120),
                    required=True,
                ),
            }
        )

        result = s.validate({'age': '-5'})

        assert result.is_failure()
        errors = get_errors(result)
        assert len(errors) == 1
        assert errors[0].path == '.age'
        # Check that error mentions the constraint (minimum/at least)
        assert 'minimum' in errors[0].message.lower() or 'at least' in errors[0].message.lower()


class DescribeSchemaRequiredAndOptional:
    """Tests for required vs optional field handling."""

    def it_validates_when_optional_field_missing(self) -> None:
        """Succeed when optional field is not provided."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
                'age': schema.Field(parser=parsers.parse_int, required=False),
            }
        )

        result = s.validate({'name': 'Alice'})

        assert result.is_success()
        data = result.value_or({})
        assert data['name'] == 'Alice'
        assert 'age' not in data

    def it_fails_when_required_field_missing(self) -> None:
        """Fail when required field is not provided."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
                'age': schema.Field(parser=parsers.parse_int, required=False),
            }
        )

        result = s.validate({'age': '25'})

        assert result.is_failure()
        errors = get_errors(result)
        assert any(e.path == '.name' for e in errors)
        assert any('required' in e.message.lower() for e in errors)

    def it_validates_optional_field_when_provided(self) -> None:
        """Validate optional field if it is provided."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
                'age': schema.Field(parser=parsers.parse_int, required=False),
            }
        )

        result = s.validate({'name': 'Alice', 'age': '30'})

        assert result.is_success()
        data = result.value_or({})
        assert data['name'] == 'Alice'
        assert data['age'] == 30


class DescribeSchemaNestedValidation:
    """Tests for nested schema composition and field path tracking."""

    def it_validates_nested_schema_successfully(self) -> None:
        """Validate nested objects using composed schemas."""
        from valid8r.core import (
            schema,
            validators,
        )

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

        user_schema = schema.Schema(
            fields={
                'address': schema.Field(parser=address_schema.validate, required=True),
            }
        )

        result = user_schema.validate({'address': {'street': '123 Main St', 'city': 'Boston'}})

        assert result.is_success()
        data = result.value_or({})
        assert data['address']['street'] == '123 Main St'
        assert data['address']['city'] == 'Boston'

    def it_tracks_field_paths_in_nested_objects(self) -> None:
        """Include full field paths for errors in nested objects."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

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

        outer_schema = schema.Schema(
            fields={
                'user': schema.Field(parser=user_schema.validate, required=True),
            }
        )

        result = outer_schema.validate({'user': {'name': '', 'email': 'bad'}})

        assert result.is_failure()
        errors = get_errors(result)
        error_paths = [e.path for e in errors]
        assert '.user.name' in error_paths
        assert '.user.email' in error_paths


class DescribeSchemaStrictMode:
    """Tests for strict mode (rejecting extra fields)."""

    def it_allows_extra_fields_by_default(self) -> None:
        """Allow extra fields when strict mode is not enabled."""
        from valid8r.core import schema

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
            }
        )

        result = s.validate({'name': 'Alice', 'age': '25'})

        assert result.is_success()
        data = result.value_or({})
        assert data['name'] == 'Alice'
        # Extra field 'age' is ignored

    def it_rejects_extra_fields_in_strict_mode(self) -> None:
        """Reject input with extra fields when strict=True."""
        from valid8r.core import schema

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
            },
            strict=True,
        )

        result = s.validate({'name': 'Alice', 'age': '25'})

        assert result.is_failure()
        errors = get_errors(result)
        assert any('unexpected' in e.message.lower() or 'extra' in e.message.lower() for e in errors)


class DescribeSchemaEmptyInput:
    """Tests for empty input handling."""

    def it_fails_with_empty_dict_when_required_fields_exist(self) -> None:
        """Fail validation when empty dict provided but fields are required."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'name': schema.Field(parser=parse_str, required=True),
                'email': schema.Field(parser=parsers.parse_email, required=True),
            }
        )

        result = s.validate({})

        assert result.is_failure()
        errors = get_errors(result)
        error_paths = [e.path for e in errors]
        assert '.name' in error_paths
        assert '.email' in error_paths


class DescribeSchemaErrorContext:
    """Tests for error context and helpful error messages."""

    def it_includes_field_path_in_error(self) -> None:
        """Ensure errors include the field path for debugging."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(
                    parser=parsers.parse_int,
                    validator=validators.minimum(18),
                    required=True,
                ),
            }
        )

        result = s.validate({'age': '15'})

        assert result.is_failure()
        errors = get_errors(result)
        assert errors[0].path == '.age'

    def it_includes_constraint_details_in_error_context(self) -> None:
        """Include constraint information in error context."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(
                    parser=parsers.parse_int,
                    validator=validators.minimum(18),
                    required=True,
                ),
            }
        )

        result = s.validate({'age': '15'})

        assert result.is_failure()
        errors = get_errors(result)
        error = errors[0]
        # Check that constraint info is in message or context
        has_constraint_info = (
            'minimum' in error.message.lower()
            or 'at least' in error.message.lower()
            or (error.context and any('min' in str(k).lower() for k in error.context))
        )
        assert has_constraint_info


class DescribeSchemaTypePreservation:
    """Tests for type preservation after parsing."""

    def it_returns_typed_values_not_strings(self) -> None:
        """Return properly typed values (int, bool) not strings."""
        from valid8r.core import (
            parsers,
            schema,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(parser=parsers.parse_int, required=True),
                'active': schema.Field(parser=parsers.parse_bool, required=True),
            }
        )

        result = s.validate({'age': '25', 'active': 'true'})

        assert result.is_success()
        data = result.value_or({})
        assert isinstance(data['age'], int)
        assert data['age'] == 25
        assert isinstance(data['active'], bool)
        assert data['active'] is True


class DescribeSchemaComplexScenarios:
    """Tests for complex nested validation scenarios."""

    def it_accumulates_errors_from_deeply_nested_fields(self) -> None:
        """Collect errors from multiple levels of nesting."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

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

        user_schema = schema.Schema(
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

        result = user_schema.validate(
            {
                'username': '',
                'email': 'not-an-email',
                'password': 'weak',
                'address': {
                    'street': '',
                    'city': 'Boston',
                    'zipcode': '',
                },
            }
        )

        assert result.is_failure()
        errors = get_errors(result)
        assert len(errors) >= 4
        error_paths = [e.path for e in errors]
        assert '.username' in error_paths
        assert '.email' in error_paths
        assert '.password' in error_paths
        assert '.address.street' in error_paths or '.address.zipcode' in error_paths
