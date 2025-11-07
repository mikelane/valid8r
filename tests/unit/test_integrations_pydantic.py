"""Tests for Pydantic integration module.

This module tests the validator_from_parser function that converts valid8r parsers
into Pydantic field validators.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
)

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.core.parsers import EmailAddress  # noqa: TC001
from valid8r.integrations.pydantic import validator_from_parser

if TYPE_CHECKING:
    from typing import Any

    from valid8r.core.maybe import Maybe


class DescribeValidatorFromParser:
    """Test suite for validator_from_parser function."""

    def it_converts_success_to_valid_pydantic_field(self) -> None:
        """Convert parser returning Success to valid Pydantic field."""
        validator_func = validator_from_parser(parsers.parse_int)
        result = validator_func('42')
        assert result == 42

    def it_converts_failure_to_pydantic_validation_error(self) -> None:
        """Convert parser returning Failure to Pydantic ValidationError."""
        validator_func = validator_from_parser(parsers.parse_int)
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            validator_func('not-a-number')
        assert 'valid integer' in str(exc_info.value).lower()

    def it_uses_custom_error_prefix(self) -> None:
        """Use custom error messages in Pydantic errors."""
        validator_func = validator_from_parser(parsers.parse_int, error_prefix='User ID')
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            validator_func('invalid')
        error_msg = str(exc_info.value)
        assert error_msg.startswith('User ID')

    def it_chains_validators_using_operator_overloading(self) -> None:
        """Chain validators using Pydantic field_validator."""
        # Create a chained validator using bind: parse_int THEN minimum(0) AND maximum(120)
        chained_validator = validators.minimum(0) & validators.maximum(120)

        def chained_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            return parsers.parse_int(value).bind(chained_validator)

        validator_func = validator_from_parser(chained_parser)

        # Valid value
        assert validator_func('25') == 25

        # Below minimum
        with pytest.raises(ValueError):  # noqa: PT011
            validator_func('-1')

        # Above maximum
        with pytest.raises(ValueError):  # noqa: PT011
            validator_func('150')

    def it_preserves_error_messages_from_parsers(self) -> None:
        """Preserve valid8r error messages in Pydantic errors."""
        validator_func = validator_from_parser(parsers.parse_email)
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            validator_func('not-an-email')
        # The error should contain something about email format
        error_msg = str(exc_info.value).lower()
        assert 'email' in error_msg or 'invalid' in error_msg


class DescribePydanticBaseModelIntegration:
    """Test suite for Pydantic BaseModel integration."""

    def it_validates_simple_field_with_parse_int(self) -> None:
        """Field validation with parse_int."""

        class User(BaseModel):
            age: int

            @field_validator('age', mode='before')
            @classmethod
            def validate_age(cls, v: Any) -> int:  # noqa: ANN401
                return validator_from_parser(parsers.parse_int)(v)

        # Valid input
        user = User(age='25')
        assert user.age == 25

        # Invalid input
        with pytest.raises(ValidationError) as exc_info:
            User(age='not-a-number')
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('age',)
        assert 'integer' in errors[0]['msg'].lower()

    def it_validates_field_with_parse_email(self) -> None:
        """Field validation with parse_email."""

        class UserProfile(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
                return validator_from_parser(parsers.parse_email)(v)

        # Valid email
        profile = UserProfile(email='user@example.com')
        assert profile.email.local == 'user'
        assert profile.email.domain == 'example.com'

        # Invalid email
        with pytest.raises(ValidationError):
            UserProfile(email='not-an-email')

    def it_validates_field_with_chained_validators(self) -> None:
        """Field validation with chained validators (parse_int THEN minimum(0))."""

        class Product(BaseModel):
            stock: int

            @field_validator('stock', mode='before')
            @classmethod
            def validate_stock(cls, v: Any) -> int:  # noqa: ANN401
                def stock_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
                    return parsers.parse_int(value).bind(validators.minimum(0))

                return validator_from_parser(stock_parser)(v)

        # Valid stock
        product = Product(stock='10')
        assert product.stock == 10

        # Negative stock (should fail)
        with pytest.raises(ValidationError) as exc_info:
            Product(stock='-5')
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert 'minimum' in errors[0]['msg'].lower() or 'least' in errors[0]['msg'].lower()

    def it_validates_multiple_fields_with_different_parsers(self) -> None:
        """Multiple fields with different parsers."""

        class ContactForm(BaseModel):
            name: str
            age: int
            email: EmailAddress

            @field_validator('age', mode='before')
            @classmethod
            def validate_age(cls, v: Any) -> int:  # noqa: ANN401
                def age_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
                    return parsers.parse_int(value).bind(validators.between(0, 120))

                return validator_from_parser(age_parser)(v)

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
                return validator_from_parser(parsers.parse_email)(v)

        # Valid data
        form = ContactForm(name='John Doe', age='30', email='john@example.com')
        assert form.name == 'John Doe'
        assert form.age == 30
        assert form.email.local == 'john'

        # Invalid age
        with pytest.raises(ValidationError) as exc_info:
            ContactForm(name='Jane', age='150', email='jane@example.com')
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('age',) for err in errors)

        # Invalid email
        with pytest.raises(ValidationError) as exc_info:
            ContactForm(name='Bob', age='25', email='invalid')
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('email',) for err in errors)

    def it_works_with_optional_fields(self) -> None:
        """Work with optional fields using Pydantic."""

        class OptionalProfile(BaseModel):
            age: int | None = None

            @field_validator('age', mode='before')
            @classmethod
            def validate_age(cls, v: Any) -> int | None:  # noqa: ANN401
                if v is None:
                    return v
                return validator_from_parser(parsers.parse_int)(v)

        # With value
        profile = OptionalProfile(age='42')
        assert profile.age == 42

        # Without value (None)
        profile_none = OptionalProfile()
        assert profile_none.age is None

        # Invalid value
        with pytest.raises(ValidationError):
            OptionalProfile(age='invalid')
