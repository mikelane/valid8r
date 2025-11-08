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
from valid8r.core.maybe import Maybe
from valid8r.core.parsers import EmailAddress
from valid8r.integrations.pydantic import validator_from_parser

if TYPE_CHECKING:
    from typing import Any

    from valid8r.core.parsers import PhoneNumber


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


class DescribeNestedModelValidation:
    """Test suite for nested model validation with valid8r parsers."""

    def it_validates_nested_model_with_valid8r_parser(self) -> None:
        """Validate nested model with valid8r parser (Gherkin scenario 1)."""
        from valid8r.core.parsers import PhoneNumber  # type: ignore[misc]  # Runtime needed

        class Address(BaseModel):
            phone: PhoneNumber

            @field_validator('phone', mode='before')
            @classmethod
            def validate_phone(cls, v: Any) -> PhoneNumber:  # noqa: ANN401
                return validator_from_parser(parsers.parse_phone)(v)

        class User(BaseModel):
            name: str
            address: Address

        # Valid nested data
        user = User(name='Alice', address={'phone': '(206) 234-5678'})
        assert user.name == 'Alice'
        assert isinstance(user.address.phone, PhoneNumber)
        assert user.address.phone.area_code == '206'
        assert user.address.phone.exchange == '234'
        assert user.address.phone.subscriber == '5678'

    def it_includes_field_path_in_nested_validation_errors(self) -> None:
        """Nested validation errors include field path (Gherkin scenario 2)."""
        from valid8r.core.parsers import PhoneNumber  # noqa: F401  # Pydantic needs at runtime

        class Address(BaseModel):
            phone: PhoneNumber

            @field_validator('phone', mode='before')
            @classmethod
            def validate_phone(cls, v: Any) -> PhoneNumber:  # noqa: ANN401
                return validator_from_parser(parsers.parse_phone)(v)

        class User(BaseModel):
            name: str
            address: Address

        # Invalid nested phone number
        with pytest.raises(ValidationError) as exc_info:
            User(name='Alice', address={'phone': 'invalid'})

        errors = exc_info.value.errors()
        assert len(errors) == 1

        # Check field path includes 'address.phone'
        error_loc = errors[0]['loc']
        assert 'address' in error_loc
        assert 'phone' in error_loc

        # Error message contains valid8r parse_phone error
        error_msg = errors[0]['msg'].lower()
        assert 'phone' in error_msg or 'invalid' in error_msg

    def it_validates_three_level_nested_models(self) -> None:
        """Validate three-level nested models."""

        class Contact(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
                return validator_from_parser(parsers.parse_email)(v)

        class Department(BaseModel):
            name: str
            contact: Contact

        class Company(BaseModel):
            name: str
            department: Department

        # Valid three-level nested data
        company = Company(
            name='Acme Corp',
            department={'name': 'Engineering', 'contact': {'email': 'eng@acme.com'}},
        )
        assert company.name == 'Acme Corp'
        assert company.department.name == 'Engineering'
        assert company.department.contact.email.local == 'eng'
        assert company.department.contact.email.domain == 'acme.com'

    def it_includes_full_path_for_deeply_nested_validation_errors(self) -> None:
        """Deeply nested validation errors include full field path."""

        class Contact(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
                return validator_from_parser(parsers.parse_email)(v)

        class Department(BaseModel):
            name: str
            contact: Contact

        class Company(BaseModel):
            name: str
            department: Department

        # Invalid email at third level
        with pytest.raises(ValidationError) as exc_info:
            Company(name='Acme', department={'name': 'Eng', 'contact': {'email': 'not-an-email'}})

        errors = exc_info.value.errors()
        assert len(errors) == 1

        # Check full field path
        error_loc = errors[0]['loc']
        assert 'department' in error_loc
        assert 'contact' in error_loc
        assert 'email' in error_loc


class DescribeListOfModelsValidation:
    """Test suite for validating lists of models with valid8r parsers."""

    def it_validates_list_of_models_with_valid8r_parsers(self) -> None:
        """Validate list of models with valid8r parsers (Gherkin scenario 3)."""

        class LineItem(BaseModel):
            quantity: int

            @field_validator('quantity', mode='before')
            @classmethod
            def validate_quantity(cls, v: Any) -> int:  # noqa: ANN401
                def quantity_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
                    return parsers.parse_int(value).bind(validators.minimum(1))

                return validator_from_parser(quantity_parser)(v)

        class Order(BaseModel):
            items: list[LineItem]

        # Valid list of items
        order = Order(items=[{'quantity': '5'}, {'quantity': '10'}])
        assert len(order.items) == 2
        assert order.items[0].quantity == 5
        assert order.items[1].quantity == 10

    def it_validates_each_item_in_list_and_reports_index(self) -> None:
        """Validate each item in list and report index in error (Gherkin scenario 3)."""

        class LineItem(BaseModel):
            quantity: int

            @field_validator('quantity', mode='before')
            @classmethod
            def validate_quantity(cls, v: Any) -> int:  # noqa: ANN401
                def quantity_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
                    return parsers.parse_int(value).bind(validators.minimum(1))

                return validator_from_parser(quantity_parser)(v)

        class Order(BaseModel):
            items: list[LineItem]

        # Invalid quantity in second item
        with pytest.raises(ValidationError) as exc_info:
            Order(items=[{'quantity': '5'}, {'quantity': '0'}])

        errors = exc_info.value.errors()
        assert len(errors) == 1

        # Check error location includes items[1].quantity
        error_loc = errors[0]['loc']
        assert 'items' in error_loc
        assert 1 in error_loc  # Index of failing item
        assert 'quantity' in error_loc

        # Check error message mentions minimum
        error_msg = errors[0]['msg'].lower()
        assert 'minimum' in error_msg or 'least' in error_msg

    def it_validates_optional_list_of_models(self) -> None:
        """Validate optional list of models."""

        class Tag(BaseModel):
            name: str

        class Post(BaseModel):
            title: str
            tags: list[Tag] | None = None

        # With tags
        post = Post(title='Hello', tags=[{'name': 'python'}, {'name': 'valid8r'}])
        assert post.title == 'Hello'
        assert len(post.tags) == 2
        assert post.tags[0].name == 'python'

        # Without tags
        post_no_tags = Post(title='World')
        assert post_no_tags.tags is None


class DescribeDictValueValidation:
    """Test suite for validating dict values with valid8r parsers."""

    def it_validates_dict_values_with_valid8r_parsers(self) -> None:
        """Validate dict values with valid8r parsers (Gherkin scenario 4)."""

        class Config(BaseModel):
            ports: dict[str, int]

            @field_validator('ports', mode='before')
            @classmethod
            def validate_ports(cls, v: Any) -> dict[str, int]:  # noqa: ANN401
                if not isinstance(v, dict):
                    raise TypeError('ports must be a dict')

                # Validate each value in the dict
                validated = {}
                for key, value in v.items():
                    validated[key] = validator_from_parser(parsers.parse_int)(value)
                return validated

        # Valid dict with string values parsed to int
        config = Config(ports={'http': '80', 'https': '443'})
        assert config.ports == {'http': 80, 'https': 443}

    def it_validates_dict_values_and_reports_key_in_error(self) -> None:
        """Validate dict values and report key in validation error."""

        class Config(BaseModel):
            ports: dict[str, int]

            @field_validator('ports', mode='before')
            @classmethod
            def validate_ports(cls, v: Any) -> dict[str, int]:  # noqa: ANN401
                if not isinstance(v, dict):
                    raise TypeError('ports must be a dict')

                validated = {}
                for key, value in v.items():
                    validated[key] = validator_from_parser(parsers.parse_int)(value)
                return validated

        # Invalid value in dict
        with pytest.raises(ValidationError) as exc_info:
            Config(ports={'http': '80', 'https': 'invalid'})

        errors = exc_info.value.errors()
        assert len(errors) == 1

        # Error should mention the value being invalid
        error_msg = errors[0]['msg'].lower()
        assert 'integer' in error_msg or 'invalid' in error_msg

    def it_validates_dict_with_model_values(self) -> None:
        """Validate dict with model values."""

        class ContactInfo(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
                return validator_from_parser(parsers.parse_email)(v)

        class Team(BaseModel):
            contacts: dict[str, ContactInfo]

        # Valid dict with model values
        team = Team(contacts={'alice': {'email': 'alice@example.com'}, 'bob': {'email': 'bob@example.com'}})
        assert len(team.contacts) == 2
        assert team.contacts['alice'].email.local == 'alice'
        assert team.contacts['bob'].email.domain == 'example.com'


class DescribeMakeAfterValidator:
    """Test suite for make_after_validator function."""

    def it_creates_pydantic_after_validator_from_parser(self) -> None:
        """Create Pydantic AfterValidator from valid8r parser."""
        from typing import Annotated

        from pydantic import AfterValidator

        from valid8r.integrations.pydantic import make_after_validator

        email_validator = make_after_validator(parsers.parse_email)

        class User(BaseModel):
            email: Annotated[str, AfterValidator(email_validator)]

        # Valid email
        user = User(email='alice@example.com')
        assert isinstance(user.email, EmailAddress)
        assert user.email.local == 'alice'
        assert user.email.domain == 'example.com'

    def it_converts_failure_to_validation_error(self) -> None:
        """Convert parser Failure to Pydantic ValidationError."""
        from typing import Annotated

        from pydantic import AfterValidator

        from valid8r.integrations.pydantic import make_after_validator

        phone_validator = make_after_validator(parsers.parse_phone)

        class Contact(BaseModel):
            phone: Annotated[str, AfterValidator(phone_validator)]

        # Invalid phone number
        with pytest.raises(ValidationError) as exc_info:
            Contact(phone='invalid')

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert 'phone' in errors[0]['msg'].lower() or 'format' in errors[0]['msg'].lower()

    def it_works_with_chained_validators(self) -> None:
        """Work with chained validators using bind for parser composition."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        # Use WrapValidator to get raw input before Pydantic's type conversion
        # Chain parse_int and minimum using bind
        def age_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            return parsers.parse_int(value).bind(validators.minimum(0))

        age_validator = make_wrap_validator(age_parser)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(age_validator)]

        # Valid value
        data = Data(value='42')
        assert data.value == 42

        # Invalid value (negative)
        with pytest.raises(ValidationError) as exc_info:
            Data(value='-1')

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert 'least' in errors[0]['msg'].lower() or 'minimum' in errors[0]['msg'].lower()

    def it_works_with_optional_fields(self) -> None:
        """Work with optional fields by wrapping parser to handle None."""
        from typing import Annotated

        from pydantic import AfterValidator

        from valid8r.integrations.pydantic import make_after_validator

        # Wrap the parser to handle None values
        def optional_email_parser(value: Any) -> Maybe[EmailAddress | None]:  # noqa: ANN401
            if value is None:
                return Maybe.success(None)
            return parsers.parse_email(value)

        email_validator = make_after_validator(optional_email_parser)

        class User(BaseModel):
            email: Annotated[str | None, AfterValidator(email_validator)] = None

        # Valid email
        user1 = User(email='alice@example.com')
        assert isinstance(user1.email, EmailAddress)

        # None value should pass through
        user2 = User(email=None)
        assert user2.email is None

        # Default None
        user3 = User()
        assert user3.email is None

    def it_mixes_with_field_validator(self) -> None:
        """Mix AfterValidator with field_validator."""
        from typing import Annotated

        from pydantic import AfterValidator

        from valid8r.integrations.pydantic import make_after_validator

        # Use a parser that works with both string and int inputs
        def flexible_int_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            if isinstance(value, int):
                return Maybe.success(value)
            return parsers.parse_int(value)

        int_validator = make_after_validator(flexible_int_parser)

        class User(BaseModel):
            age: Annotated[int, AfterValidator(int_validator)]
            name: str

            @field_validator('name')
            @classmethod
            def validate_name(cls, v: str) -> str:
                if not v.strip():
                    msg = 'Name cannot be empty'
                    raise ValueError(msg)
                return v.strip()

        # Valid data
        user = User(age='25', name='Alice')
        assert user.age == 25
        assert user.name == 'Alice'

        # Invalid age
        with pytest.raises(ValidationError) as exc_info:
            User(age='invalid', name='Bob')
        assert any(err['loc'] == ('age',) for err in exc_info.value.errors())

        # Invalid name
        with pytest.raises(ValidationError) as exc_info:
            User(age='30', name='')
        assert any(err['loc'] == ('name',) for err in exc_info.value.errors())

    def it_preserves_field_path_in_nested_models(self) -> None:
        """Preserve field path in nested model validation errors."""
        from typing import Annotated

        from pydantic import AfterValidator

        from valid8r.integrations.pydantic import make_after_validator

        phone_validator = make_after_validator(parsers.parse_phone)

        class Address(BaseModel):
            phone: Annotated[str, AfterValidator(phone_validator)]

        class User(BaseModel):
            name: str
            address: Address

        # Valid nested data
        user = User(name='Alice', address={'phone': '(206) 234-5678'})
        assert user.name == 'Alice'

        # Invalid nested phone
        with pytest.raises(ValidationError) as exc_info:
            User(name='Bob', address={'phone': 'invalid'})

        errors = exc_info.value.errors()
        assert len(errors) == 1
        error_loc = errors[0]['loc']
        assert 'address' in error_loc
        assert 'phone' in error_loc


class DescribeMakeWrapValidator:
    """Test suite for make_wrap_validator function."""

    def it_creates_pydantic_wrap_validator_from_parser(self) -> None:
        """Create Pydantic WrapValidator from valid8r parser."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        int_validator = make_wrap_validator(parsers.parse_int)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(int_validator)]

        # Valid value
        data = Data(value='42')
        assert data.value == 42
        assert isinstance(data.value, int)

    def it_receives_raw_input_before_pydantic_processing(self) -> None:
        """Receive raw input before Pydantic's type conversion."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        captured_values: list[tuple[Any, str]] = []

        def capturing_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            """Parser that captures the input value and its type."""
            captured_values.append((value, type(value).__name__))
            return parsers.parse_int(value)

        int_validator = make_wrap_validator(capturing_parser)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(int_validator)]

        # Create instance
        Data(value='  42  ')

        # Verify raw string was received (not pre-processed by Pydantic)
        assert len(captured_values) == 1
        assert captured_values[0][1] == 'str'
        assert captured_values[0][0] == '  42  '

    def it_converts_failure_to_validation_error(self) -> None:
        """Convert parser Failure to Pydantic ValidationError."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        int_validator = make_wrap_validator(parsers.parse_int)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(int_validator)]

        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            Data(value='not-a-number')

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert 'integer' in errors[0]['msg'].lower()

    def it_chains_multiple_wrap_validators(self) -> None:
        """Chain multiple WrapValidators together."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        # First validator strips whitespace
        def strip_parser(value: Any) -> Maybe[str]:  # noqa: ANN401
            if isinstance(value, str):
                return parsers.parse_str(value.strip())
            return parsers.parse_str(str(value))

        def parse_str(value: Any) -> Maybe[str]:  # noqa: ANN401
            if value is None or not isinstance(value, str):
                return Maybe.failure('Value must be a string')
            return Maybe.success(value)

        # Second validator parses int
        strip_validator = make_wrap_validator(strip_parser)
        int_validator = make_wrap_validator(parsers.parse_int)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(strip_validator), WrapValidator(int_validator)]

        # Valid value with whitespace
        data = Data(value='  42  ')
        assert data.value == 42

    def it_works_with_chained_parsers_using_bind(self) -> None:
        """Work with chained parsers using bind."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        def age_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            return parsers.parse_int(value).bind(validators.between(0, 120))

        age_validator = make_wrap_validator(age_parser)

        class User(BaseModel):
            age: Annotated[int, WrapValidator(age_validator)]

        # Valid age
        user = User(age='25')
        assert user.age == 25

        # Invalid age (negative)
        with pytest.raises(ValidationError):
            User(age='-1')

        # Invalid age (too high)
        with pytest.raises(ValidationError):
            User(age='150')

    def it_demonstrates_wrap_validator_signature(self) -> None:
        """Demonstrate WrapValidator signature with handler parameter."""
        from typing import Annotated

        from pydantic import WrapValidator

        from valid8r.integrations.pydantic import make_wrap_validator

        # WrapValidators receive (value, handler) parameters
        # make_wrap_validator creates a validator with this signature
        int_validator = make_wrap_validator(parsers.parse_int)

        class Data(BaseModel):
            value: Annotated[int, WrapValidator(int_validator)]

        # Create instance - validator receives raw value before Pydantic's conversion
        data = Data(value='42')
        assert data.value == 42
